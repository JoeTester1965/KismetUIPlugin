#!/bin/bash

VIRTUAL_ENV_IF_NEEDED=$PWD/venv/bin/activate

#Use a python virtual env if needed
if [ -s $VIRTUAL_ENV_IF_NEEDED ]; then
	source $VIRTUAL_ENV_IF_NEEDED
else
    echo "No local python virtual env at $VIRTUAL_ENV_IF_NEEDED is being used "
fi

CSV_FILE="probes.csv"
ARCHIVE_CSV_FILE="probes_archive.csv"
CONFIG_FILE="process_real_time_probes.cfg"  
nohup bash ./stop.sh &> /dev/null

if [ -s $CSV_FILE ]; then
	nohup mv $CSV_FILE $ARCHIVE_CSV_FILE &> /dev/null
else
    nohup touch $CSV_FILE &> /dev/null
fi
nohup python3 process_real_time_probes.py $CONFIG_FILE $CSV_FILE 2>/dev/null &

nohup kismet &> kismet.log & 
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &

sleep 1.0s

#tshark must be configured for non root users, use 'sudo dpkg-reconfigure wireshark-common' if needed, monitor interface address as produced by kismet 
nohup tshark -Q -l -i wlan0mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> $CSV_FILE 2>/dev/null &
