#!/bin/python3

# example use
#./plot_cfcfs_overhead.py ../tests/exp/cfcfs_overhead

import charts
import csv
import sys
import os
import math
import numpy as np

#TYPE = 'short'
#TYPE = 'long'
TYPE = 'all'

SV_TIME_SHORT = 1000

def rate_name(name):
    return int(name)

SLO = 100

# return max troughput by this policy to a SLO 100x service time
def get_max_troughput(folder):

    rates = os.listdir(folder)
    rates = sorted(rates, key=rate_name)

    lat = []
    prev_rate = 0
    for rate in rates:
        files = os.listdir(os.path.join(folder, rate))

        for file in files:
            task_times = open(os.path.join(folder, rate, file))
            #print(task_times)
            next(task_times) # skip csv header

            latencys = []
            for line in task_times:
                data = line.split(',')
                latency = int(data[1]) / 1000 #us
                service_time = int(data[2])

                if TYPE == 'short' and service_time == SV_TIME_SHORT:
                    latencys.append(latency)
                elif TYPE == 'long' and service_time != SV_TIME_SHORT:
                    latencys.append(latency)
                elif TYPE == 'all':
                    latencys.append(latency) # all

            t = np.percentile(latencys, 99.9)
            if t >= (SV_TIME_SHORT / 1000 * SLO):
                print(t, prev_rate)
                return int(prev_rate)

        prev_rate = rate

    #return max rate
    return int(rates[-1])

def rps_in_file_name(f):
    #print(f)
    return int(f.split('_')[-1])

def process_folder(folder_tests):
    x = []
    y = []
    yerr = []

    folders = os.listdir(folder_tests)
    folders = sorted(folders, key=rps_in_file_name)

    for folder in folders:
        overhead = int(folder.split('_')[1])

        folder = os.path.join(folder_tests, folder)

        print('Reading \'{}\''.format(folder))

        tr = get_max_troughput(folder) / 1000000

        x.append(overhead)
        y.append(tr)

    print(y)

    return x, y, 0

def get_next(array):
  return

def new_dataset(policy):
  global i

  x, y, yerr = process_folder(policy)

  c = 'blue'
  ls = '-'
  m = 'o'

  return {
    'x': x,
    'y': y,
    'style': {
        'label': str(policy).upper(),
        'color': c,
        'linestyle': ls,
        'marker': m,
        'linewidth': 2.0,
        'markersize': 5.0
    },
    'errorbar': {
        'x': x,
        'y': y,
        'yerr': yerr,
        #'ecolor': 'black',
        'color': c,
        'linestyle': ls,
        'marker': m,
        'elinewidth': 0.3,
        'linewidth': 1.0,
        'markersize': 4.0
    },
  }


datasets = []

if __name__ == '__main__':

  for policy in sys.argv[1:]:
     datasets.append(new_dataset(policy))

  # edit manually this general settings
  config = {
      'datasets': datasets,
      'xlabel': 'Sobrecarga (ns)',
      'ylabel': 'Vazão (MRPS)',
      #'ylabel': 'Latency 99.9% (us)',

      'font': {
          'font.size':15,
          'axes.labelsize': 15,
          'axes.titlesize': 15,
          'xtick.labelsize': 15,
          'ytick.labelsize': 15,
      },

      'grid': {
          'visible' : True,
          'which': 'major',
          'style' : {
              'color': '#ccc',
              'linestyle': '-',
              'linewidth': 0.2
           },
      },

      'set_ticks': {
          'xmajor': 100,
          'xminor': 50,
          'ymajor': 2,
          'yminor': 1,
      },

      'legend': {
      #    'loc': 'best',
      ##    'title': 'Overhead (ns)',
      #    'title_fontsize' : 12,
      #    'fontsize': 10,
      },

      #'title':{
      #    #'label': '{} requests'.format(TYPE).capitalize(),
      #    'label': 'Curtas',
      #    'loc': 'center'
      #},

      #'ylim': [-1, 16],
      'xlim': [-10, 1010],  # max(overhead) + 10],
      #'save': 'imgs/{}.pdf'.format(TYPE),
      'save': 'imgs/cfcfs_overhead.pdf',
      #'save': 'imgs/{}.png'.format(TYPE),
      #'show': 'y'
  }

  #if TYPE == 'long' or TYPE == 'all':
  #    #config['title']['label'] = '{} requests'.format(TYPE).capitalize()
  #    config['title']['label'] = 'Longas'

  #    if TYPE == 'all':
  #      config['title']['label'] = 'Geral'


      #config['set_ticks']['ymajor'] = 500
      #config['set_ticks']['yminor'] = 250
      #config['ylim'] = [0, 3500]
      #config['ylim'] = [0, 500]
      #config['set_ticks']['ymajor'] = 50
      #config['set_ticks']['yminor'] = 25


  c = charts.line(config)
