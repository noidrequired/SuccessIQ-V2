#!/bin/bash
# ============================================================================
# SuccessIQ — one-shot teammate setup (file prep only).
#
# Run this once, from inside the SuccessIQ folder you were given:
#   bash setup_successiq.sh
#
# What it does:
#   1. Clears the macOS "unidentified developer" quarantine flag so nothing
#      gets blocked after arriving via OneDrive/zip/Teams.
#   2. Makes the server and launcher executable.
#   3. Creates your own successiq.json from the blank template (never
#      touches it if one already exists — safe to re-run any time).
#
# It does NOT start any background process or install anything persistent —
# no daemons, nothing to uninstall later. Starting the dashboard is a normal,
# repeatable request to your own Cowork/Claude Code assistant: just say
# "launch successiq server" whenever you want to use it. Same thing every
# time, nothing left running quietly that you'd need to remember to stop.
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> SuccessIQ setup starting in: $SCRIPT_DIR"

# --- 1. Clear quarantine flags (harmless if absent) ------------------------
xattr -d com.apple.quarantine "successiq_server.py" 2>/dev/null || true
xattr -d com.apple.quarantine "successiq-dashboard.html" 2>/dev/null || true
xattr -d com.apple.quarantine "Start SuccessIQ Dashboard.command" 2>/dev/null || true
chmod +x "successiq_server.py" "Start SuccessIQ Dashboard.command" 2>/dev/null || true

# --- 2. Confirm Python 3 -----------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install it first (e.g. 'brew install python3' or python.org), then re-run this script."
  exit 1
fi

# --- 3. Create a blank personal database if one doesn't exist already ------
if [ ! -f "successiq.json" ]; then
  if [ -f "successiq-skill/templates/blank_database.json" ]; then
    echo "==> No successiq.json found — creating your own blank database."
    read -p "Your name (for the database owner field): " OWNER_NAME
    cp "successiq-skill/templates/blank_database.json" "successiq.json"
    python3 - "$OWNER_NAME" <<'PYEOF'
import json, sys, datetime
name = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    with open("successiq.json") as f:
        data = json.load(f)
    data["exported"] = datetime.datetime.utcnow().isoformat() + "Z"
    data.setdefault("auditLog", []).insert(0, {
        "id": "1",
        "ts": data["exported"],
        "actor": "System",
        "action": "Database created",
        "details": f"Created for {name}" if name else "Database created",
        "custId": "",
    })
    with open("successiq.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"[warn] could not stamp database: {e}")
PYEOF
    echo "    Created successiq.json for $OWNER_NAME."
  else
    echo "[warn] successiq-skill/templates/blank_database.json not found — skipping database creation. Ask whoever shared this bundle for the full successiq-skill/ folder, or create successiq.json manually."
  fi
else
  echo "==> successiq.json already exists — leaving it untouched."
fi

echo ""
echo "==> Setup complete."
echo "Next: open a Cowork/Claude Code session pointed at this folder and say"
echo "\"launch successiq server\" — it starts the dashboard at http://127.0.0.1:8765."
echo "Bookmark that URL. Run the same request again any time the dashboard isn't open"
echo "(e.g. after a restart) — nothing runs in the background when you're not using it."
