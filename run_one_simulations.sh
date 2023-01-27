#!/bin/bash

# Run one simulation

if [ "$#" -ne 2 ]; then
    echo "Usage $0 config.json description"
fi

python3 ./sim/simulation.py $1 $2


FILE=$(tail -n 1 ./results/meta_log | awk -F': ' '{print $1}')
FILE_OUT="${FILE}_$2_out.csv"
python3 analysis.py $FILE $FILE_OUT 0

awk -F, '{print($11 "," $9 "," $12 "," $10 "," $13 "," $14)}' $FILE_OUT | column --separator , -t


