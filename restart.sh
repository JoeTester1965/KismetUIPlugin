#!/bin/bash

VIRTUAL_ENV_IF_NEEDED=$PWD/venv/bin/activate

#Use a python virtual env if needed
if [ -s $VIRTUAL_ENV_IF_NEEDED ]; then
	source $VIRTUAL_ENV_IF_NEEDED
else
    echo "No local python virtual env at $VIRTUAL_ENV_IF_NEEDED is being used "
fi

nohup pkill -f tshark &> /dev/null
nohup tshark -Q -l -i wlan0mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> probes.csv 2>/dev/null &
nohup pkill -f KismetUIPlugin.py &> /dev/null
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &

# Run this from cron say every hour to stop /tmp filling !!!