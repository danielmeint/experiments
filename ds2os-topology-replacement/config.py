from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

import icarus.models as cache

import csv

TRACE_PATH    = '/Users/danielmeint/experiments/trace/subTraceWriteTimes.csv'
CONTENTS_PATH = '/Users/danielmeint/experiments/trace/contentsWriteTimes.txt'

# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

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
         'reqs_file':       TRACE_PATH,
         'contents_file':   CONTENTS_PATH
        }

N_CONTENTS = 56595
N_CACHES = 6

CACHE_SIZES = [1, 2, 3, 4, 5, 6, 8, 16] # capacity per cache in objects

NETWORK_CAPACITY = [(size * N_CACHES) for size in CACHE_SIZES] # total network capacity in objects

NETWORK_CACHE = [(capacity / N_CONTENTS) for capacity in NETWORK_CAPACITY] # total network capacity as fraction of total content objects
# NETWORK_CACHE = [0.00035, 0.002]

# Set cache placement
default['cache_placement']['name'] = 'UNIFORM'

# Set content placement
default['content_placement']['name'] = 'DS2OS'

# Set placement strategy
default['strategy']['name'] = 'LCE'

# Cache replacement policies
REPLACEMENT_POLICIES = [
    # 'MIN', # think this might not work when capacity == 1 at every cache
    'NULL',
    'FIFO',
    'LRU',
    'PERFECT_LFU',
    'IN_CACHE_LFU',
    'SLRU', # needs at least 2 segments to make sense, i.e. also at least 2 objects in each cache
    'MDMR', # many producers only offer one content chunk address // could extend to location, i.e. replace data from garage for data from garage etc.
    'LFF',
    # 'DS2OS_PERFECT_LFU',
    # 'IN_CACHE_LFU_EVICT_FIRST', # performs worse then In-cache LFU
    'RAND',
]

# problem: we register 'TTL' and pass 'cache' and 'f_time' as arguments, however, the NetworkModel init assumes for every node a cache_size[node] as maxlen parameter, e.g. LruCache(10)
# we want the call to be ttl_cache(LruCache(10), f_time) but it does ttl_cache(10, LruCache(10), f_time) instead
# solved: manually changed in network.py
for policy in REPLACEMENT_POLICIES:
    for network_cache in NETWORK_CACHE:
        experiment = copy.deepcopy(default)
        experiment['cache_policy']['name'] = policy
        experiment['cache_placement']['network_cache'] = network_cache
        experiment['desc'] = f'DS2OS topology, LCE placement strategy, {policy} replacement, {network_cache} network cache'
        # segments must be an integer and 0 < segments <= maxlen
        # alternatively manually set segments = 1; default is 2
        if policy == 'SLRU' and network_cache * N_CONTENTS <= 6: # 6 KAs in the network
            experiment['cache_policy']['segments'] = 1
        EXPERIMENT_QUEUE.append(experiment)
