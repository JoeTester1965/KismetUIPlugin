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
	TIME_INTERVAL_MINTES="5"
else
	TIME_INTERVAL_MINTES=$2
fi

sed "s|$|,0|" probes_0.csv > probes_0_temp.csv
sed "s|$|,1|" probes_1.csv > probes_1_temp.csv

cat probes_0_temp.csv probes_1_temp.csv > probes.csv

nohup python3 probes_latest.py probes.csv $TIME_INTERVAL_MINTES > probe_viewer.log 2>&1

cp -f probes_latest.csv $dir/probes_latest.csv

exit
