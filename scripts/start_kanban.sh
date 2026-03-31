#!/bin/bash
cd /home/mmariani/scrounger

kill_kanban() {
    pkill -f "server.py" 2>/dev/null
    pkill chromium 2>/dev/null
    pkill openbox 2>/dev/null
    echo "Killed kanban processes"
}

case "$1" in
    kill)
        kill_kanban
        exit 0
        ;;
esac

# Kill any existing
kill_kanban

# Start the server in background
nohup .venv/bin/python scripts/server.py > /tmp/kanban_server.log 2>&1 &
sleep 2

# Start X server
sudo /usr/bin/Xorg :0 &
sleep 2
export DISPLAY=:0

# Start openbox window manager (handles fullscreen properly)
openbox &
sleep 2

# Start chromium in kiosk mode
chromium --kiosk --incognito http://localhost:8001/kanban.html &
sleep 4

# Get screen size and resize chromium window
WINID=$(xdotool search --class chromium | head -1)
if [ -n "$WINID" ]; then
    xdotool windowsize $WINID 100% 100%
    xdotool windowmove $WINID 0 0
fi
