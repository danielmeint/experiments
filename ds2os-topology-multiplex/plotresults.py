#!/usr/bin/env python
"""Plot results read from a result set
"""
from __future__ import division
import os
import argparse
import logging

import matplotlib.pyplot as plt

from icarus.util import Settings, config_logging
from icarus.results import plot_lines, plot_bar_chart
from icarus.registry import RESULTS_READER


# Logger object
logger = logging.getLogger('plot')

# These lines prevent insertion of Type 3 fonts in figures
# Publishers don't want them
plt.rcParams['ps.useafm'] = True
plt.rcParams['pdf.use14corefonts'] = True

# If True text is interpreted as LaTeX, e.g. underscore are interpreted as
# subscript. If False, text is interpreted literally
plt.rcParams['text.usetex'] = False

# Aspect ratio of the output figures
plt.rcParams['figure.figsize'] = 8, 5

# Size of font in legends
LEGEND_SIZE = 14

# Line width in pixels
LINE_WIDTH = 1.5

# Plot
PLOT_EMPTY_GRAPHS = True

# This dict maps strategy names to the style of the line to be used in the plots
# Off-path strategies: solid lines
# On-path strategies: dashed lines
# No-cache: dotted line
# STRATEGY_STYLE = {
#     'NO_CACHE':        'k:',
#     'LCE':             'b-p',
#     'LCD':             'g-1',
#     'EDGE':            'y-s',
#     'CL4M':            'r-2',
#     'PROB_CACHE':      'c-3',
#     'RAND_BERNOULLI':  'm-*',
#     # 'OPTIMAL':        'k-o'
# }

POLICY_STYLE = {
    'NULL':             'k:',
    'MIN':              'k-o',
    'FIFO':             'b-p',
    'LRU':              'g-1',
    'SLRU':             'y-s',
    'MDMR':             'b-x',
    'PERFECT_LFU':      'r-2',
    'IN_CACHE_LFU':     'c-3',
    'IN_CACHE_LFU_EVICT_FIRST': 'b-+',
    'RAND':             'm-*',
}

# This dict maps name of strategies to names to be displayed in the legend
# STRATEGY_LEGEND = {
#     'NO_CACHE':        'No Caching',
#     'LCE':             'LCE',
#     'LCD':             'LCD',
#     'EDGE':            'Edge',
#     'CL4M':            'BTW',
#     'PROB_CACHE':      'ProbCache',
#     'RAND_BERNOULLI':  'Prob(0.2)',
# }

POLICY_LEGEND = {
    'NULL':             'No Caching',
    'MIN':              'Belady\'s MIN',
    'FIFO':             'FIFO',
    'LRU':              'LRU',
    'SLRU':             'SLRU',
    'MDMR':             'MDMR',
    'PERFECT_LFU':      'Perfect LFU',
    'IN_CACHE_LFU':     'In-Cache LFU',
    'IN_CACHE_LFU_EVICT_FIRST': 'In-Cache LFU Evict First',
    'RAND':             'Random',
}


def run_ds2os(config, results, plotdir):
    settings = Settings()
    settings.read_from(config)
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    topology = 'DS2OS'
    cache_sizes = settings.NETWORK_CACHE
    # strategies = settings.STRATEGIES
    policies = settings.REPLACEMENT_POLICIES
    print(cache_sizes, policies)
    ds2os_plot_latency_vs_cache_size(
        resultset, topology, cache_sizes, policies, plotdir)
    # removes NO_CACHE from strategies
    ds2os_plot_cache_hits_vs_cache_size(
        resultset, topology, cache_sizes, policies, plotdir)
    logger.info(
        f'Exit. Plots were saved in directory {os.path.abspath(plotdir)}')


def ds2os_plot_cache_hits_vs_cache_size(resultset, topology, cache_size_range, policies, plotdir):
    desc = {}
    # if 'NO_CACHE' in strategies:
    #     strategies.remove('NO_CACHE') # is passed by reference so removes globally
    # desc['title'] = f'Cache hit ratio: T={topology}'
    policies = [policy for policy in policies if policy not in [
        'NULL', 'IN_CACHE_LFU_EVICT_FIRST']]
    desc['xlabel'] = 'Cache to population ratio'
    desc['ylabel'] = 'Cache hit ratio'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'DS2OS'}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, f'CACHE_HIT_RATIO_T={topology}.pdf', plotdir)


def ds2os_plot_latency_vs_cache_size(resultset, topology, cache_size_range, policies, plotdir):
    desc = {}
    # desc['title'] = f'Latency: T={topology}'
    desc['xlabel'] = 'Cache to population ratio'
    desc['ylabel'] = 'Latency'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'DS2OS'}}
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['metric'] = ('LATENCY', 'MEAN')
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, f'LATENCY_T={topology}.pdf', plotdir)


def run_tables(config, results, plotdir):
    settings = Settings()
    settings.read_from(config)
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    topology = 'DS2OS'
    strategies = settings.STRATEGIES
    policies = settings.REPLACEMENT_POLICIES
    cache_sizes = settings.NETWORK_CACHE
    print(strategies, policies, cache_sizes)
    results = dict()
    for k, v in resultset:
        strategy = k['strategy']['name']
        if strategy not in results:
            results[strategy] = dict()
        policy = k['cache_policy']['name']
        if policy not in results[strategy]:
            results[strategy][policy] = dict()
        cache_size = k['cache_placement']['network_cache']
        if cache_size not in results[strategy][policy]:
            results[strategy][policy][cache_size] = {
                'cache_hit_ratio': None,
                'latency': None
            }
        hit_ratio = v['CACHE_HIT_RATIO']['MEAN']
        latency = v['LATENCY']['MEAN']
        results[strategy][policy][cache_size]['cache_hit_ratio'] = hit_ratio
        results[strategy][policy][cache_size]['latency'] = latency
        # print(strategy, policy, cache_size, results[strategy][policy][cache_size])
    
    # no slru for smallest cache size
    for cache_size in cache_sizes:
        arr = [[''] + policies] + [[strategy] + [round(results[strategy][policy][cache_size]['cache_hit_ratio'] * 100, 2) for policy in policies] for strategy in strategies]
        print(arr_to_latex_table_rows(arr))

def arr_to_latex_table_rows(arr):
    return " \\\\\n".join([" & ".join(map(str,line)) for line in arr])

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("-r", "--results", dest="results",
                        help='the results file',
                        required=True)
    parser.add_argument("-o", "--output", dest="output",
                        help='the output directory where plots will be saved',
                        required=True)
    parser.add_argument("config",
                        help="the configuration file")
    args = parser.parse_args()
    # run(args.config, args.results, args.output)
    # run_ds2os(args.config, args.results, args.output)
    run_tables(args.config, args.results, args.output)

if __name__ == '__main__':
    main()

RESULTS = {
  'LCE': {
    'FIFO': {
      0.002: {
        'cache_hit_ratio': 0.38536567979850783,
        'latency': 10.57905241648054
      },
      0.0007: {
        'cache_hit_ratio': 0.3655966354607233,
        'latency': 10.765290120230006
      },
      0.0005: {
        'cache_hit_ratio': 0.2342109014874305,
        'latency': 12.401178539181675
      },
      0.00018: {
        'cache_hit_ratio': 0.04728413249061446,
        'latency': 14.408164235137576
      }
    },
    'LRU': {
      0.0007: {
        'cache_hit_ratio': 0.3679370812146557,
        'latency': 10.745330988927435
      },
      0.0005: {
        'cache_hit_ratio': 0.23214370574537851,
        'latency': 12.434206149313312
      },
      0.002: {
        'cache_hit_ratio': 0.3932186475312455,
        'latency': 10.503682934942736
      },
      0.00018: {
        'cache_hit_ratio': 0.04728413249061446,
        'latency': 14.408164235137576
      }
    },
    'MDMR': {
      0.002: {
        'cache_hit_ratio': 0.3932661692724421,
        'latency': 10.50320771753077
      },
      0.0005: {
        'cache_hit_ratio': 0.2767666207289835,
        'latency': 12.571971677042248
      },
      0.00018: {
        'cache_hit_ratio': 0.04728413249061446,
        'latency': 14.408164235137576
      },
      0.0007: {
        'cache_hit_ratio': 0.28926483866368863,
        'latency': 12.456874019864088
      }
    },
    'SLRU': {
      0.002: {
        'cache_hit_ratio': 0.3931592453547498,
        'latency': 10.504158152354702
      },
      0.0007: {
        'cache_hit_ratio': 0.2754597728460771,
        'latency': 12.082355177493703
      },
      0.0005: {
        'cache_hit_ratio': 0.08897257995532956,
        'latency': 14.074466568455069
      }
    },
    'IN_CACHE_LFU': {
      0.00018: {
        'cache_hit_ratio': 0.08887753647293636,
        'latency': 14.075226916314215
      },
      0.0005: {
        'cache_hit_ratio': 0.1656607898113387,
        'latency': 13.454117758874686
      },
      0.0007: {
        'cache_hit_ratio': 0.13216984270303664,
        'latency': 13.718528726892554
      },
      0.002: {
        'cache_hit_ratio': 0.20110012830870122,
        'latency': 13.10654374376277
      }
    },
    'RAND': {
      0.00018: {
        'cache_hit_ratio': 0.04728413249061446,
        'latency': 14.408164235137576
      },
      0.0007: {
        'cache_hit_ratio': 0.3640046571306373,
        'latency': 10.833626384070712
      },
      0.0005: {
        'cache_hit_ratio': 0.3230290357838711,
        'latency': 11.341253623532767
      },
      0.002: {
        'cache_hit_ratio': 0.3856626906809866,
        'latency': 10.578862329515754
      }
    }
  },
  'LCD': {
    'FIFO': {
      0.0007: {
        'cache_hit_ratio': 0.3765266359359407,
        'latency': 11.362923537518414
      },
      0.0005: {
        'cache_hit_ratio': 0.3082854155776268,
        'latency': 12.12807109252483
      },
      0.002: {
        'cache_hit_ratio': 0.3895832343297058,
        'latency': 11.236135532005893
      },
      0.00018: {
        'cache_hit_ratio': 0.11419474409542366,
        'latency': 13.873069429263888
      }
    },
    'LRU': {
      0.0005: {
        'cache_hit_ratio': 0.3142137527919023,
        'latency': 12.077270351185668
      },
      0.0007: {
        'cache_hit_ratio': 0.38676757116380744,
        'latency': 11.27082640307941
      },
      0.002: {
        'cache_hit_ratio': 0.3932305279665447,
        'latency': 11.197833008601435
      },
      0.00018: {
        'cache_hit_ratio': 0.11419474409542366,
        'latency': 13.873069429263888
      }
    },
    'MDMR': {
      0.0005: {
        'cache_hit_ratio': 0.2988523499501022,
        'latency': 12.357791189469182
      },
      0.0007: {
        'cache_hit_ratio': 0.30242836097514614,
        'latency': 12.328707883856865
      },
      0.002: {
        'cache_hit_ratio': 0.3932661692724421,
        'latency': 11.197500356413059
      },
      0.00018: {
        'cache_hit_ratio': 0.11419474409542366,
        'latency': 13.873069429263888
      }
    },
    'SLRU': {
      0.002: {
        'cache_hit_ratio': 0.3932067670959464,
        'latency': 11.19802309556622
      },
      0.0007: {
        'cache_hit_ratio': 0.3186689160290833,
        'latency': 12.020909566126504
      },
      0.0005: {
        'cache_hit_ratio': 0.1377180059877394,
        'latency': 13.656275245925011
      }
    },
    'IN_CACHE_LFU': {
      0.00018: {
        'cache_hit_ratio': 0.1327401035973958,
        'latency': 13.724706553248112
      },
      0.0005: {
        'cache_hit_ratio': 0.19328280188186095,
        'latency': 13.201016965261607
      },
      0.0007: {
        'cache_hit_ratio': 0.1903126930570736,
        'latency': 13.224635270636316
      },
      0.002: {
        'cache_hit_ratio': 0.24510526065675045,
        'latency': 12.78130494701326
      }
    },
    'RAND': {
      0.00018: {
        'cache_hit_ratio': 0.11419474409542366,
        'latency': 13.873069429263888
      },
      0.0005: {
        'cache_hit_ratio': 0.34433065627524595,
        'latency': 11.751366250059402
      },
      0.0007: {
        'cache_hit_ratio': 0.36780639642636503,
        'latency': 11.487335455971106
      },
      0.002: {
        'cache_hit_ratio': 0.38807441904671386,
        'latency': 11.25181770660077
      }
    }
  },
  'EDGE': {
    'FIFO': {
      0.0007: {
        'cache_hit_ratio': 0.3789621251722663,
        'latency': 10.66159768093903
      },
      0.002: {
        'cache_hit_ratio': 0.3877774081642351,
        'latency': 10.55895071995438
      },
      0.0005: {
        'cache_hit_ratio': 0.307192415530105,
        'latency': 11.82554768806729
      },
      0.00018: {
        'cache_hit_ratio': 0.11692724421422801,
        'latency': 13.851209428313453
      }
    },
    'LRU': {
      0.0007: {
        'cache_hit_ratio': 0.38019769044337787,
        'latency': 10.647721332509622
      },
      0.002: {
        'cache_hit_ratio': 0.3908900822126123,
        'latency': 10.522549066197785
      },
      0.0005: {
        'cache_hit_ratio': 0.3076201112008744,
        'latency': 11.827115905526778
      },
      0.00018: {
        'cache_hit_ratio': 0.11692724421422801,
        'latency': 13.851209428313453
      }
    },
    'MDMR': {
      0.0005: {
        'cache_hit_ratio': 0.28871833863992774,
        'latency': 12.476785629425462
      },
      0.0007: {
        'cache_hit_ratio': 0.2935180345007841,
        'latency': 12.417430974670912
      },
      0.002: {
        'cache_hit_ratio': 0.39092572351850974,
        'latency': 10.521978805303426
      },
      0.00018: {
        'cache_hit_ratio': 0.11692724421422801,
        'latency': 13.851209428313453
      }
    },
    'SLRU': {
      0.002: {
        'cache_hit_ratio': 0.390866321342014,
        'latency': 10.522881718386161
      },
      0.0007: {
        'cache_hit_ratio': 0.31680368768711686,
        'latency': 11.768901772560946
      },
      0.0005: {
        'cache_hit_ratio': 0.1331202775269686,
        'latency': 13.72166516181153
      }
    },
    'IN_CACHE_LFU': {
      0.00018: {
        'cache_hit_ratio': 0.1330965166563703,
        'latency': 13.721855248776315
      },
      0.0005: {
        'cache_hit_ratio': 0.20317920448605237,
        'latency': 13.156916789431165
      },
      0.0007: {
        'cache_hit_ratio': 0.21141234614836288,
        'latency': 13.090053699567552
      },
      0.002: {
        'cache_hit_ratio': 0.26127453309889276,
        'latency': 12.641543506154065
      }
    },
    'RAND': {
      0.00018: {
        'cache_hit_ratio': 0.11692724421422801,
        'latency': 13.851209428313453
      },
      0.0007: {
        'cache_hit_ratio': 0.3698617117331179,
        'latency': 10.834291688447465
      },
      0.0005: {
        'cache_hit_ratio': 0.3349569928242171,
        'latency': 11.384308321056883
      },
      0.002: {
        'cache_hit_ratio': 0.3863517559283372,
        'latency': 10.58632324288362
      }
    }
  },
  'CL4M': {
    'FIFO': {
      0.0007: {
        'cache_hit_ratio': 0.3749108967352564,
        'latency': 11.135246875445516
      },
      0.0005: {
        'cache_hit_ratio': 0.30587368721189945,
        'latency': 12.032885044908046
      },
      0.002: {
        'cache_hit_ratio': 0.38890604951765434,
        'latency': 10.990638216984271
      },
      0.00018: {
        'cache_hit_ratio': 0.11828161383833104,
        'latency': 13.840279427838237
      }
    },
    'LRU': {
      0.0007: {
        'cache_hit_ratio': 0.3815758209380792,
        'latency': 11.079503873021908
      },
      0.0005: {
        'cache_hit_ratio': 0.31037637219027703,
        'latency': 11.994012260609228
      },
      0.002: {
        'cache_hit_ratio': 0.3923394953191085,
        'latency': 10.95418904148648
      },
      0.00018: {
        'cache_hit_ratio': 0.11828161383833104,
        'latency': 13.840279427838237
      }
    },
    'MDMR': {
      0.0005: {
        'cache_hit_ratio': 0.29008458869932996,
        'latency': 12.465427933279475
      },
      0.0007: {
        'cache_hit_ratio': 0.29998099130352135,
        'latency': 12.34790666730029
      },
      0.002: {
        'cache_hit_ratio': 0.34667110202917834,
        'latency': 11.646485767238511
      },
      0.00018: {
        'cache_hit_ratio': 0.11828161383833104,
        'latency': 13.840279427838237
      }
    },
    'SLRU': {
      0.0007: {
        'cache_hit_ratio': 0.3192748182293399,
        'latency': 11.935703084161004
      },
      0.002: {
        'cache_hit_ratio': 0.391745473554151,
        'latency': 10.961507389630755
      },
      0.0005: {
        'cache_hit_ratio': 0.1378605712113292,
        'latency': 13.683505203630661
      }
    },
    'IN_CACHE_LFU': {
      0.00018: {
        'cache_hit_ratio': 0.1377180059877394,
        'latency': 13.684788290642969
      },
      0.0005: {
        'cache_hit_ratio': 0.21030746566554198,
        'latency': 13.10236183053747
      },
      0.0007: {
        'cache_hit_ratio': 0.20666017202870313,
        'latency': 13.130067005655087
      },
      0.002: {
        'cache_hit_ratio': 0.2456874019864088,
        'latency': 12.772988642303854
      }
    },
    'RAND': {
      0.00018: {
        'cache_hit_ratio': 0.11828161383833104,
        'latency': 13.840279427838237
      },
      0.0005: {
        'cache_hit_ratio': 0.3428337214275531,
        'latency': 11.55643206767096
      },
      0.0007: {
        'cache_hit_ratio': 0.3650263745663641,
        'latency': 11.287459012498218
      },
      0.002: {
        'cache_hit_ratio': 0.3870645820462862,
        'latency': 11.013496174499833
      }
    }
  },
  'PROB_CACHE': {
    'FIFO': {
      0.00018: {
        'cache_hit_ratio': 0.15689302856056647,
        'latency': 13.290547925675996
      },
      0.0005: {
        'cache_hit_ratio': 0.24461816280948534,
        'latency': 12.383357886232952
      },
      0.0007: {
        'cache_hit_ratio': 0.26190419616974764,
        'latency': 12.210378748277337
      },
      0.002: {
        'cache_hit_ratio': 0.30125219788053037,
        'latency': 11.869600342156536
      }
    },
    'LRU': {
      0.00018: {
        'cache_hit_ratio': 0.15729696336073754,
        'latency': 13.296583186807965
      },
      0.0005: {
        'cache_hit_ratio': 0.31383357886232954,
        'latency': 11.808487382977713
      },
      0.0007: {
        'cache_hit_ratio': 0.32325476405455494,
        'latency': 11.712493465760586
      },
      0.002: {
        'cache_hit_ratio': 0.32717530770327424,
        'latency': 11.639595114765005
      }
    },
    'MDMR': {
      0.00018: {
        'cache_hit_ratio': 0.15783158294919925,
        'latency': 13.28422753409685
      },
      0.0005: {
        'cache_hit_ratio': 0.3049588936938649,
        'latency': 12.035261131967875
      },
      0.0007: {
        'cache_hit_ratio': 0.3107090243786532,
        'latency': 11.967209998574347
      },
      0.002: {
        'cache_hit_ratio': 0.3275911229387445,
        'latency': 11.636126027657653
      }
    },
    'SLRU': {
      0.0005: {
        'cache_hit_ratio': 0.30589744808249775,
        'latency': 11.946110345483058
      },
      0.0007: {
        'cache_hit_ratio': 0.32387254669011073,
        'latency': 11.704652378463146
      },
      0.002: {
        'cache_hit_ratio': 0.3283989925390866,
        'latency': 11.624103027134915
      }
    },
    'IN_CACHE_LFU': {
      0.00018: {
        'cache_hit_ratio': 0.14382454973150216,
        'latency': 13.6340825927862
      },
      0.0005: {
        'cache_hit_ratio': 0.15078648481680368,
        'latency': 13.57710402509148
      },
      0.0007: {
        'cache_hit_ratio': 0.18611889939647389,
        'latency': 13.294634795418904
      },
      0.002: {
        'cache_hit_ratio': 0.15634652853680558,
        'latency': 13.505108587178634
      }
    },
    'RAND': {
      0.00018: {
        'cache_hit_ratio': 0.15645345245449793,
        'latency': 13.29805636078506
      },
      0.0005: {
        'cache_hit_ratio': 0.23493560804067862,
        'latency': 12.503255239271967
      },
      0.0007: {
        'cache_hit_ratio': 0.24769519555196504,
        'latency': 12.362495841847645
      },
      0.002: {
        'cache_hit_ratio': 0.2956089911134344,
        'latency': 11.927719431639975
      }
    }
  },
  'RAND_BERNOULLI': {
    'FIFO': {
      0.00018: {
        'cache_hit_ratio': 0.13672004942261085,
        'latency': 13.44523119327092
      },
      0.0005: {
        'cache_hit_ratio': 0.2546333697666682,
        'latency': 12.218362400798366
      },
      0.002: {
        'cache_hit_ratio': 0.32743667727985554,
        'latency': 11.556669676376943
      },
      0.0007: {
        'cache_hit_ratio': 0.2784298816708644,
        'latency': 11.978995390391104
      }
    },
    'LRU': {
      0.00018: {
        'cache_hit_ratio': 0.13441524497457588,
        'latency': 13.462909280996056
      },
      0.0005: {
        'cache_hit_ratio': 0.33877061255524404,
        'latency': 11.50810245687402
      },
      0.0007: {
        'cache_hit_ratio': 0.3524806348904624,
        'latency': 11.36691536377893
      },
      0.002: {
        'cache_hit_ratio': 0.35971581998764435,
        'latency': 11.268022620348809
      }
    },
    'MDMR': {
      0.00018: {
        'cache_hit_ratio': 0.13533003849261038,
        'latency': 13.458157106876396
      },
      0.0005: {
        'cache_hit_ratio': 0.33378082972960127,
        'latency': 11.740483771325382
      },
      0.002: {
        'cache_hit_ratio': 0.3602266787055078,
        'latency': 11.26982844651428
      },
      0.0007: {
        'cache_hit_ratio': 0.3427386779451599,
        'latency': 11.635603288504491
      }
    },
    'SLRU': {
      0.0007: {
        'cache_hit_ratio': 0.3531815805731122,
        'latency': 11.374518842370385
      },
      0.0005: {
        'cache_hit_ratio': 0.33427980801216556,
        'latency': 11.646200636791333
      },
      0.002: {
        'cache_hit_ratio': 0.35940692866986645,
        'latency': 11.272299577056504
      }
    },
    'IN_CACHE_LFU': {
      0.00018: {
        'cache_hit_ratio': 0.10095993917217126,
        'latency': 13.978187520790762
      },
      0.0005: {
        'cache_hit_ratio': 0.10174404790191513,
        'latency': 13.969063346481015
      },
      0.0007: {
        'cache_hit_ratio': 0.11998051608610939,
        'latency': 13.822648861854299
      },
      0.002: {
        'cache_hit_ratio': 0.12621774461816282,
        'latency': 13.730409162191703
      }
    },
    'RAND': {
      0.00018: {
        'cache_hit_ratio': 0.13479541890414865,
        'latency': 13.450791236990923
      },
      0.0005: {
        'cache_hit_ratio': 0.25162761963598346,
        'latency': 12.292638882288648
      },
      0.0007: {
        'cache_hit_ratio': 0.27007793565556243,
        'latency': 12.100365917407213
      },
      0.002: {
        'cache_hit_ratio': 0.320712350900537,
        'latency': 11.629805636078506
      }
    }
  }
}