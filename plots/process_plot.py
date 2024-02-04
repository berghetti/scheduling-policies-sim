#!/bin/python3

# example use
# ./plot.py afp psp dfcfs
#
# to each policy this script access '../tests' folder process results and
# plot chart

import charts
import locale
import csv
import sys
import os
import math
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

TYPE = 'short'
#TYPE = 'long'
#TYPE = 'all'

get_slowdown = False

SV_TIME_SHORT = 1000

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

def get_latency(folder):

    files = os.listdir(folder)
    lat = []
    sld = []
    for file in files:

        task_times = open(os.path.join(folder, file))
        next(task_times) # skip csv header

        slowdowns = []
        latencys = []
        for line in task_times:
            data = line.split(',')
            latency = int(data[1])
            service_time = int(data[2])
            slowdown = latency / service_time

            latency /= 1000 #us

            slowdowns.append(slowdown)

            if TYPE == 'short' and service_time == SV_TIME_SHORT:
                latencys.append(latency)
            elif TYPE == 'long' and service_time != SV_TIME_SHORT:
                latencys.append(latency)
            elif TYPE == 'all':
                latencys.append(latency) # all

        if len(latencys) == 0:
            print('error get latencys')
            exit(1)


        sld.append( np.percentile(slowdowns, 99.9) )
        lat.append( np.percentile(latencys, 99.9) )
        #lat.append( np.percentile(latencys, 50.0) )

        task_times.close()

    if get_slowdown:
        return interval_confidence(sld)

    return interval_confidence(lat)

def load_in_file_name(f):
    return float(f.split('_')[-1])

def process_folder(folder_tests):
    x = []
    y = []
    yerr = []


    folders = os.listdir(folder_tests)
    folders = sorted(folders, key=load_in_file_name)

    for folder in folders:
        #tr = int(folder) / 1000000 #RPS
        tr = float(folder) * 100 # Load

        folder = os.path.join(folder_tests, folder)

        print('Reading \'{}\''.format(folder))

        avg, err = get_latency(folder)

        x.append(tr)
        y.append(avg)
        yerr.append(err)

    print(y)

    return x, y, yerr

colors = ['red', 'green', 'darkviolet']
markers = [ 'o', 's', 'P' ]
linestyles = ['-', ':', '--', '-.' ]

afp_c = ['blue', 'green', 'pink', 'violet', 'cyan']
psp_c = ['orange', 'gold', 'yellow', 'green']


FILE='points.plt'

def process_policy(policy):
  policy = policy.rstrip('/')
  print('Policy: {}'.format(policy))

  name = str(policy.split('/')[-1])
  dist = str(policy.split('/')[2]).capitalize()

  x, y, yerr = process_folder(policy)

  line = '{}_{}:'.format(dist, name)
  line +=','.join(str(i) for i in x)
  line += ':'
  line +=','.join(str(i) for i in y)
  line += ':'
  line +=','.join(str(i) for i in yerr)
  line += ':\n'

  with open(FILE, 'a') as f:
      f.write(line)


if __name__ == '__main__':


  if "-long" in sys.argv:
      sys.argv.remove("-long")
      TYPE = "long"

  if "-short" in sys.argv:
      sys.argv.remove("-short")
      TYPE = "short"

  if "-all" in sys.argv:
      sys.argv.remove("-all")
      TYPE = "all"

  if "-sld" in sys.argv:
      sys.argv.remove("-sld")
      get_slowdown = True
      TYPE = "all"

  for policy in sys.argv[1:]:
    process_policy(policy)


