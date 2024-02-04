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
        task_times.close()

        sld.append( np.percentile(slowdowns, 99.9) )
        lat.append( np.percentile(latencys, 99.9) )

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

afp_i = psp_i = 0
workload = dist = None
def new_dataset(policy):
  global dist, workload
  global afp_i, psp_i

  policy = policy.rstrip('/')
  print('Policy: {}'.format(policy))

  #policy_name = str(policy.split('/')[-1].split('_')[0]).upper()
  policy_name = str(policy.split('/')[-1])
  dist = str(policy.split('/')[2]).capitalize()
  workload = str(policy.split('/')[3]).capitalize()


  if 'psp' in policy:
    c = 'orange'
    m = 'o'
    ls = '-'
    ov = policy_name.split('_')[1].strip('ov')
    print(ov)
    res = policy_name.split('_')[2].strip('res')
    match int(ov):
        case 150:
            c = 'orange'
        case 300:
            c = 'green'
        case 450:
            c = 'purple'
        case 600:
            c = 'pink'
    policy_name = 'PSP-{}'.format(ov)
    #policy_name = 'PSP-{}-{}'.format(ov, res)
    #c = psp_c[psp_i % len(psp_c)]
    #psp_i += 1
  elif 'rss' in policy:
    c = 'red'
    m = 'x'
    ls = '-.'
    if TYPE == 'short':
        policy_name = ''
  elif 'afp' in policy:
    ls = '--'
    m = 's'
    c = 'blue'
    #ov = policy_name.split('_')[1].strip('ov')
    q = policy_name.split('_')[2].strip('q')
    match int(q):
        case 1:
            c = 'blue'
        case 2:
            c = 'green'
        case 4:
            c = 'purple'
        case 8:
            c = 'black'
    policy_name = 'AFP-{}'.format(q)
    #c = afp_c[afp_i]
    #afp_i = (afp_i + 1) % len(afp_c)

  x, y, yerr = process_folder(policy)

  print(policy_name, dist)

  return {
    'x': x,
    'y': y,
    'style': {
        #'label': '{} - {}'.format(policy_name, dist),
        'label': '{}'.format(policy_name).upper(),
        'color': c,
        'linestyle': ls,
        'marker': m,
        'linewidth': 1.0,
        'markersize': 4,
        #'markerfacecolor': mc,
        #'markeredgecolor': mc
    },
    'errorbar': {
        'x': x,
        'y': y,
        'yerr': yerr,
        'ecolor': 'black',
        'color': c,
        'linestyle': ls,
        'marker': m,
        'elinewidth': 1,
        #'barsabove': True,
        'linewidth': 1.0,
        'markersize': 4,
        'capsize': 3, # upper and bottom in error bar
        #'markerfacecolor': mc,
        #'markeredgecolor': mc
    },
  }

datasets = []

# return dict with each key a array de datasets
# each key is a arrival dist
def multdatasets_create(policys):
    last_dist = None
    rows = []
    datasets = []

    d = {}

    for i, policy in enumerate(policys):
        dist = str(policy.split('/')[2])

        match dist:
            case 'exp':
                dist = 'Exponencial'
            case 'lognorm':
                dist = 'Lognormal'

        if dist not in d:
            d[dist] = []

        d[dist].append(new_dataset(policy))

    #print(d)
    return d

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

  name = sys.argv[1]
  del(sys.argv[1])

  rows = multdatasets_create(sys.argv[1:])
  print('total datasets {}'.format(len(rows)))


  #for policy in sys.argv[1:]:
  #   datasets.append(new_dataset(policy))

  # edit manually this general settings
  config = {
      #'datasets': datasets,
      'mult_datasets': rows,
      'xlabel': 'Utilização (%)',
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
          'which': 'major',
          'style' : {
              'color': '#ccc',
              'linestyle': '-',
              'linewidth': 0.2
           },
      },

      'set_ticks': {
          'xmajor': 10,
          'xminor': 0,
          'ymajor': 20,
          'yminor': 10,
      },

      'legend': {
          'loc': 'upper center',
          #'bbox_to_anchor': (0.5, 1.3),
          'bbox_to_anchor': (0.5, 1.45),
          #'loc': 'lower left',
          #'bbox_to_anchor': (0.2, 0.9, 1.0, 0.2), #outside plot
          #'bbox_to_anchor': (0, 1.02, 1.0, 0.2), #outside plot
          #'bbox_to_anchor': (0.25, 1.),
          #'loc': 'upper left',
          #'title': 'Overhead (ns)',
          #'loc': 'lower left',
          #'bbox_to_anchor': (0, 0.65, 1, 0.2),
          'title_fontsize' : 12,
          'fontsize': 18,
          'ncol': 3,
          #'mode': 'expand',
          #'handles': legend_paches
          'frameon': False,
      },

      #'ticklabel_format': {
      #    'style': 'sci',
      #    'axis': 'y',
      #    'scilimits':(0, 0),
      #    'useLocale': True,
      #    'useMathText': True},

      #'title':{
      #    #'label': '{} requests'.format(TYPE).capitalize(),
      #    'label': 'Curtas',
      #    'loc': 'center'
      #},

      'ylim': [0, 80],
      'xlim': [0, 99.9],  # max(overhead) + 10],
      #'save': 'imgs/{}.pdf'.format(TYPE),
      'save': 'imgs/{}_{}_{}.pdf'.format(workload, TYPE, name),
      #'save': 'imgs/test.pdf'.format(workload, TYPE),
      #'save': 'imgs/{}.png'.format(TYPE),
      'show': 'n',
  }

  if TYPE == 'long' or TYPE == 'all':
      config['set_ticks']['ymajor'] = 150
      config['set_ticks']['yminor'] = 50
      config['ylim'] = [0, 600]
      config['legend']['ncol'] = 4

  if get_slowdown:
      config['save'] = 'imgs/slowdown_{}_{}.pdf'.format(workload, TYPE)
      config['ylabel'] = 'Slowdown'
      config['set_ticks']['ymajor'] = 25
      config['set_ticks']['yminor'] = 0
      config['ylim'] = [0, 100]

  c = charts.multrows_line(config)
