#!/bin/bash
nohup pkill -f kismet_cap_linux_wifi &> /dev/null
nohup pkill -f kismet &> /dev/null
nohup pkill -f KismetUIPlugin.py &> /dev/null
nohup rm *.kismet &> /dev/null
nohup rm *.kismet-journal &> /dev/null
nohup rm *.log &> /dev/null
nohup rm edge_df.csv &> /dev/null
nohup rm nohup.out &> /dev/null
