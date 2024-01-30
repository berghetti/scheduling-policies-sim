#!/bin/bash

#for type in '-short' '-long' '-sld'; do
for type in '-short' '-long'; do
    ./plot_1_100.py $type 'psp100' ../tests/*/1_100/{afp*q{1,2,4,8},psp*100*} &
    ./plot_1_100.py $type 'psp150' ../tests/*/1_100/{afp*q{1,2,4,8},psp*150*} &
    ./plot_1_100.py $type 'psp200' ../tests/*/1_100/{afp*q{1,2,4,8},psp*200*} &
    ./plot_1_100.py $type 'psp250' ../tests/*/1_100/{afp*q{1,2,4,8},psp*250*} &
    PID=$!
done

wait $PID

#for type in '-short' '-long'; do
#    ./plot_1_100.py $type 'psp100' ../tests/*/high/{afp*q{1,2,4,8},psp*100*} &
#    ./plot_1_100.py $type 'psp150' ../tests/*/high/{afp*q{1,2,4,8},psp*150*} &
#    ./plot_1_100.py $type 'psp200' ../tests/*/high/{afp*q{1,2,4,8},psp*200*} &
#    ./plot_1_100.py $type 'psp250' ../tests/*/high/{afp*q{1,2,4,8},psp*250*} &
#    PID=$!
#done
#
#wait $PID
