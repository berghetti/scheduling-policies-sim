#!/bin/bash

PIDS=()

./plot_wk2.py '-short' 'fig4a' ../tests/{exp,lognorm}/workload2/{afp*q{1,2,4,8},psp*150*,rss} &
PID+=($!)

./plot_wk2.py '-all' 'fig4b' ../tests/{exp,lognorm}/workload2/{afp*q{1,2,4,8},psp*150*,rss} &
PID+=($!)

./plot_wk2.py '-all' 'fig5b' ../tests/{exp,lognorm}/workload2/{afp*q{1,8},psp*{150,300,450,600}*,rss} &
PID+=($!)

for pid in "${PIDS[@]}"; do
    wait $pid
done
