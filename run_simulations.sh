#!/bin/bash



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

for i in ${!CONF_FILES[@]}; do
    echo "Starting: ${DESCRIPTIONS[$i]}"
    ./start.sh ${CONF_FILES[$i]} ${DESCRIPTIONS[$i]}
done
