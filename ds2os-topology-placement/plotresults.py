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
COLORS = [
    '#8bc34a',
    '#009688',
    '#03a9f4',
    '#3f51b5',
    '#9c27b0',
    '#f44336',
    '#795548',
    '#ff9800',
    '#ffeb3b',
]

STRATEGY_STYLE = {
    'NO_CACHE':        'k:',
    'LCE':             'b-p',
    'LCD':             'g-1',
    'EDGE':            'y-s',
    'CL4M':            'r-2',
    'RAND_BERNOULLI':  'm-*',
    'PROB_CACHE':      'c-3',
    'PCASTING':        'g-x',
    # 'OPTIMAL':        'k-o'
}

# This dict maps name of strategies to names to be displayed in the legend
STRATEGY_LEGEND = {
    'NO_CACHE':        'No Caching',
    'LCE':             'LCE',
    'LCD':             'LCD',
    'EDGE':            'Edge',
    'CL4M':            'BTW',
    'RAND_BERNOULLI':  'Prob(0.2)',
    'PROB_CACHE':      'ProbCache',
    'PCASTING':        'pCASTING',
}


def run_ds2os(config, results, plotdir):
    settings = Settings()
    settings.read_from(config)
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    topology = 'DS2OS'
    alpha = 1.0  # TODO: calculate real alpha
    print(settings)
    cache_sizes = settings.NETWORK_CACHE #; pass CACHE_SIZES as xticks
    print(cache_sizes)
    strategies = settings.STRATEGIES
    # plot_cache_hits_vs_cache_size(resultset, topology, alpha, cache_sizes, strategies, plotdir)
    ds2os_plot_latency_vs_cache_size(
        resultset, topology, cache_sizes, strategies, plotdir)
    ds2os_plot_cache_hits_vs_cache_size(
        resultset, topology, cache_sizes, strategies, plotdir)
    logger.info('Exit. Plots were saved in directory %s' %
                os.path.abspath(plotdir))


def ds2os_plot_cache_hits_vs_cache_size(resultset, topology, cache_size_range, strategies, plotdir):
    desc = {}
    # desc['title'] = f'Cache hit ratio: T={topology}'
    strategies = [
        strategy for strategy in strategies if strategy != 'NO_CACHE']
    desc['xlabel'] = 'Total network cache capacity in number of objects (logarithmic scale)'
    desc['ylabel'] = 'Cache hit ratio'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['xticks'] = cache_size_range
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'DS2OS'}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(strategies)
    desc['ycondnames'] = [('strategy', 'name')] * len(strategies)
    desc['ycondvals'] = strategies
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right'
    desc['line_style'] = STRATEGY_STYLE
    desc['legend'] = STRATEGY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, f'CACHE_HIT_RATIO_T={topology}.pdf', plotdir)


def ds2os_plot_latency_vs_cache_size(resultset, topology, cache_size_range, strategies, plotdir):
    desc = {}
    print('plotting strategies', strategies)
    # desc['title'] = f'Latency: T={topology}'
    desc['xlabel'] = 'Total network cache capacity in number of objects (logarithmic scale)'
    desc['ylabel'] = 'Latency in ms'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['xticks'] = cache_size_range
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'DS2OS'}}
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(strategies)
    desc['ycondnames'] = [('strategy', 'name')] * len(strategies)
    desc['ycondvals'] = strategies
    desc['metric'] = ('LATENCY', 'MEAN')
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right'
    desc['line_style'] = STRATEGY_STYLE
    desc['legend'] = STRATEGY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, f'LATENCY_T={topology}.pdf', plotdir)


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
    run_ds2os(args.config, args.results, args.output)


if __name__ == '__main__':
    main()
