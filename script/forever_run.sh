#!/bin/sh
# Loop: check if app.py is running, start run.sh if not

while true; do
    if ! pgrep -f "python app.py" > /dev/null; then
        echo "App not running, starting with run.sh..."
        sh /home/admin.local/monitor-controller/script/run.sh
    else
        echo "App is running."
    fi
    sleep 5
done