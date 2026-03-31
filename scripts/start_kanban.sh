#!/bin/bash
cd /home/mmariani/scrounger

# Kill any existing server
pkill -f "server.py" 2>/dev/null

# Start the server in background
nohup .venv/bin/python scripts/server.py > /tmp/kanban_server.log 2>&1 &
sleep 2

# Start X with Chromium in fullscreen kiosk mode
exec sudo xinit chromium --kiosk --incognito http://localhost:8001/kanban.html
