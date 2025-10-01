#!/bin/bash

VIRTUAL_ENV_DIR=$PWD/venv

#Use a python virtual env if needed
if [ -d $VIRTUAL_ENV_DIR ]; then
        source $VIRTUAL_ENV_DIR/bin/activate
else
    echo "No local python virtual env at $VIRTUAL_ENV_DIR , see README.md on how to create"
    exit
fi

if [[ -z $1 ]]
then
	dir=.
else
	dir=$1
fi

if [[ -z $2 ]]
then
	TIME_INTERVAL="24h"
else
	TIME_INTERVAL=$2
fi

cp -f process_real_time_probes.cfg $dir

nohup python3 probe_viewer.py probes_0.csv $TIME_INTERVAL > probe_viewer_0.log 2>&1

cp -f probes.jpg $dir/$(date +%d-%m-%Y-%H-%M)-probes_0.jpg
cp -f probes-raw.jpg $dir/$(date +%d-%m-%Y-%H-%M)-probes-raw_0.jpg
cp -f probes_printable.csv $dir/$(date +%d-%m-%Y-%H-%M)-probes_printable_0.csv

nohup python3 probe_viewer.py probes_1.csv $TIME_INTERVAL > probe_viewer_0.log 2>&1

cp -f probes.jpg $dir/$(date +%d-%m-%Y-%H-%M)-probes_1.jpg
cp -f probes-raw.jpg $dir/$(date +%d-%m-%Y-%H-%M)-probes-raw_1.jpg
cp -f probes_printable.csv $dir/$(date +%d-%m-%Y-%H-%M)-probes_printable_1.csv

exit
