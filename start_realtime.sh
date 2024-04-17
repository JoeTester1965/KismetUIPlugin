#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
CSV_FILE="probes.csv"
nohup ./stop_realtime.sh
nohup touch $CSV_FILE &> /dev/null
nohup chmod ugo+r $CSV_FILE &> /dev/null
nohup stdbuf -i0 -o0 -e0 tshark -l -i wlan0 -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, > $CSV_FILE &
nohup sudo -H -u pi python3 ./process_real_time_probes.py process_real_time_probes.cfg $CSV_FILE &> /dev/null &
