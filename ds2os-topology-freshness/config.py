from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

import icarus.models as cache

import csv

TRACE_PATH    = '/Users/danielmeint/experiments/trace/subTrace2.csv'
CONTENTS_PATH = '/Users/danielmeint/experiments/trace/contents.txt'
ADDRESSES_PATH = '/Users/danielmeint/experiments/trace/contentsNoVersions.txt' # all accessedNodeAddresses, no versions

# GENERAL SETTINGS


# compare three different freshness approaches (in terms of latency only?)
# 0. producer-based updates: caches always have the most recent version available: ignore versions?
# 1. producer-based callbacks/invalidations: assume caches (and consumers?) always know which is the most current version;
#    basically already implemented via version change on write; will have the best latency; make clear again that maintenance overhead is necessary
# 2. ttl-based: every version has a conservative estimate for a ttl; emulate by updating versions more often then necessary?
#    when objects are requested after ttl and not updated, make them uncacheable by always updating their version (! still use up caching space)
# 3. polling-every-time: emulate latency without caching

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
         'name':            'DS2OSNoVersions',
         'reqs_file':       TRACE_PATH,
         'contents_file':   ADDRESSES_PATH
        }

# mindestens 1 objekt pro cache, d.h. 6 objekte; 6/34465 = 0.00017408965
# NETWORK_CACHE = [0.00018, 0.00035, 0.0005, 0.0007, 0.001, 0.002, 0.005]
# NETWORK_CACHE = [0.00018, 0.0005, 0.0007, 0.002]
# NETWORK_CACHE = [
#     # 0.00018, # 6 objects
#     # 0.00035, # 12 objects
#     # # 0.0005, # 17 objects
#     0.00053, # 18 objects
#     # 0.0007, # 24 objects
#     # 0.00105, # 36 objects
#     # 0.00209, # 72 objects
#     # 0.00523 # 180 objects
# ]

# network cache sizes when there are only 34 contents
NETWORK_CACHE = [
    0.53 # 18 objects
]

# Set cache placement
default['cache_placement']['name'] = 'UNIFORM'

# Set content placement
default['content_placement']['name'] = 'DS2OS'

# caching meta-policies / placement strategies
STRATEGIES = [
    'NO_CACHE',        # No caching, shortest-path routing
    # 'LCE',             # Leave Copy Everywhere
    # 'LCD',
    # 'EDGE',
    # 'CL4M',            # Betweenness Centrality, Cache Less For More
    # 'PROB_CACHE',      # ProbCache
    # 'RAND_BERNOULLI',  # Random Bernoulli: cache randomly in caches on path
]

# Cache replacement policies
REPLACEMENT_POLICIES = [
    # 'MIN', # think this might not work when capacity == 1 at every cache
    # 'NULL',
    # 'FIFO',
    'LRU',
    # 'MDMR',
    # 'SLRU', # needs at least 2 segments to make sense, i.e. also at least 2 objects in each cache
    # # 'PERFECT_LFU',
    # 'IN_CACHE_LFU',
    # # 'IN_CACHE_LFU_EVICT_FIRST',
    # 'RAND',
    # # 'MDMR', problematic because many producers only offer one content chunk address // could extend to location, i.e. replace data from garage for data from garage etc.
]

# problem: we register 'TTL' and pass 'cache' and 'f_time' as arguments, however, the NetworkModel init assumes for every node a cache_size[node] as maxlen parameter, e.g. LruCache(10)
# we want the call to be ttl_cache(LruCache(10), f_time) but it does ttl_cache(10, LruCache(10), f_time) instead
# solved: manually changed in network.py
for strategy in STRATEGIES:
    for policy in REPLACEMENT_POLICIES:
        for network_cache in NETWORK_CACHE:
            experiment = copy.deepcopy(default)
            experiment['strategy']['name'] = strategy
            experiment['cache_policy']['name'] = policy
            experiment['cache_placement']['network_cache'] = network_cache
            experiment['desc'] = f'DS2OS topology, {strategy} placement strategy, {policy} replacement, {network_cache} network cache'
            EXPERIMENT_QUEUE.append(experiment)

