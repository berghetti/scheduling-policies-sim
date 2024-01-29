#!/bin/bash

#for type in '-short' '-long' '-sld'; do
for type in '-short' '-long'; do
    #./plot_extreme.py $type ../tests/*/extreme/* &
    ./plot_extreme.py $type '-psp100' ../tests/*/extreme/{afp*q{1,2,4,8},psp*100*}
    ./plot_extreme.py $type '-psp150' ../tests/*/extreme/{afp*q{1,2,4,8},psp*150*}
    ./plot_extreme.py $type '-psp200' ../tests/*/extreme/{afp*q{1,2,4,8},psp*200*}
    ./plot_extreme.py $type '-psp250' ../tests/*/extreme/{afp*q{1,2,4,8},psp*250*}
    PID=$!
done

wait $PID
