#!/bin/bash
cd /home/mmariani/scrounger

# Kill any existing server
pkill -f "server.py" 2>/dev/null

# Start the server in background
nohup .venv/bin/python scripts/server.py > /tmp/kanban_server.log 2>&1 &
sleep 2

# Start X server and Chromium
sudo /usr/bin/Xorg :0 &
sleep 2
export DISPLAY=:0
chromium --kiosk --incognito http://localhost:8001/kanban.html
