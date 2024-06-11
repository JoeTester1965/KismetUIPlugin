#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

CSV_FILE="probes.csv"
CONFIG_FILE="process_real_time_probes.cfg"  
nohup ./stop_realtime.sh &> /dev/null
nohup touch $CSV_FILE &> /dev/null
nohup chmod ugo+r $CSV_FILE &> /dev/null
nohup tshark -Q -l -i wlan0mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> $CSV_FILE 2>/dev/null &
nohup tshark -Q -l -i wlan1mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> $CSV_FILE 2>/dev/null &
nohup tshark -Q -l -i wlan2mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> $CSV_FILE 2>/dev/null &
nohup sudo -u pi -H python3 process_real_time_probes.py $CONFIG_FILE $CSV_FILE 2>/dev/null &
nohup sudo -u pi -H python3 probe_viewer.py ./probes_archive.csv &> /dev/null &