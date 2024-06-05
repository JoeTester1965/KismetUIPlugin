#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
CSV_FILE="probes.csv"
ARCHIVE_CSV_FILE="probes_archive.csv"
nohup rm -f $ARCHIVE_CSV_FILE > /dev/null
if [ -f $CSV_FILE ]; then
	nohup mv $CSV_FILE $ARCHIVE_CSV_FILE
fi
pkill -f tshark > /dev/null
pkill -f process_real_time_probes.py > /dev/null
