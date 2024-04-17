#!/bin/bash
nohup pkill -f kismet_cap_linux_wifi &> /dev/null
nohup pkill -f kismet &> /dev/null
nohup pkill -f KismetUIPlugin.py &> /dev/null
nohup sudo rm *.kismet &> /dev/null
nohup sudo rm *.kismet-journal &> /dev/null
nohup sudo rm *.log &> /dev/null
nohup sudo rm edge_df.csv &> /dev/null
nohup sudo rm nohup.out &> /dev/null
