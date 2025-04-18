#!/bin/bash

CSV_FILE="probes.csv"

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

nohup python3 probe_viewer.py $CSV_FILE $TIME_INTERVAL $ 2>/dev/null 

cp -f watchlist.csv probes.sqlite3 $dir
cp -f probes.jpg $dir/$(date +%d-%m-%Y-%H-%M)-probes.jpg

exit