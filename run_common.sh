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

set_psp_reserved()
{
    FIELD="\"persephone_total_reserved_cores\""
    sed -i "s/${FIELD}:.*/${FIELD}: $1,/g" $2
}

RUNS=10 # runs same test in multiple threads

MAX_THREADS=$(nproc)

exec_test()
{
    TEST_NAME=$1
    POLICY_NAME=$2
    CONFIG_FILE=$3
    LOAD=$4

    RANDOM_TEST_NAME=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 10)

   python3 ./sim/run_sim.py $CONFIG_FILE $RUNS $RANDOM_TEST_NAME

   DIR_TEST="${TEST_NAME}/${POLICY_NAME}/${LOAD}"

   [ -d ./tests/${DIR_TEST} ] || mkdir -p ./tests/${DIR_TEST}

   #save raw request
   for (( i = 0; i < $RUNS; i++ )); do
       mv ./results/sim_${RANDOM_TEST_NAME}_t${i}/task_times.csv \
           ./tests/${DIR_TEST}/${i}_tasks.csv;
   done
}

[ -d tests ] || mkdir tests

