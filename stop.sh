#!/bin/bash

pkill -f kismet
sleep 1
sudo rm *.kismet
pkill -f KismetUIPlugin.py
