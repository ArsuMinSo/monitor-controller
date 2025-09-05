#!/bin/bash

# kill existing Chromium
pkill chromium
ps aux | grep "/usr/bin/python app.py" | grep -v grep | awk 'NR==1 {print $2}' | xargs -r kill

# relaunch in kiosk mode
DISPLAY=:0 /usr/lib/chromium-browser/chromium-browser --kiosk http://tv.omnika.home:8080/viewer.html &

# start http server if not already running
cd /home/admin.local/http-server
/usr/bin/screen -dmS http-server /usr/bin/python app.py
