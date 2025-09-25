#!/bin/bash

VIRTUAL_ENV_IF_NEEDED=$PWD/venv/bin/activate

#Use a python virtual env if needed
if [ -s $VIRTUAL_ENV_IF_NEEDED ]; then
	source $VIRTUAL_ENV_IF_NEEDED
else
    echo "No local python virtual env at $VIRTUAL_ENV_IF_NEEDED is being used "
fi

CONFIG_FILE="process_real_time_probes.cfg"  

nohup bash ./stop.sh &> /dev/null

nohup python3 process_real_time_probes.py $CONFIG_FILE $CSV_FILE 2>/dev/null &

nohup kismet &> kismet.log & 
nohup python3 KismetUIPlugin.py &>KismetUIPlugin.log &

sleep 1.0s

#tshark must be configured for non root users, use 'sudo dpkg-reconfigure wireshark-common' if needed then 'sudo usermod -aG wireshark myusername' then use monitor interface address as produced by kismet 
#
bash ./restart_tshark.sh
