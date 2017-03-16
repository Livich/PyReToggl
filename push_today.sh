#!/bin/bash
dt=$(date +'%d/%m/%Y')
if [ -z "$1" ] || ([ "$1" != "0" ] && [ "$1" != "1" ]);
then
    echo "USAGE:  push_today [simulation]"
    echo "        [simulation] to 1 to simulate time entry pushig process. Set to 0 otherwise."
    exit
fi
python3 ./tw2rt.py -f ${dt}T00:01 -t ${dt}T23:59 -v 4 -S $1
