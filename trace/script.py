import numpy as np
import matplotlib.pyplot as plt

LEGEND_SIZE = 14

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

alphas    = [0, 0.25, 0.5, 0.75, 1]
perc_diff = [0.945045434876679, 0.9678961552528342, 2.878644850010481, 7.30965599551332, 14.640917624625672]
# lfu  = [323.54,   320.4476, 305.088,  261.7524, 190.4744]
# rr   = [326.5976, 323.5492, 313.8704, 280.8856, 218.3616]
# lru  = [329.15,   327.2288, 319.3072, 288.8568, 221.9272]
# slru = [332.2304, 327.3696, 313.3148, 272.3912, 204.8156]
latencies = {
    'IN_CACHE_LFU_EVICT_FIRST':  [323.54,   320.4476, 305.088,  261.7524, 190.4744],
    'RAND':   [326.5976, 323.5492, 313.8704, 280.8856, 218.3616],
    'LRU':  [329.15,   327.2288, 319.3072, 288.8568, 221.9272],
    'SLRU': [332.2304, 327.3696, 313.3148, 272.3912, 204.8156]
}

# These lines prevent insertion of Type 3 fonts in figures
# Publishers don't want them
plt.rcParams['ps.useafm'] = True
plt.rcParams['pdf.use14corefonts'] = True

# If True text is interpreted as LaTeX, e.g. underscore are interpreted as
# subscript. If False, text is interpreted literally
plt.rcParams['text.usetex'] = False


def main():
    for key in latencies:
        arr = latencies[key]
        factors = []
        for i in range(len(arr)):
            factors += [arr[i]/latencies['IN_CACHE_LFU_EVICT_FIRST'][i]]
        diffs = [(factor - 1)*100 for factor in factors]
        print(key, diffs)
        if key != 'IN_CACHE_LFU_EVICT_FIRST':
            plt.plot(alphas, diffs, color=POLICY_STYLE[key][0], marker=POLICY_STYLE[key][-1])
    # plt.plot(alphas, perc_diff)
    # plt.xticks(alphas)
    plt.xlabel('Content distribution alpha parameter')
    plt.ylabel('Relative latency difference in %')
    legend = [POLICY_LEGEND[l] for l in ['RAND', 'LRU', 'SLRU']]
    plt.legend(legend, prop={'size': LEGEND_SIZE})
    plt.show()

if __name__ == "__main__":
    main()