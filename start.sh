#!/bin/bash
CSV_FILE="probes.csv"
CONFIG_FILE="process_real_time_probes.cfg"  
nohup bash ./stop.sh &> /dev/null

nohup touch $CSV_FILE &> /dev/null

#tshark must be configured for non root users, use 'sudo dpkg-reconfigure wireshark-common' if needed, monitor interface address as produced by kismet 
nohup tshark -Q -l -i wlan1mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> $CSV_FILE 2>/dev/null &

nohup python3 process_real_time_probes.py $CONFIG_FILE $CSV_FILE 2>/dev/null &

#produce a pretty picture of probes found on last tun
nohup python3 probe_viewer.py ./probes_archive.csv &> /dev/null &

nohup kismet &> kismet.log & 
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &