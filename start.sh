#!/bin/bash
nohup bash ./stop.sh &> /dev/null
nohup kismet &> kismet.log &
sleep 1
#nohup kismet_cap_linux_wifi --connect 192.168.1.50:2501 --source wlan0:name=RemoteCollectorExample,channel=1 --user username --password password &> Collector.log &
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &