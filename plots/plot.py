#!/bin/python3

# example use
# ./plot.py afp psp dfcfs
#
# to each policy this script access '../tests' folder process results and
# plot chart

import charts
import csv
import sys
import os
import math

TYPE = 'short'
#TYPE = 'long'

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

def get_throughput(file):
    buffer = []
    with open(file, newline = '') as f:
        reader = csv.DictReader(f)
        for row in reader:
            buffer.append(float(row["Throughput_config"]) / 1e6)

    return buffer

def get_latency(file, col=None):
    buffer = []
    with open(file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = int(float(row[col]))
            if lat > 0:
                buffer.append( lat / 1e3)

    return buffer

def rps_in_file_name(f):
    return int(f.split('_')[1])
    #return int(f.split('_')[2])

def process_folder(folder):
    x = []
    y = []
    yerr = []

    files = os.listdir(folder)
    files = sorted(files, key=rps_in_file_name)

    for file in files:
        f = os.path.join(folder, file)
        if not os.path.isfile(f):
            continue

        print('Reading file \'{}\''.format(file))

        tr = get_throughput(f)
        if len(tr) == 0:
            print('Error file {}. Aborting'.format(file))
            exit(1)

        try:
            lat = get_latency(f, " 'latency_{} 99.9%'".format(TYPE))
        except KeyError:
            lat = get_latency(f, 'latency_{} 99.9%'.format(TYPE))
        if len(lat) == 0: continue

        avg, error = interval_confidence(lat)
        x.append(tr[0])
        y.append(avg)
        yerr.append(error)

    return x, y, yerr

def get_next(array):
  return

colors = ['orange', 'green', 'mediumblue', 'maroon', 'purple']
linestyles = [ '-', '--', ':', '-.' ]
markers = ['o', '*', 'P', 's', 'p' ]

i = 0
def new_dataset(policy):
  global i

  x, y, yerr = process_folder('../tests/{}'.format(policy))

  c = colors[ i % len(colors) ]
  ls = linestyles[ i % len(linestyles) ]
  m = markers[ i % len(markers) ]
  i += 1

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
      'xlabel': 'Throughput (MRPS)',
      'ylabel': 'Latency 99.9% (us)',

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
          'ymajor': 50,
          'yminor': 25,
      },

      'legend': {
          'loc': 'best',
      #    'title': 'Overhead (ns)',
          'title_fontsize' : 12,
          'fontsize': 10,
      },

      'title':{
          'label': '{} requests (0.5 us)'.format(TYPE).capitalize(),
          'loc': 'center'
      },

      'ylim': [0, 300],
      'xlim': [0, 5],  # max(overhead) + 10],
      #'save': 'imgs/{}.pdf'.format(TYPE),
      'save': 'imgs/{}.png'.format(TYPE),
      #'show': 'y'
  }

  if TYPE == 'long':
      config['title']['label'] = '{} requests (500 us)'.format(TYPE).capitalize()
      config['set_ticks']['ymajor'] = 500
      config['set_ticks']['yminor'] = 250
      config['ylim'] = [0, 3500]


  c = charts.line(config)
