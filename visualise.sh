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

sed "s|$|,0|" probes_0.csv > probes_0_temp.csv
sed "s|$|,1|" probes_1.csv > probes_1_temp.csv

cat probes_0_temp.csv probes_1_temp.csv > probes.csv

nohup python3 probe_viewer.py probes.csv $TIME_INTERVAL > probe_viewer.log 2>&1

mkdir -p $dir/$(date +%d-%m-%Y)
mkdir -p $dir/$(date +%d-%m-%Y)/$(date +%H:%M)

cp -f probes.jpg $dir/$(date +%d-%m-%Y)/$(date +%H:%M)
cp -f probes-raw.jpg $dir/$(date +%d-%m-%Y)/$(date +%H:%M)
cp -f probes_sorted.csv $dir/$(date +%d-%m-%Y)/$(date +%H:%M)

exit
