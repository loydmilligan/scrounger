#!/bin/bash
cd /home/mmariani/scrounger

kill_kanban() {
    pkill -f "server.py" 2>/dev/null
    pkill chromium 2>/dev/null
    echo "Killed kanban processes"
}

case "$1" in
    kill)
        kill_kanban
        exit 0
        ;;
esac

# Kill any existing server
kill_kanban

# Start the server in background
nohup .venv/bin/python scripts/server.py > /tmp/kanban_server.log 2>&1 &
sleep 2

# Start X server and Chromium
sudo /usr/bin/Xorg :0 &
sleep 2
export DISPLAY=:0
chromium --kiosk --incognito --fullscreen http://localhost:8001/kanban.html
