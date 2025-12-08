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

cp -f process_real_time_probes.cfg $dir

nohup python3 probe_viewer.py probes.csv > probe_viewer.log 2>&1

mkdir -p $dir/$(date +%d-%m-%Y)
mkdir -p $dir/$(date +%d-%m-%Y)/$(date +%H-%M)

cp -f probes.jpg $dir/$(date +%d-%m-%Y)/$(date +%H-%M)
cp -f probes-raw.jpg $dir/$(date +%d-%m-%Y)/$(date +%H-%M)
cp -f probes.csv $dir/$(date +%d-%m-%Y)/$(date +%H-%M)
cp -f probes_printable.csv $dir/$(date +%d-%m-%Y)/$(date +%H-%M)

cat probes.csv >> $dir/probes.csv
cat probes.csv >> $dir/$(date +%d-%m-%Y)/probes.csv
cat probes_printable.csv >> $dir/probes_printable.csv
cat probes_printable.csv >> $dir/$(date +%d-%m-%Y)/probes_printable.csv

exit
