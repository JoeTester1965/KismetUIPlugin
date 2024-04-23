#!/bin/bash
nohup bash ./stop.sh &> /dev/null
nohup kismet &> kismet.log &
sleep 1
nohup kismet_cap_linux_wifi --connect 127.0.0.1:2501 --source wlan1:name=Scanner1 --user username --password password &> Scanner.log &
nohup kismet_cap_linux_wifi --connect 127.0.0.1:2501 --source wlan2:name=Scanner2, --user username --password password &> Collector.log &
nohup kismet_cap_linux_wifi --connect 127.0.0.1:2501 --source wlan0:name=Collector,channel=1 --user username --password password &> Collector.log &
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &