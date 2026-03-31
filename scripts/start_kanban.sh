#!/bin/bash
cd /home/mmariani/scrounger
.venv/bin/python scripts/server.py &
SERVER_PID=$!
sleep 2
xinit chromium --kiosk --incognito http://localhost:8000/kanban.html -- --screen 0 1920x1080
kill $SERVER_PID 2>/dev/null
