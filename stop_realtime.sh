#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
CSV_FILE="probes.csv"
nohup rm -f $CSV_FILE &> /dev/null
pkill -f tshark &> /dev/null
pkill -f process_real_time_probes.py &> /dev/null
