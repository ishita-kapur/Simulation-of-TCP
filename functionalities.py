###
#   Ishita Kapur, UTA ID : 1001753123
#   CSE 5344, Fall 2019
#   
#   functionalities.py - Dependent functions which are being called from the other scripts
#   
#   References:
#               http://www.gilles-bertrand.com/2014/03/dijkstra-algorithm-python-example-source-code-shortest-path.html - for Dijkstras Algorithm (shortest path between two nodes)
#               https://stackoverflow.com/questions/1767910/checksum-udp-calculation-python - for Checksum computation
#               https://docs.python.org/3/library/pickle.html - for Python object serialization
#               https://stackoverflow.com/questions/24423162/how-to-send-an-array-over-a-socket-in-python - for Serialization
#               https://github.com/cdk1220/Computer-Networks-CSE-4344-Project-3-Simulation-of-TCP - as a Reference
#               https://github.com/SanyTiger/tcp-simulator-master - as a Reference
#               http://www.bitforestinfo.com/2018/01/python-codes-to-calculate-tcp-checksum.html - for Checksum calculation
###

import sys
import time
import socket
import pickle
import datetime
import random
import threading

# localhost IP address
localHost = "127.0.0.1"
# Router Names and Port Numbers
namesAndPorts = {'A': 8000, 'B': 8001, 'C': 8002, 'D': 8003, 'E': 8004, \
                'F': 8005, 'G': 8006, 'L': 8007, 'H': 8008, 'Ann': 1111, \
                'Jan': 1100, 'Chan': 1101}

def Dijkstras(graph, src, dest, visited=[], distances={}, predecessors={}):
    """
        Function for Dijkstras Algorithm - shortest path between two agents
    """
    
    # Verify if source and destination are a part of the graph
    if src not in graph:
        raise TypeError('The root of the shortest path tree cannot be found')
    if dest not in graph:
        raise TypeError('The target of the shortest path cannot be found')    
    if src == dest:
        # Compute shortest path
        path = []
        pred = dest
        while pred != None:
            path.append(pred)
            pred = predecessors.get(pred, None)
        return path
    else :     
        # If it is the initial run, initializes the cost
        if not visited: 
            distances[src] = 0
        # Visit the neighbors
        for neighbor in graph[src] :
            # Visit them if they are not visited
            if neighbor not in visited:
                # Update if new distance is less than current distance
                new_distance = distances[src] + graph[src][neighbor]
                if new_distance < distances.get(neighbor,float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = src
        # Mark as visited
        visited.append(src)
        # now that all neighbors have been visited: recurse                         
        # select the non visited node with lowest distance 'x'
        # run Dijskstra with src='x'
        unvisited={}
        for k in graph:
            if k not in visited:
                unvisited[k] = distances.get(k, float('inf'))        
        x = min(unvisited, key = unvisited.get)
        path = Dijkstras(graph, x, dest, visited, distances, predecessors)
        return path

def CreateTCPPacket(sourceID, destinationID, acknowledgementNumber, sequenceNumber,\
                            data, urgentPointer, synBit, finBit, rstBit, terBit):
    """
        Function for creating the TCP Packet and calculating the header length
    """
    
    packet = {}
    # Compute checksum
    checksum = Checksum(data)
    # Urgent Pointer for urgent data if needs to be sent
    urgentPointer = urgentPointer
    # Header length of the packet
    headerLength = len(str(sourceID)) + len(str(destinationID)) + len(str(acknowledgementNumber)) \
                            + len(str(sequenceNumber)) + len(str(urgentPointer)) \
                            + len(str(synBit)) + len(str(finBit)) + len(str(rstBit)) \
                            + len(str(terBit))                   
    # Append all the fields to the Packet dictionary 
    packet.update({'Source ID': sourceID})
    packet.update({'Destination ID': destinationID})
    packet.update({'Sequence Number': sequenceNumber})
    packet.update({'Acknowledgement Number': acknowledgementNumber})
    packet.update({'Data': data})
    packet.update({'Checksum': checksum})
    packet.update({'Urgent Pointer': urgentPointer})
    packet.update({'Syn Bit': synBit})
    packet.update({'Fin Bit': finBit})
    packet.update({'Rst Bit': rstBit})
    packet.update({'Ter Bit': terBit})
    packet.update({'Header Length': headerLength})
    return packet

def SerializeAndSendPacket(responsePacket, portTalkingTo):
    """
        Function for Python object serialization of the packet and sending the packet
    """

    responsePacketEncoded = pickle.dumps(responsePacket) #Byte object            
    # Sending Byte object
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((localHost, portTalkingTo))
        sock.sendall(responsePacketEncoded)
    finally:
        sock.close()

def PassPacket(shortestPath, routerName, packetOnTheWay):
    """
        Function for forwarding the packet to the next node
    """
    
    # Finding the next node from the current node
    nextRouterIndex = shortestPath.index(routerName) + 1
    if nextRouterIndex < len(shortestPath):
        nextRouterName = shortestPath[nextRouterIndex]
        nextRouterPort = namesAndPorts.get(nextRouterName)  
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((localHost, nextRouterPort))
            sock.sendall(packetOnTheWay)
        except ConnectionRefusedError:
            print('Router ' + nextRouterName + ' is offline.')
        finally:
            sock.close()

def Checksum(msg):
    """
        Function for Computing Checksum
    """

    s = 0
    for i in range(0, len(msg), 2):
        try:
            w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        except IndexError:
            w = ord(msg[i]) + (0 << 8)
        s = CarryAroundAdd(s, w)
    return ~s & 0xffff

def CarryAroundAdd(a, b):
    """
        Function for Checksum extra bit addition
    """
    
    c = a + b
    return (c & 0xffff) + (c >> 16)

def ReadFile(path):
    """
        Function for reading a file and returning contents
    """
    
    with open(path, 'r') as file:
        content = file.readlines()
    return content

def WriteToLogFile(path, mode, data):
    """
        Function for writing to the log file
    """
    
    with open(path, mode) as file:
        file.write(data)

def GetKeyFromValue(value):
    """
        Function for retreiving key for a given value in the dictionary
    """
    
    for key in namesAndPorts:
        if namesAndPorts.get(key) == value:
            return key





   

