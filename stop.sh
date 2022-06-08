#!/bin/bash

pkill -f kismet
sleep 1
rm *.kismet
pkill -f KismetUIPlugin.py
rm -f nohup.out
