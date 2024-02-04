#!/bin/python3

import os
import math
import numpy as np

get_slowdown = False

def interval_confidence( data ):
    Z = 1.96 # nivel de confiança 95%
    avg = sum(data) / len(data)

    sum_ = 0
    for i in range(len(data)):
        sum_ += math.pow( data[i] - avg, 2 )

    desvio = math.sqrt( sum_ / len(data) )
    margin_error = Z * ( desvio / math.sqrt(len(data) ) ) # intervalo de confiança

    avg = round(avg, 4)
    margin_error = round(margin_error, 4)
    return avg, margin_error

def slowdown(folder):

    files = os.listdir(folder)
    sld = []
    for file in files:

        with open(os.path.join(folder, file)) as task_times:
            next(task_times) # skip header

            slowdowns = []
            for line in task_times:
                data = line.split(',')
                latency = int(data[1])
                service_time = int(data[2])

                slowdown = latency / service_time
                slowdowns.append(slowdown)

            sld.append( np.percentile(slowdowns, 99.9) )

    return interval_confidence(sld)

def get_latency(folder, TYPE=None, SV_TIME_SHORT=None):

    if TYPE == None or SV_TIME_SHORT == None:
        exit('Error: TYPE or SV_TIME_SHORT is None')

    files = os.listdir(folder)
    lat = []
    for file in files:

        with open(os.path.join(folder, file)) as task_times:
            next(task_times) # skip header

            latencys = []
            for line in task_times:
                data = line.split(',')
                latency = int(data[1])
                service_time = int(data[2])

                latency /= 1000 #us

                if TYPE == 'short' and service_time == SV_TIME_SHORT:
                    latencys.append(latency)
                elif TYPE == 'long' and service_time != SV_TIME_SHORT:
                    latencys.append(latency)
                elif TYPE == 'all':
                    latencys.append(latency) # all

            if len(latencys) == 0:
                exit('error get latencys')

            lat.append( np.percentile(latencys, 99.9) )

    return interval_confidence(lat)

def load_in_file_name(f):
    return float(f.split('_')[-1])

def process_folder(folder_tests, TYPE, SV_TIME_SHORT):
    x = []
    y = []
    yerr = []

    folders = os.listdir(folder_tests)
    folders = sorted(folders, key=load_in_file_name)

    for folder in folders:
        tr = float(folder) * 100 # Load

        folder = os.path.join(folder_tests, folder)

        print('Reading \'{}\''.format(folder))

        if get_slowdown:
            avg, err = slowdown(folder)
        else:
            avg, err = get_latency(folder, TYPE, SV_TIME_SHORT)

        x.append(tr)
        y.append(avg)
        yerr.append(err)

    print(y)

    return x, y, yerr

