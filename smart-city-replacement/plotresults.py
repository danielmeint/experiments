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
    'DS2OS_PERFECT_LFU': 'r-x',
    'RAND':             'm-*',
}

POLICY_LEGEND = {
    'NULL':             'No Caching',
    'MIN':              'Belady\'s MIN',
    'FIFO':             'FIFO',
    'LRU':              'LRU',
    'SLRU':             'SLRU',
    'MDMR':             'MDMR',
    'PERFECT_LFU':      'Perfect LFU',
    'IN_CACHE_LFU':     'In-Cache LFU',
    'IN_CACHE_LFU_EVICT_FIRST': 'In-Cache LFU',
    'DS2OS_PERFECT_LFU': 'Version-agnostic Perfect LFU',
    'RAND':             'Random',
}


def plot_cache_hits_vs_alpha(resultset, topology, cache_size, alpha_range, policies, plotdir):
    desc = {}
    # desc['title'] = 'Cache hit ratio: T=%s C=%s' % (topology, cache_size)
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = f"Skewness of the request ditribution (Zipf $\\alpha$ parameter)"
    desc['xparam'] = ('workload', 'alpha')
    desc['xvals'] = alpha_range
    desc['filter'] = {'topology': {'name': topology},
                      'cache_placement': {'network_cache': cache_size}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['errorbar'] = False
    desc['legend_loc'] = 'upper left'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, 'CACHE_HIT_RATIO_T=%s@C=%s.pdf'
               % (topology, cache_size), plotdir)


def plot_cache_hits_vs_cache_size(resultset, topology, alpha, cache_size_range, policies, plotdir):
    desc = {}
    # desc['title'] = 'Cache hit ratio: T=%s A=%s' % (topology, alpha)
    desc['title']  = f"$\\alpha$={alpha}"
    # desc['xlabel'] = u'Cache to population ratio'
    desc['xlabel'] = 'Capacity per cache in number of objects (logarithmic scale)'
    desc['ylabel'] = 'Cache hit ratio'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['xticks'] = cache_size_range
    desc['ymin'] = 0
    desc['ymax'] = 1
    desc['xticklabels'] = [1, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'STATIONARY', 'alpha': alpha}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['errorbar'] = False
    desc['legend_loc'] = 'upper left'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, 'CACHE_HIT_RATIO_T=%s@A=%s.pdf'
               % (topology, alpha), plotdir)


def plot_link_load_vs_alpha(resultset, topology, cache_size, alpha_range, policies, plotdir):
    desc = {}
    desc['title'] = 'Internal link load: T=%s C=%s' % (topology, cache_size)
    desc['xlabel'] = f"Skewness of the request ditribution (Zipf $\\alpha$ parameter)"
    desc['ylabel'] = 'Internal link load'
    desc['xparam'] = ('workload', 'alpha')
    desc['xvals'] = alpha_range
    desc['filter'] = {'topology': {'name': topology},
                      'cache_placement': {'network_cache': cache_size}}
    desc['ymetrics'] = [('LINK_LOAD', 'MEAN_INTERNAL')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['errorbar'] = False
    desc['legend_loc'] = 'upper right'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, 'LINK_LOAD_INTERNAL_T=%s@C=%s.pdf'
               % (topology, cache_size), plotdir)


def plot_link_load_vs_cache_size(resultset, topology, alpha, cache_size_range, policies, plotdir):
    desc = {}
    desc['title'] = 'Internal link load: T=%s A=%s' % (topology, alpha)
    desc['xlabel'] = 'Cache to population ratio'
    desc['ylabel'] = 'Internal link load'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'stationary', 'alpha': alpha}}
    desc['ymetrics'] = [('LINK_LOAD', 'MEAN_INTERNAL')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['errorbar'] = False
    desc['legend_loc'] = 'upper right'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, 'LINK_LOAD_INTERNAL_T=%s@A=%s.pdf'
               % (topology, alpha), plotdir)


def plot_latency_vs_alpha(resultset, topology, cache_size, alpha_range, policies, plotdir):
    desc = {}
    # desc['title'] = 'Latency: T=%s C=%s' % (topology, cache_size)
    # desc['xlabel'] = 'Content distribution alpha parameter'
    # desc['xlabel'] = f"$\\alpha$ parameter of Zipf distribution"
    desc['xlabel'] = f"Skewness of the request ditribution (Zipf $\\alpha$ parameter)"
    desc['ylabel'] = 'Latency in ms'
    desc['xparam'] = ('workload', 'alpha')
    desc['xvals'] = alpha_range
    desc['filter'] = {'topology': {'name': topology},
                      'cache_placement': {'network_cache': cache_size}}
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['errorbar'] = False
    desc['legend_loc'] = 'upper right'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, 'LATENCY_T=%s@C=%s.pdf'
               % (topology, cache_size), plotdir)


def plot_latency_vs_cache_size(resultset, topology, alpha, cache_size_range, policies, plotdir):
    desc = {}
    # desc['title'] = 'Latency: T=%s A=%s' % (topology, alpha)
    desc['title']  = f"$\\alpha$={alpha}"
    desc['xlabel'] = 'Capacity per cache in number of objects (logarithmic scale)'
    desc['ylabel'] = 'Latency in ms'
    desc['xscale'] = 'log'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['xticks'] = cache_size_range # daniel
    desc['ymin'] = 100
    desc['ymax'] = 350
    desc['xticklabels'] = [1, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    desc['filter'] = {'topology': {'name': topology},
                      'workload': {'name': 'STATIONARY', 'alpha': alpha}}
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(policies)
    desc['ycondnames'] = [('cache_policy', 'name')] * len(policies)
    desc['ycondvals'] = policies
    desc['metric'] = ('LATENCY', 'MEAN')
    desc['errorbar'] = False
    desc['legend_loc'] = 'upper right'
    desc['line_style'] = POLICY_STYLE
    desc['legend'] = POLICY_LEGEND
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, 'LATENCY_T=%s@A=%s.pdf'
               % (topology, alpha), plotdir)

def run(config, results, plotdir):
    """Run the plot script

    Parameters
    ----------
    config : str
        The path of the configuration file
    results : str
        The file storing the experiment results
    plotdir : str
        The directory into which graphs will be saved
    """
    settings = Settings()
    settings.read_from(config)
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    # Parse params from settings
    topology = 'TS'
    cache_sizes = settings.NETWORK_CACHE
    alphas = settings.ALPHA
    # strategies = settings.STRATEGIES
    policies = settings.REPLACEMENT_POLICIES
    # Plot graphs

    for cache_size in cache_sizes:
        logger.info('Plotting cache hit ratio for topology %s and cache size %s vs alpha' % (
            topology, str(cache_size)))
        plot_cache_hits_vs_alpha(
            resultset, topology, cache_size, alphas, policies, plotdir)
        logger.info('Plotting latency for topology %s vs cache size %s' % (
            topology, str(cache_size)))
        plot_latency_vs_alpha(resultset, topology,
                                cache_size, alphas, policies, plotdir)
    for alpha in alphas:
        logger.info('Plotting cache hit ratio for topology %s and alpha %s vs cache size' % (
            topology, str(alpha)))
        plot_cache_hits_vs_cache_size(
            resultset, topology, alpha, cache_sizes, policies, plotdir)
        logger.info('Plotting latency for topology %s and alpha %s vs cache size' % (
            topology, str(alpha)))
        plot_latency_vs_cache_size(
            resultset, topology, alpha, cache_sizes, policies, plotdir)


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
    run(args.config, args.results, args.output)


if __name__ == '__main__':
    main()
