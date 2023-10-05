#!/bin/bash

# Run one simulation

if [ "$#" -ne 2 ]; then
    echo "Usage $0 config.json description"
fi

#python3 ./sim/simulation.py $1 $2 $3


FILE=$(tail -n 1 ./results/meta_log | awk -F': ' '{print $1}')
FILE_OUT="${FILE}_$2_out.csv"
echo $FILE $FILE_OUT
python3 analysis.py $FILE $FILE_OUT 0

awk -F, '{print($11 "," $9 "," $12 "," $10 "," $13 "," $14 "," $19 "," $20 "," $21)}' $FILE_OUT | column --separator , -t


