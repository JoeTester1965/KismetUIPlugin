#!/bin/bash

./stop.sh
nohup kismet 2>/dev/null &
sleep 5
nohup python KismetUIPlugin.py 2>/dev/null &
