#!/bin/bash
pkill -f kismet_cap_linux_wifi > /dev/null
pkill -f kismet > /dev/null
pkill -f KismetUIPlugin.py &> /dev/null
sudo rm *.kismet &> /dev/null
sudo rm *.kismet-journal &> /dev/null
sudo rm *.log &> /dev/null
sudo rm *.csv &> /dev/null
