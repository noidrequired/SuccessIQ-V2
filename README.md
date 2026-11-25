SuccessIQ — Getting Started 

A few minutes of setup. After that, everything else is just asking your Claude assistant.  

Before you start 

You'll need the SuccessIQ bundle you were sent. 

You'll need Claude Cowork installed on your Mac. 

5 mins setup using terminal commands and Claude Cowork 

Step 1 — Get the folder 

Double-click the zip file you were sent. It creates a folder, put it wherever you like (Preferably OneDrive). Remember where it is; you'll point Claude at it in Step 3. 

Step 2 — Connect Desktop Commander to your Claude Cowork.  

This is what lets your Claude start the local server for you. You can connect it via connectors or use the below command line for quickest setup. 
 
Open Terminal (press Command and Space together, type Terminal, press Enter). 

Paste this one line and press Enter: 
 

touch ~/.zshrc 

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash 

export NVM_DIR="$HOME/.nvm" 

[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" 

nvm install --lts 

node -v && npm -v && npx -v 

npx -y @wonderwhy-er/desktop-commander@latest setup 

 

When it finishes, fully close and reopen Claude Desktop. That's the only Terminal step in this entire guide — everything from here on is just chatting with your assistant. 

Step 3 — Set up and launch your dashboard 

Open a new chat in Claude Desktop, pointed at your SuccessIQ folder. Paste this message to your assistant: 
 

“Run setup_successiq.sh in this folder to create my personal SuccessIQ database — ask me for my name if it needs it. Then launch the SuccessIQ server and give me the dashboard URL.” 

Your assistant will set everything up, start the server, and hand you a link. Open it in your browser and bookmark it — that's your dashboard from now on. 

Step 4 — Turn on your daily automatic updates 

This makes your dashboard update itself every day from your email, Slack, and Zoom — no typing required. 

Open the file SWEEP_SCHEDULE_PROMPT_TEMPLATE.md in the same folder (double-click opens it in TextEdit). 

At the top, replace the two placeholders with your folder's location and the time you'd like it to run each day. 

Copy everything below the line and paste it to your assistant as a message. 

Your assistant creates the daily update for you — nothing else to configure. 

Step 5 — Using it every day 

Whenever you want to open your dashboard, just tell your assistant: 

“launch successiq server” 

That's the entire daily routine. If it's already running, your assistant will just confirm that and hand you the link again. 

If something goes wrong 

If this happens... 

Do this 

Your assistant says it can't run commands on your computer 

Make sure you fully restarted Claude Desktop after Step 2 — it only takes effect after a restart. 

The dashboard link doesn't open in your browser 

Tell your assistant “launch successiq server” again. 

You're not sure your daily update is working 

Ask your assistant “show my scheduled tasks” to confirm it's set up and when it last ran. 

You want to start over 

You can re-run the Step 3 message any time — it never overwrites your existing data. 

A couple of things to remember 

Your dashboard only works on your own computer — nobody else can see it. 

Your data file is personal to you — never share it or send it to a teammate. 

Your dashboard remains active unless you shut down your laptop for more than 3-4 days or restart it.  
