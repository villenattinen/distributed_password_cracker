import logging
import random
import socket
import sys
import time

class Server:
    workerNodes = {}
    requestClients = {}
    commandResponsePairs = {
        'PING': 'PONG',
        'JOB': 'JOB',
        'ACK_JOB': 'ACK_JOB'
    }

    # Initialize the server class
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    def add_node(self, address):
        nodeId = random.randbytes(4).hex()
        self.workerNodes[nodeId] = address
        return nodeId

    # Handle incoming requests
    def handle_request(self, data, address):
        print('Received:', data.decode(), 'from', address)
        logging.info('Received: %s from %s', data.decode(), address)
        requestNodeId, requestCommand = data.decode().split(':')        
        if requestCommand == 'PING':
            if requestNodeId not in self.requestClients:
                nodeId = self.add_node(address)
                logging.info('Client %s joined', nodeId)
            self.handle_response(f'{nodeId}:PONG'.encode(), address)
        elif requestCommand == 'JOIN':
            if requestNodeId not in self.workerNodes:
                nodeId = self.add_node(address)
                logging.info('Node %s %s joined', nodeId, address)
            self.handle_response(f'{nodeId}:ACK'.encode(), address)
        else:
            pass

    # Send a response
    def handle_response(self, data, address):
        logging.info('Sending message: %s to %s', data.decode(), address)
        self.serverSocket.sendto(data, address)

    # Run the server
    def run(self):
        logging.info('Server running')
        while True:
            print('Waiting for a message...')
            data, address = self.serverSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        filename='server.log',
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logging.info('Launching server...')

    # Start the server
    server = Server('localhost', 9090) #sys.argv[1], sys.argv[2]) # 
    server.run()
