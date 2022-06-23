#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

pkill -f kismet
sleep 1
rm *.kismet
pkill -f KismetUIPlugin.py
rm -f nohup.out
