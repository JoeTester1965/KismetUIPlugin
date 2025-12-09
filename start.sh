#!/bin/bash

nohup bash ./stop.sh 2>/dev/null

nohup ./activate_monitoring.sh 2>/dev/null

nohup ./activate_hopping.sh 2>/dev/null &

sleep 5

VIRTUAL_ENV_IF_NEEDED=$PWD/venv/bin/activate

#Use a python virtual env if needed
if [ -s $VIRTUAL_ENV_IF_NEEDED ]; then
	source $VIRTUAL_ENV_IF_NEEDED
else
    echo "No local python virtual env at $VIRTUAL_ENV_IF_NEEDED is being used "
fi

CONFIG_FILE="process_real_time_probes.cfg"  

nohup python3 process_real_time_probes.py $CONFIG_FILE probes.csv 2>/dev/null &

#nohup kismet &> kismet.log & 
#nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &

#tshark must be configured for non root users, use 'sudo dpkg-reconfigure wireshark-common' if needed then 'sudo usermod -aG wireshark myusername' then use monitor interface address as produced by kismet 
nohup tshark -Q -l -i wlan0mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> probes.csv 2>/dev/null &
