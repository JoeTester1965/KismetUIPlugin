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

TIME_INTERVAL="24h"

directory=$dir/$(date -d "yesterday" +%d-%m-%Y)

file=$directory/probes_sorted.csv

nohup python3 probe_viewer_sorted.py $file > probe_viewer.log 2>&1

cp -f probes.jpg $directory
cp -f probes-raw.jpg $directory

exit
