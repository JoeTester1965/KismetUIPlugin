#!/bin/bash

ARCHIVE_CSV_FILE="probes_archive.csv"

VIRTUAL_ENV=$PWD/venv/bin/activate

#Use a python virtual env if needed
if [ -s $VIRTUAL_ENV_IF_NEEDED ]; then
        source $VIRTUAL_ENV
else
    echo "No local python virtual env at $VIRTUAL_ENV is being used "
fi

nohup python3 probe_viewer.py $ARCHIVE_CSV_FILE 2>/dev/null 

if [[ ! -z $1 ]] then
    mkdir -p $1/$(date +%d-%m-%Y-%H-%M)
    cp -f watchlist.csv probes.sqlite3 $1
    cp -f probes.jpg $1/$(date +%d-%m-%Y-%H-%M)
fi

exit