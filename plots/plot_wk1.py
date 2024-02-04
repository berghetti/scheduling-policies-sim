#!/bin/python3

import os
import sys

import charts
from plot_common import process_folder

TYPE=None
SV_TIME_SHORT=500

afp_i = psp_i = 0
workload = dist = None
def new_dataset(policy):
  global dist, workload
  global afp_i, psp_i

  policy = policy.rstrip('/')
  print('Policy: {}'.format(policy))

  policy_name = str(policy.split('/')[-1])
  #dist = str(policy.split('/')[2])
  workload = str(policy.split('/')[3])


  if 'psp' in policy:
    c = 'orange'
    m = 'o'
    ls = '-'
    ov = policy_name.split('_')[1].strip('ov')
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
  elif 'rss' in policy:
    c = 'red'
    m = 'x'
    ls = '-.'
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
        case 16:
            c = 'pink'
    policy_name = 'AFP-{}'.format(q)

  x, y, yerr = process_folder(policy, TYPE, SV_TIME_SHORT)

  print(policy_name, dist)

  return {
    'x': x,
    'y': y,
    'style': {
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

  # edit manually this general settings
  config = {
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
          'bbox_to_anchor': (0.5, 1.45),
          'title_fontsize' : 12,
          'fontsize': 18,
          'ncol': 3,
          #'mode': 'expand',
          'frameon': False,
      },

      #'title':{
      #    #'label': '{} requests'.format(TYPE).capitalize(),
      #    'label': 'Curtas',
      #    'loc': 'center'
      #},

      'ylim': [0, 80],
      'xlim': [0, 99.9],  # max(overhead) + 10],
      #'save': 'imgs/{}.pdf'.format(TYPE),
      'save': 'imgs/{}_{}_{}.pdf'.format(name, workload, TYPE),
      #'save': 'imgs/test.pdf'.format(workload, TYPE),
      #'save': 'imgs/{}.png'.format(TYPE),
      'show': 'n',
  }

  if TYPE == 'long' or TYPE == 'all':
      config['set_ticks']['ymajor'] = 500
      config['set_ticks']['yminor'] = 250
      config['ylim'] = [0, 2000]
      config['legend']['ncol'] = 4

  c = charts.multrows_line(config)
