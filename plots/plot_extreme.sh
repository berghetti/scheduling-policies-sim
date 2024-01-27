#!/bin/bash

#for type in '-short' '-long' '-sld'; do
for type in '-short' '-long'; do
    ./plot_extreme.py $type ../tests/*/extreme/* &
    PID=$!
done

wait $PID
