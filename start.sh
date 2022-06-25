#!/bin/bash

sudo pkill -f kismet
pkill -f KismetUIPlugin.py
sudo nohup kismet 2>/dev/null &
sleep 1
nohup python KismetUIPlugin.py 2>/dev/null &
