#!/bin/bash

./stop.sh 2>/dev/null
nohup kismet 2>/dev/null &
nohup python KismetUIPlugin.py 2>/dev/null &
