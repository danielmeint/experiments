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
         'reqs_file':       '/Users/danielmeint/experiments/trace/subTrace2.csv',
         'contents_file':   '/Users/danielmeint/experiments/trace/contents.txt'
        }

# default['workload'] = {
#          'name':       'STATIONARY',
#          'n_contents': 10 ** 5,
#          'n_warmup':   10 ** 2,
#          'n_measured': 4 * 10 ** 2,
#          'alpha':      1.0,
#          'rate':       1
#     }

NETWORK_CACHE = [0.002, 0.004, 0.01, 0.05]

# Set cache placement
default['cache_placement']['name'] = 'UNIFORM'
# default['cache_placement']['network_cache'] = 0.01

# Set content placement
# default['content_placement']['name'] = 'UNIFORM'
default['content_placement']['name'] = 'DS2OS'

# !!! lce and lcd gave same cache hit ratio? only single-hops? but chr for individual agents differ??

# default['strategy']['name'] = 'LCD'

# Cache replacement policies
# REPLACEMENT_POLICIES = [
#     'LRU',
#     'PERFECT_LFU',
#     'IN_CACHE_LFU',
#     'RAND',
# ]

default['cache_policy']['name'] = 'LRU'

p02 = copy.deepcopy(default)
p05 = copy.deepcopy(default)

p02['strategy']['name'] = 'RAND_BERNOULLI'
p05['strategy']['name'] = 'RAND_BERNOULLI'

p02['strategy']['n']    = 0.2
p05['strategy']['n']    = 0.5

p02['desc'] = 'DS2OS topology, Prob(0.2) placement, LRU replacement'
p05['desc'] = 'DS2OS topology, Prob(0.5) placement, LRU replacement'

lce = copy.deepcopy(default)
lce['strategy']['name'] = 'LCE'

cache_policy = Tree()

# problem: we register 'TTL' and pass 'cache' and 'f_time' as arguments, however, the NetworkModel init assumes for every node a cache_size[node] as maxlen parameter, e.g. LruCache(10)
# we want the call to be ttl_cache(LruCache(10), f_time) but it does ttl_cache(10, LruCache(10), f_time) instead
# solved: manually changed in network.py

# how to get a good f_time function

# in engine.py > exec_experiment, strategy_inst.process_event must be passed time, event where event has ttl or expires values
# time is a float type

# 0.3317255144228485


# !!! eigentlich sollte v5 v4 ersetzen

PROB_P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

for p in PROB_P:
    experiment = copy.deepcopy(default)
    experiment['strategy']['name'] = 'RAND_BERNOULLI'
    experiment['strategy']['p']    = p
    experiment['cache_placement']['network_cache'] = 0.002
    experiment['desc'] = f'DS2OS topology, Prob({p}) placement, LRU replacement, 0.002 network cache'
    EXPERIMENT_QUEUE.append(experiment)
