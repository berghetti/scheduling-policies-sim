#!/bin/bash

CONF_FILES=(
    "./configs/bimodal_flag_static_config.json"
    "./configs/constant_flag_static_config.json"
)

DESCRIPTIONS=(
    "bimodal_flag"
    "constant_flag"
)

for i in ${!CONF_FILES[@]}; do
    echo "Starting: ${DESCRIPTIONS[$i]}"
    ./start.sh ${CONF_FILES[$i]} ${DESCRIPTIONS[$i]}
done

git add . && git commit -m "new results bimodal_flag and constant flag" && git push && shutdown -P
