#!/bin/bash

# Run multiples simulations and salve all results in one file RESULTS

CONF_FILES=(
    "./configs/dfcfs.json"
    "./configs/ec_static_config.json"
    "./configs/flag_static_config.json"
    "./configs/ws_static_config.json"
    "./configs/new_policy.json"
)

DESCRIPTIONS=(
    "exp_dfcfs"
    "exp_ec"
    "exp_flag"
    "exp_ws"
    "exp_new_policy"
)

RESULTS="exp_out.csv"

for i in ${!CONF_FILES[@]}; do
    echo "Starting: ${DESCRIPTIONS[$i]}"

    python3 ./sim/simulation.py ${CONF_FILES[$i]} ${DESCRIPTIONS[$i]}

    FILE=$(tail -n 1 ./results/meta_log | awk -F': ' '{print $1}')
    FILE_OUT="${FILE}_$2_out.csv"
    python3 analysis.py $FILE $FILE_OUT 0

    awk -F, '{print($11 "," $9 "," $12 "," $10)}' $FILE_OUT | column --separator , -t

    tail -n 1 ${FILE_OUT} >> ${RESULTS}
done
