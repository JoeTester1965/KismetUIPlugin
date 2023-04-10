#!/bin/bash

pkill -f kismet
pkill -f KismetUIPlugin.py
nohup kismet 2>/dev/null &
sleep 1
nohup python KismetUIPlugin.py 2>/dev/null &
