#!/bin/bash
cd /home/admin.local/http-server
/usr/bin/screen -dmS http-server /usr/bin/python app.py
