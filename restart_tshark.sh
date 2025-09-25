#!/bin/bash
killall tshark
nohup tshark -Q -l -i wlan0mon -Y 'wlan.fc.type==0 and wlan.fc.type_subtype==4 and wlan.ssid != ""' -T fields -e frame.time_epoch -e wlan.ta -e wlan.ra -e wlan.sa -e wlan.da -e frame.len -e wlan_radio.channel -e wlan_radio.signal_dbm -e wlan.ssid -E separator=, >> probes.csv 2>/dev/null &

# Run this from cron say every hour to stop /tmp filling !!!