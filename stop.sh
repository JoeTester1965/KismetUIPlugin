#!/bin/bash

killall -9 kismet
sleep 5
rm *.kismet 2>/dev/null
rm *.kismet-journal 2>/dev/null
pkill -f KismetUIPlugin.py
