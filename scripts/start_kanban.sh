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

# Start X server and Chromium in true fullscreen
sudo /usr/bin/Xorg :0 &
sleep 2
export DISPLAY=:0

# Start chromium and maximize window
chromium --kiosk --incognito http://localhost:8001/kanban.html &
sleep 3

# Wait for window to appear and maximize it
for i in 1 2 3 4 5; do
    sleep 1
    xdotool search --name chromium windowmap 2>/dev/null && break
done

xdotool search --name chromium key F11
xdotool search --name chromium windowfocus
sleep 1
xdotool key F11
