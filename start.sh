#!/bin/bash
./stop.sh 2>/dev/null
nohup /usr/local/bin/kismet &> kismet.log &
nohup python KismetUIPlugin.py &>KismetUIPlugin.log &
