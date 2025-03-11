#!/bin/bash

CSV_FILE="probes.csv"

VIRTUAL_ENV=$PWD/venv/bin/activate

#Use a python virtual env if needed
if [ -s $VIRTUAL_ENV_IF_NEEDED ]; then
        source $VIRTUAL_ENV
else
    echo "No local python virtual env at $VIRTUAL_ENV is being used "
fi

if [[ -z $1 ]]
then
	dir=.
else
	dir=$1
fi

nohup python3 probe_viewer.py $CSV_FILE 2>/dev/null 

cp -f watchlist.csv probes.sqlite3 $dir
cp -f probes.jpg $dir/$(date +%d-%m-%Y-%H-%M)-probes.jpg

exit