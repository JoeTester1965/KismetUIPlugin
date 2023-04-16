#!/bin/bash
pkill -f kismet &> /dev/null
pkill -f KismetUIPlugin.py &> /dev/null
sudo rm *.kismet &> /dev/null
sudo rm *.kismet-journal &> /dev/null
sudo rm *.csv &> /dev/null
