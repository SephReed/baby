#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/Projects/baby
sudo -u pi python3 baby.py
cd /
