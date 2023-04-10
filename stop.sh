#!/bin/bash

pkill -f kismet
sleep 1
rm *.kismet 2>/dev/null
rm *.kismet-journal 2>/dev/null
pkill -f KismetUIPlugin.py
