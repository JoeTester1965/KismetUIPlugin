#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
CSV_FILE="probes.csv"
ARCHIVE_CSV_FILE="probes_archive.csv"
if [ -f $CSV_FILE ]; then
	nohup cat $CSV_FILE >> $ARCHIVE_CSV_FILE
	nohup rm -f $CSV_FILE > /dev/null
	nohup rm -f $CSV_FILE > /dev/null
fi
pkill -f tshark > /dev/null
pkill -f process_real_time_probes.py > /dev/null
