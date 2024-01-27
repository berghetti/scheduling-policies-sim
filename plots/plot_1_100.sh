#!/bin/bash

#for type in '-short' '-long' '-sld'; do
for type in '-short' '-long'; do
    ./plot_1_100.py $type ../tests/*/1_100/* &
    PID=$!
done

wait $PID
