"""Configuration file for running a single simple simulation."""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = False

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Number of times each experiment is replicated
N_REPLICATIONS = 1

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported
RESULTS_FORMAT = 'PICKLE'

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icarus/execution/collectors.py
DATA_COLLECTORS = ['CACHE_HIT_RATIO', 'LATENCY']

# Queue of experiments
EXPERIMENT_QUEUE = deque()

# Create experiment
default = Tree()

# Set topology
default['topology']['name'] = 'DS2OS'
# default['topology']['delay'] = 10

# Set workload
default['workload'] = {
         'name':       'STATIONARY',
         'n_contents': 10 ** 5,
         'n_warmup':   10 ** 2,
         'n_measured': 4 * 10 ** 2,
         'alpha':      1.0,
         'rate':       1
                       }

# Set cache placement
default['cache_placement']['name'] = 'UNIFORM'
default['cache_placement']['network_cache'] = 0.01

# Set content placement
default['content_placement']['name'] = 'UNIFORM'

# caching meta-policies / placement strategies
STRATEGIES = [
     'LCE',             # Leave Copy Everywhere
     'NO_CACHE',        # No caching, shortest-path routing
     'PROB_CACHE',      # ProbCache
     'RAND_BERNOULLI',  # Random Bernoulli: cache randomly in caches on path
             ]

# default['strategy']['name'] = 'LCD'

# Cache replacement policies
REPLACEMENT_POLICIES = [
    'LRU',
    'PERFECT_LFU',
    'IN_CACHE_LFU',
    'RAND',
]

# default['cache_policy']['name'] = 'LRU'

for strategy in STRATEGIES:
    for policy in REPLACEMENT_POLICIES:
        experiment = copy.deepcopy(default)
        experiment['strategy']['name'] = strategy
        experiment['cache_policy']['name'] = policy
        experiment['desc'] = f'DS2OS topology, {strategy} placement strategy, {policy} replacement'
        EXPERIMENT_QUEUE.append(experiment)
