#!/bin/bash

CSV_FILE="probes.csv"
ARCHIVE_CSV_FILE="probes_archive.csv"

nohup pkill -f kismet_cap_linux_wifi &> /dev/null
nohup pkill -f kismet &> /dev/null
nohup pkill -f KismetUIPlugin.py &> /dev/null
nohup pkill -f process_real_time_probes.py &> /dev/null
nohup pkill -f probe_viewer.py &> /dev/null
nohup rm *.kismet &> /dev/null
nohup rm *.kismet-journal &> /dev/null
nohup rm *.log &> /dev/null
nohup rm edge_df.csv &> /dev/null
nohup rm nohup.out &> /dev/null
pkill -f tshark > /dev/null

if [ -f $CSV_FILE ]; then
	nohup mv $CSV_FILE $ARCHIVE_CSV_FILE &> /dev/null
fi
