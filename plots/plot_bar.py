#!/bin/python3

import charts
import csv
import sys
import os
import math
import numpy as np

#group1 = {
#     'name': '1',
#     'bars': [
#      {
#        'y': 50,
#        'group_config': {
#            'label': 'Curtas',
#            'color': 'b'
#        }
#      },
#      {
#        'y': 60,
#        'group_config': {
#            'label': 'Longas',
#            'color': 'darkblue'
#          }
#       },
#     ]
#}
#
#group2 = {
#     'name': '1',
#     'bars': [
#      {
#        'y': 70,
#        'group_config': {
#            #'label': 'Curtas',
#            'color': 'b'
#        }
#      },
#      {
#        'y': 90,
#        'group_config': {
#            #'label': 'Longas',
#            'color': 'darkblue'
#          }
#       },
#     ]
#}

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

SV_TIME_SHORT = 1000
def get_latency(TYPE, folder):

    files = os.listdir(folder)
    lat = []
    for file in files:

        task_times = open(os.path.join(folder, file))
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

        if len(latencys) == 0:
            print('error get latencys')
            exit(1)

        lat.append( np.percentile(latencys, 99.9) )

    return interval_confidence(lat)

workload = ''
def new_dataset(policy):
  global i, workload, SV_TIME_SHORT

  policy = policy.rstrip('\/')

  if 'extreme' in policy:
      SV_TIME_SHORT = 500

  workload = policy.split('/')[3]

  quantum = str(policy.split('/')[-1].split('_')[-1])[1:]
  print(quantum)
  short_lat, short_err = get_latency('short', policy)
  long_lat, long_err = get_latency('long', policy)

  return {
     'name': quantum,
     'bars': [
      {
        'y': short_lat,
        'group_config': {
            'label': 'Curtas',
            'color': '#CCEBCB',
            'edgecolor': 'black',
            'yerr': short_err,
            'alpha': 0.70
        }
      },
      {
        'y': long_lat,
        'group_config': {
            'label': 'Longas',
            'color': 'blue',
            'edgecolor': 'black',
            'yerr': long_err,
            'alpha': 0.70,
            'capsize': 3
          }
       },
     ]
  }


#datasets = [group1, group2]
datasets = []
if __name__ == '__main__':

  for policy in sys.argv[1:]:
     print(policy)
     datasets.append(new_dataset(policy))

  #remove duplicate labels
  for d in datasets[1:]:
      d['bars'][0]['group_config']['label'] = ''
      d['bars'][1]['group_config']['label'] = ''


  # edit manually this general settings
  config = {
      'datasets': datasets,
      'xlabel': '$\it{Quantum}\ (\mu$s)',
      #'ylabel': 'Latency 99.9% (us)',
      'ylabel': 'Latência de Cauda ($\mu$s)',

      'font': {
          'font.size':20,
          'axes.labelsize': 20,
          'axes.titlesize': 20,
          'xtick.labelsize': 20,
          'ytick.labelsize': 20,
      },

      'grid': {
          'visible' : True,
          'which': 'both',
          'style' : {
              'axis': 'y',
              'color': '#ccc',
              'linestyle': '-',
              'linewidth': 0.2
           },
      },

      'set_ticks': {
          'xmajor': False,
          'xminor': False,
          'ymajor': 100,
          'yminor': 50,
      },


      'legend': {
          #'loc': 'lower left',
          'loc': 'best',
      #    'title': 'Overhead (ns)',
          'title_fontsize' : 12,
           #'bbox_to_anchor': (0, 1.02, 1.0, 0.2),
          'fontsize': 15,
          'ncol': 2,
          #'mode': 'expand',
          'frameon': False, # remove legend background
      },

      'set_axisbelow': 'true',

      #'title':{
      #    #'label': '{} requests'.format(TYPE).capitalize(),
      #    'label': 'Curtas',
      #    'loc': 'center'
      #},

      # chart bar only
      'bar_w' : { 'bar_width': 0.35 },
      #'bar_xticks': list(range(len(datasets))), # tick idx
      'bar_xticks': [0,1,2,3,4], # tick idx
      'bar_xticklabels': [x['name'] for x in datasets], # tick name
      #'bar_yticks_major': list(range(0, 800, 100)),
      #'bar_yticks_minor': list(range(0, 800, 50)),

      'ylim': [0, 800],
      'save': 'imgs/{}_{}.pdf'.format('quantum', workload),
      'show': 'n'
  }

  if '1_100' in workload:
    config['ylim'] = [0,160]
    config['set_ticks']['ymajor'] = 20
    config['set_ticks']['yminor'] = 10

  #print(config['bar_xticklabels'])
  #print(config['datasets'])

  c = charts.bar(config)
