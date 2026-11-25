#!/usr/bin/env python3
"""
Local SuccessIQ Dashboard server.

Serves successiq-dashboard.html on http://127.0.0.1:8765 and exposes
/api/data (GET/POST) backed directly by successiq.json in this same
folder. No browser file picker, no permission prompts — the dashboard
loads and saves automatically against the real file on disk.

Run it by double-clicking "Start SuccessIQ Dashboard.command" next to
this file, or manually with:  python3 successiq_server.py
"""
import glob
import http.server
import json
import os
import socket
import sys
import threading
import time
import webbrowser

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "successiq.json")
HTML_FILE = os.path.join(BASE_DIR, "successiq-dashboard.html")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
SWEEP_REPORTS_DIR = os.path.join(BASE_DIR, "Sweep Reports")
BACKUP_INTERVAL_SECONDS = 15 * 60  # at most one rolling backup every 15 minutes

_last_backup_time = 0.0
_backup_lock = threading.Lock()


def make_backup(force=False):
    """Keep a rolling backup, but at most once every 15 minutes unless
    force=True (used by the explicit "Force backup" button) — the live
    successiq.json is written on every save regardless; this just throttles
    how often we snapshot it to the backups/ folder."""
    global _last_backup_time
    try:
        if not os.path.exists(DATA_FILE):
            return False
        with _backup_lock:
            now = time.time()
            if not force and now - _last_backup_time < BACKUP_INTERVAL_SECONDS:
                return False
            _last_backup_time = now
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUP_DIR, f"successiq_autosave_{stamp}.json")
        with open(DATA_FILE, "rb") as src, open(dest, "wb") as out:
            out.write(src.read())
        # keep only the most recent 50 autosave backups (roughly 12+ hours at this cadence)
        autos = sorted(
            f for f in os.listdir(BACKUP_DIR) if f.startswith("successiq_autosave_")
        )
        for old in autos[:-50]:
            try:
                os.remove(os.path.join(BACKUP_DIR, old))
            except OSError:
                pass
        return True
    except Exception as e:
        print(f"[warn] backup skipped: {e}", file=sys.stderr)
        return False


class Handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                with open(HTML_FILE, "rb") as f:
                    body = f.read()
                self._set_headers(200, "text/html")
                self.wfile.write(body)
            except FileNotFoundError:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"successiq-dashboard.html not found")
        elif self.path == "/api/data":
            try:
                with open(DATA_FILE, "rb") as f:
                    body = f.read()
                self._set_headers(200)
                self.wfile.write(body)
            except FileNotFoundError:
                self._set_headers(404)
                self.wfile.write(b'{"error":"successiq.json not found"}')
        elif self.path == "/api/sweep-report":
            try:
                candidates = glob.glob(os.path.join(SWEEP_REPORTS_DIR, "SWEEP_REPORT_*.md"))
                candidates += glob.glob(os.path.join(BASE_DIR, "SWEEP_REPORT_*.md"))  # back-compat for any left at the root
                if not candidates:
                    self._set_headers(404)
                    self.wfile.write(b'{"error":"no sweep report found"}')
                    return
                latest = max(candidates, key=os.path.getmtime)
                with open(latest, "r", encoding="utf-8") as f:
                    content = f.read()
                payload = {
                    "filename": os.path.basename(latest),
                    "mtime": os.path.getmtime(latest),
                    "content": content,
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(payload).encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == "/api/data":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                data = json.loads(raw)  # validate it's real JSON before writing
                make_backup()
                tmp_path = DATA_FILE + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, DATA_FILE)
                self._set_headers(200)
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
        elif self.path == "/api/backup":
            try:
                did = make_backup(force=True)
                self._set_headers(200)
                self.wfile.write(json.dumps({"ok": True, "backed_up": did}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # keep the terminal window quiet


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    open_browser = "--no-browser" not in sys.argv
    url = f"http://127.0.0.1:{PORT}/"
    if port_in_use(PORT):
        print(f"SuccessIQ server already running at {url}")
        if open_browser:
            webbrowser.open(url)
        return
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    print(f"SuccessIQ Dashboard running at {url}")
    print("Keep this window open while you use the dashboard. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
