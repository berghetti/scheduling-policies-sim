#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage $0 config.json description"
fi

python3 ./sim/simulation.py $1 $2


FILE=$(tail -n 1 ./results/meta_log | awk -F': ' '{print $1}')
python3 analysis.py $FILE "${FILE}_${$2}_out.csv" 0
