#!/bin/bash
./stop.sh 2>/dev/null
nohup /usr/local/bin/kismet &> kismet.log &
nohup /usr/bin/kismet &> kismet.log &
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &
