from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

import icarus.models as cache

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

# Set workload
default['workload'] = {
         'name':            'DS2OS',
         'reqs_file':       '/Users/danielmeint/experiments/trace/subTraceWriteTimes.csv',
         'contents_file':   '/Users/danielmeint/experiments/trace/contentsWriteTimes.txt'
        }

# mindestens 1 objekt pro cache, d.h. 6 objekte; 6/34465 = 0.00017408965
# warum 56595 objekte in contentWriteTimes
TOTAL_OBJECTS = 56595

CACHE_SIZES = [6, 12, 18, 24, 36, 72, 180]

NETWORK_CACHE = [size/TOTAL_OBJECTS for size in CACHE_SIZES]

# Set cache placement
default['cache_placement']['name'] = 'UNIFORM'

# Set content placement
default['content_placement']['name'] = 'DS2OS'

# Set cache replacement policy
default['cache_policy']['name'] = 'LRU'

# caching meta-policies / placement strategies
STRATEGIES = [
    'NO_CACHE',        # No caching, shortest-path routing
    'LCE',             # Leave Copy Everywhere
    'LCD',
    'EDGE',
    'CL4M',            # Betweenness Centrality, Cache Less For More
    'RAND_BERNOULLI',  # Random Bernoulli: cache randomly in caches on path
    'PROB_CACHE',      # ProbCache
    'PCASTING',
]

for strategy in STRATEGIES:
    for network_cache in NETWORK_CACHE:
        experiment = copy.deepcopy(default)
        experiment['strategy']['name'] = strategy
        experiment['cache_placement']['network_cache'] = network_cache
        # experiment['workload']['alpha'] = 1.0
        experiment['desc'] = f'DS2OS topology, {strategy} placement strategy, LRU replacement, {network_cache} network cache'
        EXPERIMENT_QUEUE.append(experiment)
