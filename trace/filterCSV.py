# bei jedem write wird ein update ausgeführt, d.h. neue Version der destServiceAddress

# unter 'normalen' request gibt es nur writes zur eigenen Adresse (sourceAddress == destinationServiceAddress) oder an den destinationServiceType == batteryService, v.a. an washing machines (?)

# washingmachine3,/agent14/washingmachine3,/washingService,Showerroom,/agent12/battery5,/batteryService,Entrance,/agent12/battery5/charge,/basic/number,write,9,1520032100782,normal

# subscribe operations von questioningservices, i.e. smartphones NUR AN SICH SELBST

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

trace = []

lastWrite = 0
tempin3interUpdateTimes = []

def setup():
    with open('trace/fullTrace.csv', 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader) # skip the first row / header
        for row in reader:
            sourceID,sourceAddress,sourceType,sourceLocation,destinationServiceAddress,destinationServiceType,destinationLocation,accessedNodeAddress,accessedNodeType,operation,value,timestamp,normality = row
            trace.append({
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
    normalRequests = [request for request in trace if request['normality'] == 'normal']
    updates = [r for r in normalRequests if r['sourceID'] == sensor and r['operation'] == 'write']
    interarrivaltimes = [int(updates[i]['timestamp']) - int(updates[i-1]['timestamp']) for i in range(1, len(updates))]
    
    print(plt.subplots())

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
    return [r for r in trace if r['normality'] == 'normal']

# def main():
#     setup()
#     normalRequests = getNormalRequests(trace)
#     agents = set(['agent1', 'agent2', 'agent3', 'agent4', 'agent5', 'agent6'])
#     requests = []
#     for r in normalRequests:
#         srcAgent = r['sourceAddress'].split('/')[1]
#         dstAgent = r['destinationServiceAddress'].split('/')[1].strip()
#         srcId    = r['sourceID']
#         dstId    = r['destinationServiceAddress'].split('/')[2].strip()
#         time     = r['timestamp']
#         op       = r['operation']
#         normal   = True if r['normality'] == 'normal' else False

#         if normal and srcAgent in agents and dstAgent in agents and op in ['read', 'write']:
#             requests.append({
#                 'srcAgent': srcAgent,
#                 'srcId'   : srcId,
#                 'dstAgent': dstAgent,
#                 'dstId'   : dstId,
#                 'time'    : time,
#                 'op'      : op
#             })
    
#     # keys = requests[0].keys()
#     # print(keys)
#     # with open('trace/subTrace2.csv', 'w') as output_file:
#     #     dict_writer = csv.DictWriter(output_file, keys)
#     #     dict_writer.writeheader()
#     #     dict_writer.writerows(requests)
    

#     # edges = getEdges(getNormalRequests(trace))
#     # print(edges)
#     # draw_graph(edges)
#     # print(getRooms([r for r in trace if r['normality'] == 'normal']))

def read_csv(path):
    res = []
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            res.append(row)
    return res

def write_dict_array_to_csv(path, dict_array):
    keys = dict_array[0].keys()
    with open(path, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict_array)

def plot_temp_sensor_updates():
    trace = read_csv('trace/subTrace.csv')

    sensors = [f'tempin{id}' for id in range(1, 7)]
    updates = [
        [
            request for request in trace if request['srcId'] == sensor and request['op'] == 'write'
        ] for sensor in sensors
    ]
    interarrivaltimes = [
        [
            int(row[i]['time']) - int(row[i-1]['time']) for i in range(1, len(row))
        ] for row in updates
    ]

    fig, ax = plt.subplots()
    # ax.set_title('Time between updates for temperature sensors in ms')
    ax.boxplot(interarrivaltimes, showfliers=False)
    plt.xticks([1, 2, 3, 4, 5, 6], ['tempin1', 'tempin2', 'tempin3', 'tempin4', 'tempin5', 'tempin6'])
    plt.show()

def boxplot(data):
    fig, ax = plt.subplots()
    ax.boxplot(data, showfliers=True)
    plt.xticks([1], ['movement1/movement'])
    plt.show()

def main():
    trace = read_csv('trace/subTrace2.csv')
    objects = set([r['accessedNodeAddress'] for r in trace])
    print(objects)
    print(len(objects))
    # print(len([r for r in trace if r['operation'] == 'read']))

    # contents = set([f"{r['accessedNodeAddress']}/v{r['version']}" for r in trace])
    # subtracereads = [r for r in trace if r['operation'] == 'read']
    # write_dict_array_to_csv('trace/subtrace_reads.csv', subtracereads)


    # trace = read_csv('trace/fullTrace.csv')
    # agents = set(['agent1', 'agent2', 'agent3', 'agent4', 'agent5', 'agent6'])
    # nodes = set(['/agent6/lightcontrol6/lightOn', '/agent2/tempin2', '/agent5/lightcontrol5/lightOn', '/agent3/heatingcontrol1/heatingOn', '/agent6/washingmachine1/washing', '/agent5/battery1/charge', '/agent3/doorlock1/open', '/agent3/movement3/lastChange', '/agent4/battery3/charge', '/agent3/heatingcontrol1', '/agent3/tempin3', '/agent3/lightcontrol3/lightOn', '/agent5/movement5/movement', '/agent5/tempin5', '/agent6/movement6/movement', '/agent6/movement6/lastChange', '/agent1/tempin1', '/agent5/battery2/charge', '/agent5/movement5/lastChange', '/agent3/movement3/movement', '/agent2/movement2/movement', '/agent2/movement2/lastChange', '/agent6/tempin6', '/agent4/movement4/lastChange', '/agent4/movement4/movement', '/agent1/movement1/lastChange', '/agent4/battery3/charging', '/agent5/battery2/charging', '/agent2/lightcontrol2/lightOn', '/agent1/lightcontrol1/lightOn', '/agent4/lightcontrol4/lightOn', '/agent1/movement1/movement', '/agent4/tempin4', '/agent5/battery1/charging'])
    # version = { node : 0 for node in nodes}
    # sub_trace = []
    # for r in trace:
    #     srcAgent = r['sourceAddress'].split('/')[1]
    #     dstAgent = r['destinationServiceAddress'].split('/')[1].strip()
    #     accessedNode = r['accessedNodeAddress']

    #     assert dstAgent == accessedNode.split('/')[1].strip()
    #     normal = r['normality'] == 'normal'
    #     operation = r['operation']
    #     if normal and srcAgent in agents and dstAgent in agents and operation in ['read', 'write']:
    #         if operation == 'write':
    #             version[accessedNode] += 1
    #         r.update({'version': version[accessedNode]})
    #         sub_trace.append(r)
    # write_dict_array_to_csv('trace/subTrace2.csv', sub_trace)





    # tempin1_updates = [r for r in trace if r['accessedNodeAddress'] == '/agent1/tempin1' and r['operation'] == 'write' and r['normality'] == 'normal']
    # interarrivaltimes = [int(tempin1_updates[i]['timestamp']) - int(tempin1_updates[i-1]['timestamp']) for i in range(1, len(tempin1_updates))]
    # print(np.mean(interarrivaltimes), np.median(interarrivaltimes), np.var(interarrivaltimes))

    # movement1_updates = [r for r in trace if r['accessedNodeAddress'] == '/agent1/movement1/movement' and r['operation'] == 'write' and r['normality'] == 'normal']
    # interarrivaltimes = [int(movement1_updates[i]['timestamp']) - int(movement1_updates[i-1]['timestamp']) for i in range(1, len(movement1_updates))]
    # print(len(interarrivaltimes), np.mean(interarrivaltimes), np.median(interarrivaltimes), np.var(interarrivaltimes))
    # boxplot(interarrivaltimes)

    # updates = [r for r in normalRequests if r['sourceID'] == sensor and r['operation'] == 'write']
    # interarrivaltimes = [int(updates[i]['timestamp']) - int(updates[i-1]['timestamp']) for i in range(1, len(updates))]
    
    # print(plt.subplots())

    # fig1, ax1 = plt.subplots()
    # ax1.set_title('Time between updates for a temperature sensor in ms')
    # ax1.boxplot(interarrivaltimes, showfliers=False)
    # plt.xticks([1], [sensor])

    # plt.show()



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