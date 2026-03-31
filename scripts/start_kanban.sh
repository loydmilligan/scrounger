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

# Start X server
sudo /usr/bin/Xorg :0 &
sleep 2
export DISPLAY=:0

# Get screen resolution
SCREEN_SIZE=$(xdotool getdisplaygeometry)
SCREEN_W=$(echo $SCREEN_SIZE | cut -d' ' -f1)
SCREEN_H=$(echo $SCREEN_SIZE | cut -d' ' -f2)

# Start chromium
chromium --kiosk --incognito http://localhost:8001/kanban.html &
sleep 4

# Find and resize Chromium window to full screen
WINID=$(xdotool search --name chromium | head -1)
if [ -n "$WINID" ]; then
    xdotool windowsize $WINID $SCREEN_W $SCREEN_H
    xdotool windowmove $WINID 0 0
    xdotool windowfocus $WINID
    xdotool key F11
fi
