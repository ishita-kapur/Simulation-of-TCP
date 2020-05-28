###
#   Ishita Kapur, UTA ID : 1001753123
#   CSE 5344, Fall 2019
#   
#   chan.py - python script for Agent Chan's functionalities
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

# All ports need to be under localhost IP
localHost = functionalities.localHost
# Chan listens to Port Number
portListeningTo = functionalities.namesAndPorts.get('Chan')
# Dumping messages to the immediately connected router
portTalkingTo = functionalities.namesAndPorts.get('E')
# Conversation files path
pathToChanToJanFile = './Conversations/Chan/Chan-_Jan.txt'
pathToChanToAnnFile = './Conversations/Chan/Chan-_Ann.txt'
# Log File paths
pathToChanJanLogFile = './Logs/Chan/ChanJanLog.txt'
pathToChanAnnLogFile = './Logs/Chan/ChanAnnLog.txt'
# Clear old logs before session start
functionalities.WriteToLogFile(pathToChanJanLogFile, 'w', '')
functionalities.WriteToLogFile(pathToChanAnnLogFile, 'w', '')
# Reading content of the conversations
contentChanToJan = functionalities.ReadFile(pathToChanToJanFile)
contentChanToAnn = functionalities.ReadFile(pathToChanToAnnFile)

# Set this upon keyboard interrupt to let the threads know they have to exit
exitEvent = threading.Event() 

# Multithreaded Server
class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """
        Handle requests in a separate thread
    """
    
# Request handler for the server portion of the agents
class TCPRequestHandler(BaseRequestHandler):
    def handle(self):
        """
            Function for Request Handling
        """
        
        # self.request is the TCP socket connected to the client
        incomingPacket = self.request.recv(4096)
        incomingPacketDecoded = pickle.loads(incomingPacket)        
        receivedFrom = functionalities.GetKeyFromValue(incomingPacketDecoded.get('Source ID'))
        if incomingPacketDecoded.get('Ter Bit') == 1:
            print('Ann has ordered the termination of the connection.\n')
            exitEvent.set()
        # When someone else is trying to setup connection with us
        elif incomingPacketDecoded.get('Syn Bit') == 1 and \
                            incomingPacketDecoded.get('Acknowledgement Number') == -1:            
            # Send TCP packet with syn bit still one and acknowledgement number as 1 + sequence number. Also, create your own sequence number
            sourceID = portListeningTo                                                   # The port listening to
            destinationID = incomingPacketDecoded.get('Source ID')                       # The destination of the packet about to be sent is where the original packet came from
            sequenceNumber = random.randint(10000, 99999)                                # First time talking to client, create new sequence number
            acknowledgementNumber = incomingPacketDecoded.get('Sequence Number') + 1     # Client wanted to connect, therefore no data in the original packet, ack # will be one more than client seq #
            packetData = ''                                                              # Second step of three way handshake, therefore no data
            urgentPointer = 0                                                            # Not urgent as this is connection setup
            synBit = 1                                                                   # Syn bit has to be one for the second step of threeway handshake
            finBit = 0                                                                   # Not trying to finish connection, therefore 0                                               
            rstBit = 0                                                                   # Not trying to reset connection, therefore 0
            terBit = 0                                                                   # Not trying to terminate connection, therefore 0           
            # Create Packet
            responsePacket = functionalities.CreateTCPPacket(sourceID, destinationID, \
                                                acknowledgementNumber, sequenceNumber, \
                                                packetData, urgentPointer, synBit, \
                                                finBit, rstBit, terBit)            
            # Send packet
            functionalities.SerializeAndSendPacket(responsePacket, portTalkingTo)            
            # Logging Information
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'            
            if receivedFrom == 'Jan':
                data = data + 'Jan as a client attempted to connect. Sent packet with Syn Bit as 1, which is the second step of the threeway handshake.\n\n'
                functionalities.WriteToLogFile(pathToChanJanLogFile, 'a', data)
            elif receivedFrom == 'Ann':
                data = data + 'Ann as a client attempted to connect. Sent packet with Syn Bit as 1, which is the second step of the threeway handshake.\n\n'
                functionalities.WriteToLogFile(pathToChanAnnLogFile, 'a', data)                      
        # Your attempt to setup connection with someone else has been responded to
        elif incomingPacketDecoded.get('Syn Bit') == 1:
            # Start sending data here and raise the flag to wait for acknowledgement
            sourceID = portListeningTo                                                   # The port listening to
            destinationID = incomingPacketDecoded.get('Source ID')                       # The destination of the packet about to be sent is where the original packet came from
            sequenceNumber = incomingPacketDecoded.get('Acknowledgement Number')         # The  next byte you should be sending is the byte that the other party is expecting
            acknowledgementNumber = incomingPacketDecoded.get('Sequence Number') + 1     # Just one more than the sequence number
            urgentPointer = 0                                                            # Not urgent as this is connection setup
            synBit = 0                                                                   # Threeway handshake third step, no need of this bit
            finBit = 0                                                                   # Not trying to finish connection, therefore 0                                               
            rstBit = 0                                                                   # Not trying to reset connection, therefore 0
            terBit = 0                                                                   # Not trying to terminate connection, therefore 0
            # Populate data field depending on who the connection is being established with
            if receivedFrom == 'Jan':
                try:
                    packetData = contentChanToJan.pop(0)     # Get the first element from list and delete it from there
                except IndexError:
                    print('Chan-_Jan.txt is empty.\n\n')
            elif receivedFrom == 'Ann':
                try:
                    packetData = contentChanToAnn.pop(0)    # Get the first element from list and delete it from there
                except IndexError:
                    print('Chan-_Ann.txt is empty.\n\n')             
            # Create Packet
            responsePacket = functionalities.CreateTCPPacket(sourceID, destinationID, \
                                                acknowledgementNumber, sequenceNumber, \
                                                packetData, urgentPointer, synBit, \
                                                finBit, rstBit, terBit)            
            # Send packet
            functionalities.SerializeAndSendPacket(responsePacket, portTalkingTo)            
            # Logging Information
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'            
            if receivedFrom == 'Jan':
                data = data + 'Connection with Jan as the server is successful. This is the third step of the threeway handshake. First, which is below line was sent.\n'
                data = data + packetData + '\n\n'
                functionalities.WriteToLogFile(pathToChanJanLogFile, 'a', data)
            elif receivedFrom == 'Ann':
                data = data + 'Connection with Ann as the server is successful. This is the third step of the threeway handshake. First, which is below line was sent.\n'
                data = data + packetData + '\n\n'
                functionalities.WriteToLogFile(pathToChanAnnLogFile, 'a', data)                
        # Any other case, is receiving data
        else:
            # Send acknowledgement
            sourceID = portListeningTo                                            # The port listening to
            destinationID = incomingPacketDecoded.get('Source ID')                # The destination of the packet about to be sent is where the original packet came from
            sequenceNumber = incomingPacketDecoded.get('Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting                                                                                   
                                                                                  # Next byte of data that you want
            acknowledgementNumber = incomingPacketDecoded.get('Sequence Number') + len(incomingPacketDecoded.get('Data')) 
            urgentPointer = 0                                                     # Not urgent as this is connection setup
            synBit = 0                                                            # Syn bit has to be one for the second step of threeway handshake
            finBit = 0                                                            # Not trying to finish connection, therefore 0                                               
            rstBit = 0                                                            # Not trying to reset connection, therefore 0
            terBit = 0                                                            # Not trying to terminate connection, therefore 0
            # Populate data field depending on who the connection is being established with
            if receivedFrom == 'Jan':
                try:
                    packetData = contentChanToJan.pop(0)     # Get the first element from list and delete it from there
                except IndexError:
                    # Kick of connection tear down function here
                    pass
            elif receivedFrom == 'Ann':
                try:
                    packetData = contentChanToAnn.pop(0)    # Get the first element from list and delete it from there
                except IndexError:
                    # Kick of connection tear down function here
                    pass
            # Create Packet
            responsePacket = functionalities.CreateTCPPacket(sourceID, destinationID, \
                                                acknowledgementNumber, sequenceNumber, \
                                                packetData, urgentPointer, synBit, \
                                                finBit, rstBit, terBit)            
            # Send packet
            functionalities.SerializeAndSendPacket(responsePacket, portTalkingTo)            
            # Logging Information
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + incomingPacketDecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'
            if receivedFrom == 'Jan':
                functionalities.WriteToLogFile(pathToChanJanLogFile, 'a', data)
            elif receivedFrom == 'Ann':
                functionalities.WriteToLogFile(pathToChanAnnLogFile, 'a', data)
        return

def AgentServer ():
    """
        Function for creating server for an Agent
    """

    try:
        server = ThreadedTCPServer((localHost, portListeningTo), TCPRequestHandler)
       
        server.timeout = 0.01           # Make sure not to wait too long when serving requests
        server.daemon_threads = True    # So that handle_request thread exits when current thread exits

        # Poll so that you see the signal to exit as opposed to calling server_forever
        while not exitEvent.isSet():
            server.handle_request()   

        server.server_close()           
    except:
        print('Problem creating server for agent Chan.')

    sys.exit()


if __name__ == '__main__':
    """
        Main Function
    """

    try:
        # Make sure the event is clear initially
        exitEvent.clear()                            
        # Create a separate thread for Chan's server portion
        chanServer = threading.Thread(target=AgentServer, args=())       
        # Start the Chan's server
        chanServer.start()
        # Sleep to ensure that all agents are online
        time.sleep(10)
    except:
        print ("Couldn't create thread for Chan's router.")


    try:
        # Start connection setup with Jan
        sourceID = portListeningTo                                            # The port listening to
        destinationID = functionalities.namesAndPorts.get('Jan')              # Trying to setup connection with Jan, so send the packet to Jan
        sequenceNumber = random.randint(10000, 99999)                         # First time talking to Jan, create new sequence number
        acknowledgementNumber = -1                                            # Haven't recevied anything from Jan, therefore -1
        packetData = ''                                                       # Acknowledgment packets contain no data
        urgentPointer = 0                                                     # Not urgent as this is connection setup
        synBit = 1                                                            # Syn bit has to be one since this is connection setup
        finBit = 0                                                            # Not trying to finish connection, therefore 0                                               
        rstBit = 0                                                            # Not trying to reset connection, therefore 0
        terBit = 0                                                            # Not trying to terminate connection, therefore 0
        # Create Packet
        responsePacket = functionalities.CreateTCPPacket(sourceID, destinationID, \
                                            acknowledgementNumber, sequenceNumber, \
                                            packetData, urgentPointer, synBit, \
                                            finBit, rstBit, terBit)        
        # Send packet
        functionalities.SerializeAndSendPacket(responsePacket, portTalkingTo)
        # Logging Information
        timeStamp = time.time()
        data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        data = data + "Connection setup with Jan started. This is the first step of the threeway handshake.\n\n"
        functionalities.WriteToLogFile(pathToChanJanLogFile, 'a', data)
        # Run till connection teardown or termination
        while not exitEvent.isSet():
            pass        
        # Wait for Chan's server to finish
        chanServer.join()
                
        sys.exit()
    except KeyboardInterrupt:
        print('Keyboard interrupt\n')
        exitEvent.set()  # Upon catching keyboard interrupt, notify threads to exit
        
        # Wait for Jan's server to finish
        chanServer.join()
                
        sys.exit()
