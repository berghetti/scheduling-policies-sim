#!/bin/bash

source ./run_common.sh

LOAD_NAME="workload2"

run_afp()
{
  CONF="./configs/afp.json"

  OVERHEAD=580

  set_1_100_load $CONF
  set_preempt_overhead $OVERHEAD
  set_afp_rr false
  set_afp_startvation_limit 1000

  for dist in 'exp' 'lognorm'; do
      set_arrival_dist $dist $CONF

      for q in {1000,2000,4000,8000}; do
        set_quantum $q

        for load in {0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9}; do
          set_avg_system_load $load $CONF
          exec_test "${dist}/${LOAD_NAME}" "afp_ov${OVERHEAD}_q$((q/1000))" $CONF $load  &
          sleep 10

          while [ $(ps aux | grep "python3 ./sim/run_sim.py" | grep -v "grep" | wc -l) -ge $(( MAX_THREADS - RUNS )) ]; do
            wait -n # wait lest one process return
          done
        done


      done

  done
}

run_rss()
{
  CONF="./configs/rss.json"

  set_1_100_load $CONF

  for dist in 'exp' 'lognorm'; do
      set_arrival_dist $dist $CONF

      for load in {0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9}; do
        set_avg_system_load $load $CONF
        exec_test "${dist}/${LOAD_NAME}" "rss" $CONF $load &
        sleep 10

        while [ $(ps aux | grep "python3 ./sim/run_sim.py" | grep -v "grep" | wc -l) -ge $(( MAX_THREADS - RUNS )) ]; do
          wait -n # wait lest one process return
        done
      done

  done
}

run_psp()
{
  CONF="./configs/psp.json"
  RESERVED=2

  set_1_100_load $CONF
  set_psp_reserved $RESERVED $CONF

  for dist in 'exp' 'lognorm'; do
      set_arrival_dist $dist $CONF

      for ov in {150,300,450,600}; do
          set_psp_overhead $ov $CONF

          for load in {0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9}; do
             set_avg_system_load $load $CONF
             exec_test "${dist}/${LOAD_NAME}" "psp_ov${ov}_res${RESERVED}" $CONF $load &
             sleep 10

             while [ $(ps aux | grep "python3 ./sim/run_sim.py" | grep -v "grep" | wc -l) -ge $(( MAX_THREADS - RUNS )) ]; do
               wait -n # wait lest one process return
             done
          done

      done

  done
}

run_afp
run_rss
run_psp

