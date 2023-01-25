#!/bin/bash

CONF_FILES=(
    "./configs/constant_dfcfs.json"
    "./configs/constant_ec_static_config.json"
    "./configs/constant_flag_static_config.json"
    "./configs/constant_new_policy.json"
    "./configs/constant_ws_static_config.json"
)

DESCRIPTIONS=(
    "constant_dfcfs"
    "constant_ec"
    "constant_flag"
    "constant_new_policy"
    "constant_ws"
)

for i in ${!CONF_FILES[@]}; do
    echo "Starting: ${DESCRIPTIONS[$i]}"
    ./start.sh ${CONF_FILES[$i]} ${DESCRIPTIONS[$i]}
done
