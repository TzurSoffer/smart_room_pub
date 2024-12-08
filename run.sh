#!/bin/bash

echo "Starting Mosquitto..."
mosquitto -c /etc/mosquitto/mosquitto.conf -d

echo "Starting roomManager..."
cd src/roomManager || exit
screen -wipe
screen -dmS manager python roomManager.py

echo "Starting client..."
cd .. || exit
screen -dmS core bash -c 'while true; do python core.py || echo "core crashed, restarting..."; sleep 2; done'

echo "Starting clientLoader and serverLoader..."
cd modules || exit
screen -dmS clientLoader python clientLoader.py
screen -dmS serverLoader python serverLoader.py

echo "Starting GUI..."
cd ../GUI || exit
screen -dmS GUI python main.py

echo "Listing all screens..."
screen -ls

tail -f /dev/null
