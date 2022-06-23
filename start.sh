#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

pkill -f kismet
pkill -f KismetUIPlugin.py
nohup kismet 2>/dev/null &
sleep 1
sudo -H -u pi nohup python KismetUIPlugin.py 2>/dev/null &
