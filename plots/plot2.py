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

SV_TIME_SHORT = 500

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

    if get_slowdown:
        return interval_confidence(sld)

    return interval_confidence(lat)

def rps_in_file_name(f):
    #return int(f.split('_')[-1])
    return float(f.split('_')[-1])

def process_folder(folder_tests):
    x = []
    y = []
    yerr = []


    folders = os.listdir(folder_tests)
    folders = sorted(folders, key=rps_in_file_name)

    for folder in folders:
        #tr = int(folder) / 1000000 #RPS
        tr = float(folder) * 100 #RPS

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
#markers = ['*', 'P', 's', 'p' ]
#labels = ['Exp', 'Lognorm', 'Pareto']

#afp_colors = ['blue', 'deepskyblue', 'darkviolet' ]
#psp_colors = ['red', 'orange', 'goldenrod']

#afp_line = mlines.Line2D([], [], color='blue', linestyle='-', label='AFP')
#psp_line = mlines.Line2D([], [], color='orange', linestyle='-', label='PSP')
#
#legend_paches = [afp_line, psp_line]
#
#for i in range(len(colors)):
#  legend_paches.append(
#    mlines.Line2D([], [], color=colors[i], marker=markers[i], linestyle='None',
#                          markersize=3.0, label=labels[i])
#  )


i = j = k = l = 0
workload = dist = None
def new_dataset(policy):
  global i, j, k, l
  global dist, workload

  policy = policy.rstrip('/')
  print('Policy: {}'.format(policy))

  x, y, yerr = process_folder(policy)

  if 'psp' in policy:
    #c = psp_colors[ i % len(colors) ]
    c = 'orange'
    m = 'o'
    #ls = linestyles[ i % len(linestyles) ]
    ls = '-'
    i += 1
  elif 'afp-rr' in policy:
    c = 'red'
    m = '2'
    ls = ':'
    #ls = linestyles[ l % len(linestyles) ]
    l += 1
  else:
    #c = afp_colors[ j % len(colors) ]
    #ls = linestyles[ j % len(linestyles) ]
    ls = '--'
    m = 's'
    c = 'blue'
    j += 1


  #policy = str(policy)

  policy_name = str(policy.split('/')[-1].split('_')[0]).upper()
  dist = str(policy.split('/')[2]).capitalize()
  workload = str(policy.split('/')[3]).capitalize()
  #dist = ''

  print(policy_name, dist)

  #if last_dist == None:
  #  last_dist = dist
  #elif last_dist != dist:
  #  k += 1
  #  last_dist = dist

  #mc = colors[ k % len(colors) ]
  #m = markers[ k % len(markers) ]
  #k += 1

  return {
    'x': x,
    'y': y,
    'style': {
        #'label': '{} - {}'.format(policy_name, dist),
        'label': '{}'.format(policy_name),
        'color': c,
        'linestyle': ls,
        'marker': m,
        'linewidth': 1.0,
        'markersize': 5.0,
        #'markerfacecolor': mc,
        #'markeredgecolor': mc
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
        'markersize': 5.0,
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

        if dist not in d:
            d[dist] = []

        d[dist].append(new_dataset(policy))

    #print(d)
    return d



if __name__ == '__main__':

  locale.setlocale(locale.LC_NUMERIC, "pt_BR.utf8")#

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

  #rows = multdatasets_create(sys.argv[1:])
  #print('total datasets {}'.format(len(rows)))


  for policy in sys.argv[1:]:
     datasets.append(new_dataset(policy))

  # edit manually this general settings
  config = {
      'datasets': datasets,
      #'mult_datasets': rows,
      #'xlabel': 'Throughput (MRPS)',
      'xlabel': 'Utilização (%)',
      #'ylabel': 'Latency 99.9% (us)',
      'ylabel': 'Latência de Cauda ($\mu$s)',

      'font': {
          'font.size':23,
          'axes.labelsize': 23,
          'axes.titlesize': 23,
          'xtick.labelsize': 23,
          'ytick.labelsize': 23,
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
          'ymajor': 10,
          'yminor': 5,
      },

      'legend': {
          #'loc': 'lower center',
          #'bbox_to_anchor': (0, 1.02, 1.0, 0.2), #outside plot
          #'bbox_to_anchor': (0.25, 1.),
          #'loc': 'upper left',
          'loc': 'best',
      #    'title': 'Overhead (ns)',
          'title_fontsize' : 12,
          'fontsize': 15,
          'ncol': 1,
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

      'ylim': [0, 50],
      'xlim': [0, 80],  # max(overhead) + 10],
      #'save': 'imgs/{}.pdf'.format(TYPE),
      'save': 'imgs/{}_{}.pdf'.format(workload, TYPE),
      #'save': 'imgs/{}_{}.pdf'.format(workload, TYPE),
      #'save': 'imgs/{}.png'.format(TYPE),
      'show': 'n',
  }

  if TYPE == 'long' or TYPE == 'all':
      config['set_ticks']['ymajor'] = 1000
      config['set_ticks']['yminor'] = 500
      config['ylim'] = [0, 3000]
      #config['set_ticks']['ymajor'] = 150
      #config['set_ticks']['yminor'] = 50
      #config['ylim'] = [0, 600]
      #pass

  if get_slowdown:
      config['save'] = 'imgs/slowdown_{}_{}.pdf'.format(workload, TYPE)
      config['ylabel'] = 'Slowdown'
      config['set_ticks']['ymajor'] = 10
      config['set_ticks']['yminor'] = 5
      config['ylim'] = [0, 100]

  c = charts.line(config)
