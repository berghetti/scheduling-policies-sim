#!/bin/python3

# example use
# ./plot.py afp/500000 psp/500000 dfcfs/500000
#
import charts
import csv
import sys
import os
import math
import numpy as np
import scipy.stats as ss

#TYPE = 'short'
#TYPE = 'long'
TYPE = 'all'

SV_TIME_SHORT = 1000

# Calcule CDF with definition P(X < x)
# data: array
# return: array with CDF probabilities
def cdf(data):
    values, counts = np.unique(data, return_counts=True)

    size = len(data)
    cdf = []
    s = 0
    for c in counts:
        cdf.append(s/size)
        s += c

    return values, cdf

def process_folder(folder):

    files = os.listdir(folder)
    files = sorted(files)

    task_times = open(os.path.join(folder, files[0]))
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
            latencys.append(latency)

    x, y = cdf(latencys)

    return x, y


def get_next(array):
  return

colors = ['blue', 'green', 'purple', 'marron']
linestyles = ['--', ':', '-.' ]
markers = ['*', 'P', 's', 'p' ]

i = 0
def new_dataset(policy):
  global i

  x, y = process_folder('{}'.format(policy))

  if 'psp' in policy:
    c = 'orange'
    ls = '-'
    m = 'o'
  else:
    c = colors[ i % len(colors) ]
    ls = linestyles[ i % len(linestyles) ]
    m = markers[ i % len(markers) ]
    i += 1

  return {
    'x': x,
    'y': y,
    'style': {
        'label': str(policy.split('/')[-2].split('_')[0]).upper(),
        #'label': str(policy).upper(),
        'color': c,
        'linestyle': ls,
        #'marker': m,
        'linewidth': 2.0,
        #'markersize': 2.0
    },
    'errorbar': 0,
    #'errorbar': {
    #    'x': x,
    #    'y': y,
    #    'yerr': yerr,
    #    #'ecolor': 'black',
    #    'color': c,
    #    'linestyle': ls,
    #    'marker': m,
    #    'elinewidth': 0.3,
    #    'linewidth': 1.0,
    #    'markersize': 4.0
    #},
  }


datasets = []

if __name__ == '__main__':

  for policy in sys.argv[1:]:
     print('Processing: {}'.format(policy))
     datasets.append(new_dataset(policy))

  # edit manually this general settings
  config = {
      'datasets': datasets,
      'xlabel': 'Latência ($u$s)',
      'ylabel': 'CDF',
      #'ylabel': 'CDF $P(X < x)$',

      'font': {
          'font.size':10,
          'axes.labelsize': 10,
          'axes.titlesize': 10,
          'xtick.labelsize': 10,
          'ytick.labelsize': 10,
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
          'xmajor': 1,
          'xminor': 0.5,
          'ymajor': 0.2,
          'yminor': 0.1,
      },

      'legend': {
          'loc': 'best',
      #    'title': 'Overhead (ns)',
          'title_fontsize' : 12,
          'fontsize': 10,
      },

      'title':{
          'label': 'Curtas',
          'loc': 'center'
      },

      'ylim': [0, 1.01],
      'xlim': [0, 20],  # max(overhead) + 10],
      #'save': 'imgs/cfd_shorts_1_100_rate_500k.pdf',
      #'save': 'imgs/{}_{}.png'.format(TYPE, rate),
      'show': 'y'
  }

  if TYPE == 'long':
      config['title']['label'] = 'Longas'.format(TYPE.capitalize())
      #config['set_ticks']['ymajor'] = 500
      #config['set_ticks']['yminor'] = 250
      #config['ylim'] = [0, 3500]


  c = charts.line(config)
