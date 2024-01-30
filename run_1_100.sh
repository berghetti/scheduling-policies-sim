#!/bin/bash


set_arrival_dist()
{
    FIELD="\"regular_arrivals\""
    sed -i "s/${FIELD}:.*/${FIELD}: \"$1\",/g" $2
}

set_afp_startvation_limit()
{
    FIELD="\"AFP_STARVATION_COUNTER_THRESHOLD\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" configs/afp.json
}

set_afpii()
{
    FIELD="\"afp_unconditional_interrupt\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" configs/afp.json
}

set_quantum()
{
    FIELD="\"PREEMPTION_QUANTUM\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" configs/afp.json
}

set_preempt_overhead()
{
    FIELD="\"PREEMPTION_OVERHEAD\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" configs/afp.json
}

set_afp_rr()
{
    FIELD="\"afp_rr\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" ./configs/afp.json
}

set_exponential_st()
{
    FIELD="\"bimodal_service_time\""
    sed -i "s/${FIELD}:.*/${FIELD}: false,/g" $1
}

set_long_request()
{
    FIELD="\"LONG_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" $2
}

set_bimodal()
{
    FIELD="\"bimodal_service_time\""
    sed -i "s/${FIELD}:.*/${FIELD}: true,/g" $1

    #FIELD="\"AVERAGE_SERVICE_TIME\""
    #sed -i "s/${FIELD}:.*/${FIELD}: 1000,/g" $1
}

set_psp_overhead()
{
    FIELD="\"PERSEPHONE_OVERHEAD\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" $2
}


set_avg_system_load()
{
    FIELD="\"avg_system_load\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" $2
}

#PSP extreme load
set_extreme_load()
{
    set_bimodal $1
    FIELD="\"SHORT_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: 500,/g" $1

    FIELD="\"LONG_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: 500000,/g" $1

    FIELD="\"SHORT_REQUEST_RATE\""
    sed -i "s/${FIELD}:.*/${FIELD}: 995,/g" $1
}

set_1_100_load()
{
    set_bimodal $1
    FIELD="\"SHORT_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: 1000,/g" $1

    FIELD="\"LONG_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: 100000,/g" $1

    FIELD="\"SHORT_REQUEST_RATE\""
    sed -i "s/${FIELD}:.*/${FIELD}: 990,/g" $1
}

set_5_100_load()
{
    set_bimodal $1
    FIELD="\"SHORT_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: 5000,/g" $1

    FIELD="\"LONG_REQUEST_SERVICE_TIME\""
    sed -i "s/${FIELD}:.*/${FIELD}: 100000,/g" $1

    FIELD="\"SHORT_REQUEST_RATE\""
    sed -i "s/${FIELD}:.*/${FIELD}: 990,/g" $1
}

set_psp_reserved()
{
    FIELD="\"persephone_total_reserved_cores\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" $2
}

set_worker_cores()
{
    COUNT=$1
    FIELD="\"worker_cores_count\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" $2

    #set one more to dispatching and timer core
    FIELD="\"num_queues\""
    sed -i "s/${FIELD}:.*/${FIELD}: $((COUNT + 1)),/g" $2

    FIELD="\"num_threads\""
    sed -i "s/${FIELD}:.*/${FIELD}: $((COUNT + 1)),/g" $2

    vals=($(seq 0 $COUNT))
    MAPS=$(printf '%s\n' ${vals[@]} | jq -R . | jq -s .)

    #echo $MAPS
    FIELD="\"mapping\""
    #sed -i "s/${FIELD}:.*/${FIELD}: ${MAPS},/g" $2
}
RUNS=10 # runs same test in multiple threads

MAX_THREADS=140
counter=0

exec_test()
{
    TEST_NAME=$1
    POLICY_NAME=$2
    CONFIG_FILE=$3
    LOAD=$4 # percent from max possible

    RANDOM_TEST_NAME=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 10)
    echo $RANDOM_TEST_NAME

   python3 ./sim/run_sim.py $CONFIG_FILE $RUNS $RANDOM_TEST_NAME

   DIR_TEST="${TEST_NAME}/${POLICY_NAME}/${LOAD}"

   [ -d ./tests/${DIR_TEST} ] || mkdir -p ./tests/${DIR_TEST}

   #save raw request
   for (( i = 0; i < $RUNS; i++ )); do
       mv ./results/sim_${RANDOM_TEST_NAME}_t${i}/task_times.csv \
           ./tests/${DIR_TEST}/${i}_tasks.csv;
   done

   ((counter--))
}

[ -d tests ] || mkdir tests

LOAD_NAME="1_100"


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

      for q in {1000,2000,4000,8000,16000}; do
        set_quantum $q

        for load in {0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9}; do
          set_avg_system_load $load $CONF
          exec_test "${dist}/${LOAD_NAME}" "afp_ov${OVERHEAD}_q$((q/1000))" $CONF $load  &
          sleep 10

          ((counter++))
          if [ $counter -ge $MAX_THREADS ]; then
            while [ $conter -ge $MAX_THREADS - $RUNS ]; do
              wait -n # wait lest one process return
            done
          fi
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
        PID=$!
        sleep 10
      done
      wait $PID

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

             ((counter++))
              if [ $counter -ge $MAX_THREADS ]; then
                while [ $conter -ge $MAX_THREADS - $RUNS ]; do
                  wait -n # wait lest one process return
                done
              fi
           done

      done

  done
}

run_afp
#run_rss
run_psp

