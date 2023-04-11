#!/bin/bash

killall -9 kismet 2>/dev/null 
sudo rm *.kismet 2>/dev/null 
sudo rm *.kismet-journal 2>/dev/null
pkill -f KismetUIPlugin.py 2>/dev/null 
