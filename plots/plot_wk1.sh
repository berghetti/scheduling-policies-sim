#!/bin/bash

PIDS=()

./plot_wk1.py '-short' 'fig3a' ../tests/{exp,lognorm}/workload1/{afp*q{1,2,4,8},psp*150*,rss} &
PID+=($!)

./plot_wk1.py '-all' 'fig3b' ../tests/{exp,lognorm}/workload1/{afp*q{1,2,4,8},psp*150*,rss} &
PID+=($!)

./plot_wk1.py '-all' 'fig5a' ../tests/{exp,lognorm}/workload1/{afp*q{1,8},psp*{150,300,450,600}*,rss} &
PID+=($!)

for pid in "${PIDS[@]}"; do
    wait $pid
done
