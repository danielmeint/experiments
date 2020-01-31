# bei jedem write wird ein update ausgeführt, d.h. neue Version der destServiceAddress

# unter 'normalen' request gibt es nur writes zur eigenen Adresse (sourceAddress == destinationServiceAddress) oder an den destinationServiceType == batteryService, v.a. an washing machines (?)

# timestamp 1520031600000
# Assuming that this timestamp is in milliseconds:
# GMT: Friday, 2. March 2018 23:00:00
# Your time zone: Samstag, 3. März 2018 00:00:00 GMT+01:00
# Relative: 2 years ago

import csv
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

res = []
agents = set()
edges  = set()
services = set()

requests = []

lastWrite = 0
tempin3interUpdateTimes = []

def setup():
    with open('/Users/danielmeint/Desktop/fullTrace.csv', 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader) # skip the first row / header
        for row in reader:
            sourceID,sourceAddress,sourceType,sourceLocation,destinationServiceAddress,destinationServiceType,destinationLocation,accessedNodeAddress,accessedNodeType,operation,value,timestamp,normality = row
            requests.append({
                'sourceID': sourceID,
                'sourceAddress': sourceAddress,
                'sourceType': sourceType,
                'sourceLocation': sourceLocation,
                'destinationServiceAddress': destinationServiceAddress,
                'destinationServiceType': destinationServiceType,
                'destinationLocation': destinationLocation,
                'accessedNodeAddress': accessedNodeAddress,
                'accessedNodeType': accessedNodeType,
                'operation': operation,
                'value': value,
                'timestamp': timestamp,
                'normality': normality
            })

def draw_graph(graph):
    # extract nodes from graph
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])

    print("nodes:", nodes)

    # create networkx graph
    G=nx.Graph()

    # add nodes
    for node in nodes:
        G.add_node(node)

    # add edges
    for edge in graph:
        G.add_edge(edge[0], edge[1])

    # draw graph
    pos = nx.shell_layout(G)
    nx.draw(G, pos)

    # show graph
    plt.show()


def plotWriteInterarrivalTimes(sensor='tempin3'):
    normalRequests = [request for request in requests if request['normality'] == 'normal']
    updates = [r for r in requests if r['sourceID'] == sensor and r['operation'] == 'write']
    interarrivaltimes = [int(updates[i]['timestamp']) - int(updates[i-1]['timestamp']) for i in range(1, len(updates))]
    
    fig1, ax1 = plt.subplots()
    ax1.set_title('Time between updates for a temperature sensor in ms')
    ax1.boxplot(interarrivaltimes, showfliers=False)
    plt.xticks([1], [sensor])

    plt.show()


def getRooms(trace):
    res = {}
    for request in trace:
        sourceLoc = request['sourceLocation']
        address   = request['sourceAddress']
        if sourceLoc not in res:
            res[sourceLoc] = set()
        else:
            res[sourceLoc].add(address)
    return res

def getEdges(trace):
    res = set()
    for request in trace:
        sourceAgent = int(request['sourceAddress'].split('/')[1][5:])
        destAgent   = int(request['destinationServiceAddress'].split('/')[1][5:])
        if sourceAgent != destAgent:
            edge        = (sourceAgent, destAgent) if sourceAgent < destAgent else (destAgent, sourceAgent)
            res.add(edge)
    return res

def getNormalRequests(trace):
    return [r for r in requests if r['normality'] == 'normal']

def main():
    setup()
    edges = getEdges(getNormalRequests(requests))
    print(edges)
    draw_graph(edges)
    # print(getRooms([r for r in requests if r['normality'] == 'normal']))


if __name__ == "__main__":
    main()




# with open('/Users/danielmeint/Desktop/fullTrace.csv', 'rt') as f:
#     reader = csv.reader(f, delimiter=',')
#     next(reader) # skip the first row / header
#     for row in reader:
#         sourceID,sourceAddress,sourceType,sourceLocation,destinationServiceAddress,destinationServiceType,destinationLocation,accessedNodeAddress,accessedNodeType,operation,value,timestamp,normality = row
#         assert destinationServiceAddress == accessedNodeAddress[:len(destinationServiceAddress)]

#         sourceAgent = int(sourceAddress.split('/')[1][5:])
#         destAgent   = int(destinationServiceAddress.split('/')[1][5:])

#         sourceService = sourceID
#         destService   = destinationServiceAddress.split('/')[2]

#         services.add(sourceService)
#         services.add(destService)

#         agents.add(sourceAgent)
#         agents.add(destAgent)

#         if sourceAgent != destAgent:
#             edge = (sourceAgent, destAgent) if sourceAgent < destAgent else (destAgent, sourceAgent)
#             edges.add(edge)
        
#         if sourceService == 'tempin3' and operation.strip() == 'write':
#             timestamp = int(timestamp)
#             sinceLastWrite = timestamp - lastWrite
#             if sinceLastWrite < timestamp: # ignore first
#                 tempin3interUpdateTimes.append(sinceLastWrite)
            

#             # update timestamp for the last write
#             lastWrite = timestamp

#         # if destService == 'tempin3' and operation.strip() == 'read':
#             # print('read from', sourceService, ', value: ', value)

#         # if operation.strip() == 'read' and sourceAddress != destinationServiceAddress:
#         #     sourceAgent = int(sourceAddress.split('/')[1][5:])
#         #     destAgent   = int(destinationServiceAddress.split('/')[1][5:])
#         #     if sourceAgent != destAgent:
#         #         res.append([sourceAgent, destAgent])


# # print(len(agents), len(services))

# print(services)

# # fig1, ax1 = plt.subplots()
# # ax1.set_title('Time between updates for a temperature sensor in ms')
# # ax1.boxplot(tempin3interUpdateTimes, showfliers=False)
# # plt.xticks([1], ['tempin3'])

# # plt.show()

# # graph = [(n1, n2) for n1, n2 in edges if n1 >= 20 and n2 >= 20]
# # draw_graph(graph)