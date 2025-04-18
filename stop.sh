#!/bin/bash

nohup pkill -f kismet_cap_linux_wifi &> /dev/null
nohup pkill -f kismet &> /dev/null
nohup pkill -f KismetUIPlugin.py &> /dev/null
nohup pkill -f process_real_time_probes.py &> /dev/null
nohup pkill -f probe_viewer.py &> /dev/null
nohup rm edge_df.csv &> /dev/null
nohup rm nohup.out &> /dev/null
nohup pkill -f tshark &> /dev/null
