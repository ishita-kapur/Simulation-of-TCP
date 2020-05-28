###
#   Ishita Kapur, UTA ID : 1001753123
#   CSE 5344, Fall 2019
#   
#   mission_tcp.py - This script is developed for multithreaded server creation, server implementation, request handling, threading routers
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
import functionalities
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler

# Map of the Mission in dictionary format
mission_map = {
    'A': {'B': 4, 'C': 3, 'E': 7},
    'B': {'A': 4, 'C': 6, 'L': 5},
    'C': {'A': 3, 'B': 6, 'D': 11},
    'D': {'C': 11, 'L': 9, 'F': 6, 'G': 10},
    'E': {'A': 7, 'G': 5},
    'F': {'L': 5, 'D': 6},
    'G': {'E': 5, 'D': 10},
    'L': {'B': 5, 'D': 9, 'F': 5}
}

# Dijkstras Algorithm for Calculating the shortest path between two agents (Ann-Jan, Jan-Chan, Ann-Chan)
pathAnnToJan = functionalities.Dijkstras(mission_map, 'F', 'A', visited=[], distances={}, predecessors={})
pathAnnToJan.insert(0, 'Ann')
pathAnnToJan.append('Jan')
pathJanToAnn = pathAnnToJan[::-1]
print("Shortest path from Ann to Jan is : " + str(pathAnnToJan))
print("Shortest path from Jan to Ann is : "+ str(pathJanToAnn) + "\n\n")
pathJanToChan = functionalities.Dijkstras(mission_map, 'E', 'F', visited=[], distances={}, predecessors={})
pathJanToChan.insert(0, 'Jan')
pathJanToChan.append('Chan')
pathChanToJan = pathJanToChan[::-1]
print("Shortest path from Jan to Chan is : "+ str(pathJanToChan))
print("Shortest path from Chan to Jan is : "+ str(pathChanToJan)+ "\n\n")
pathAnnToChan = functionalities.Dijkstras(mission_map, 'E', 'A', visited=[], distances={}, predecessors={})
pathAnnToChan.insert(0, 'Ann')
pathAnnToChan.append('Chan')
pathChanToAnn = pathAnnToChan[::-1]
print("Shortest path from Ann to Chan is : " + str(pathAnnToChan))
print("Shortest path from Chan to Ann is : " + str(pathChanToAnn)+ "\n\n")

pathToAirForceJanLogFile = './Logs/AirForceJanLogFile.txt'
# All ports need to be under localhost IP
localHost = functionalities.localHost

# Multithreaded TCP Server
class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """
        Handle requests in a separate thread
    """
    
# Request handler for the server portion of the routers
def TCPHandler(routerName):
    class RequestHandler(BaseRequestHandler):
        
        def handle(self):
            """
                Function for Request Handling
            """
            
            # self.request is the TCP socket connected to the client
            packetOnTheWay = self.request.recv(4096)
            packet = pickle.loads(packetOnTheWay)
            print('Router ' + routerName + ' :\n' + str(packet) + '\n')
            sourceID = packet.get('Source ID')
            destinationID = packet.get('Destination ID')
            # Ann to Jan packet forwarding
            if sourceID == functionalities.namesAndPorts.get('Ann') \
                            and destinationID == functionalities.namesAndPorts.get('Jan'):
                functionalities.PassPacket(pathAnnToJan, routerName, packetOnTheWay)
            # Jan to the Airforce packet forwarding
            elif sourceID == functionalities.namesAndPorts.get('Jan') \
                            and destinationID == functionalities.namesAndPorts.get('H'):
                sourceID = functionalities.namesAndPorts.get('H')
                destinationID = functionalities.namesAndPorts.get('Jan')                     # The destination of the packet about to be sent is where the original packet came from
                sequenceNumber = random.randint(10000, 99999)                                # First time talking to Jan, create new sequence number, Next byte of data that you want
                acknowledgementNumber = packet.get('Sequence Number')+ len(packet.get('Data'))    
                packetData = 'Success!'                                                      # Second step of three way handshake, therefore no data
                urgentPointer = 0                                                            # Not urgent as this is connection setup
                synBit = 0                                                                   # Syn bit is zero
                finBit = 0                                                                   # Trying to finish connection
                rstBit = 0                                                                   # Not trying to reset connection, therefore 0
                terBit = 0                                                                   # Not trying to terminate connection, therefore 0
                # Create packet
                responsePacket = functionalities.CreateTCPPacket(sourceID, destinationID, \
                                                    acknowledgementNumber, sequenceNumber, \
                                                    packetData, urgentPointer, synBit, \
                                                    finBit, rstBit, terBit)
                # Send packet
                functionalities.SerializeAndSendPacket(responsePacket, destinationID)
                # Logging Information
                timeStamp = time.time()
                data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
                data = data + 'Received following line.\n'
                data = data + packet.get('Data')
                data = data + 'Acknowledgement sent along with below line.\n'
                data = data + packetData + '\n\n'
                functionalities.WriteToLogFile(pathToAirForceJanLogFile, 'w', data)
                print('Airforce to Jan -> Success!')            
            # Jan to Ann packet forwarding
            elif sourceID == functionalities.namesAndPorts.get('Jan') \
                            and destinationID == functionalities.namesAndPorts.get('Ann'):    
                functionalities.PassPacket(pathJanToAnn, routerName, packetOnTheWay)
            # Jan to Chan packet forwarding
            elif sourceID == functionalities.namesAndPorts.get('Jan') \
                            and destinationID == functionalities.namesAndPorts.get('Chan'):    
                functionalities.PassPacket(pathJanToChan, routerName, packetOnTheWay)
            # Chan to Jan packet forwarding
            elif sourceID == functionalities.namesAndPorts.get('Chan') \
                            and destinationID == functionalities.namesAndPorts.get('Jan'):    
                functionalities.PassPacket(pathChanToJan, routerName, packetOnTheWay)
            # Ann to Chan packet forwarding
            elif sourceID == functionalities.namesAndPorts.get('Ann') \
                            and destinationID == functionalities.namesAndPorts.get('Chan'):    
                functionalities.PassPacket(pathAnnToChan, routerName, packetOnTheWay)
            # Jan to Ann packet forwarding
            elif sourceID == functionalities.namesAndPorts.get('Chan') \
                            and destinationID == functionalities.namesAndPorts.get('Ann'):    
                functionalities.PassPacket(pathChanToAnn, routerName, packetOnTheWay)
            # Incorrect direction of the packet
            else:
                print('Incorrect direction of the packet' + '\n\n')
            return
    return RequestHandler

def ThreadRouter (exitEvent, routerName):
    """
        Function for Threading Routers
    """
    try:
        RequestHandler = TCPHandler(routerName)
        server = ThreadedTCPServer((localHost, functionalities.namesAndPorts.get(routerName)), RequestHandler)
        server.timeout = 0.01           # Make sure not to wait too long when serving requests
        server.daemon_threads = True    # So that handle_request thread exits when current thread exits
        # Poll so that you see the signal to exit as opposed to calling server_forever
        while not exitEvent.isSet():
            server.handle_request()     
        server.server_close()         
    except:
        print('Router ' + routerName + ' could not be created!')
    sys.exit()

if __name__ == '__main__':
    """
        Main Function
    """
    try:

        exitEvent = threading.Event() # Set this upon keyboard interrupt to let the threads know they have to exit
        exitEvent.clear()             # Make sure the event is clear initially
        # Thread as many as the number of routers
        A = threading.Thread(target=ThreadRouter, args=(exitEvent, 'A'))
        B = threading.Thread(target=ThreadRouter, args=(exitEvent, 'B'))
        C = threading.Thread(target=ThreadRouter, args=(exitEvent, 'C'))
        D = threading.Thread(target=ThreadRouter, args=(exitEvent, 'D'))
        E = threading.Thread(target=ThreadRouter, args=(exitEvent, 'E'))
        F = threading.Thread(target=ThreadRouter, args=(exitEvent, 'F'))
        G = threading.Thread(target=ThreadRouter, args=(exitEvent, 'G'))
        L = threading.Thread(target=ThreadRouter, args=(exitEvent, 'L'))
        H = threading.Thread(target=ThreadRouter, args=(exitEvent, 'H'))
        # Start the routers
        A.start()
        B.start()
        C.start()
        D.start()
        E.start()
        F.start()
        G.start()
        L.start()
        H.start()
    except:
        print ("ERROR: Routers could not be started")
    
    try:
        # Run till keyboard interrupt is encountered
        while True:
            pass
    except KeyboardInterrupt:
        exitEvent.set()  # When keyboard interrupt is encountered, notify threads to exit
        # Wait for all routers to finish
        A.join()
        B.join()
        C.join()
        D.join()
        E.join()
        F.join()
        G.join()
        L.join() 
        H.join()
                
        sys.exit()
