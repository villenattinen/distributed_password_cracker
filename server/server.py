import logging
import random
import socket
import sys
import time

class Server:
    workerNodes = {}
    requestClients = {}
    result = None

    # Initialize the server class
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    # Handle incoming requests
    def handle_request(self, data, address):
        print('Received:', data.decode(), 'from', address)
        logging.info('Received: %s from %s', data.decode(), address)
        requestNodeId, requestCommand, payload = data.decode().split(':')

        # Check the request type

        # Only request clients send PINGs    
        if requestCommand == 'PING':
            self.handle_ping(requestNodeId, address)

        # Only worker nodes send JOINs
        elif requestCommand == 'JOIN':
            self.handle_join(requestNodeId, address)

        # Only request clients send JOBs
        elif requestCommand == 'JOB':
            self.handle_job(requestNodeId, address, payload)
        
        # Only worker nodes send statuses
        elif requestCommand == 'IDLE' or requestCommand == 'BUSY':
            return requestCommand
        
        # Only worker nodes send ACK_JOBs
        elif requestCommand == 'ACK_JOB':
            logging.info('Job accepted by %s %s', requestNodeId, self.workerNodes[requestNodeId])

        elif requestCommand == 'RESULT':
            logging.info('Job result: %s', payload)
            self.result = payload

        elif requestCommand == 'FAIL':
            logging.info(f'Job result: {requestCommand}')
            self.result = requestCommand

    # Send a response
    def handle_response(self, data, address):
        logging.info('Sending message: %s to %s', data.decode(), address)
        self.serverSocket.sendto(data, address)

    # Handle PING requests
    def handle_ping(self, requestNodeId, address):
        # Check if a familiar client is pinging
        if requestNodeId not in self.requestClients:
            requestNodeId = random.randbytes(4).hex()
            self.requestClients[requestNodeId] = address
            logging.info('Client %s %s joined', requestNodeId, address)
        if self.result:
            if self.result == 'FAIL':
                self.handle_response(f'{requestNodeId}:FAIL:'.encode(), address)
            else:
                self.handle_response(f'{requestNodeId}:RESULT:{self.result}'.encode(), address)
            
            # Remove client from dict once job is finished
            del self.requestClients[requestNodeId]
            # Reset result
            self.result = None
        else:
            # Send a response with the node ID and PONG 
            self.handle_response(f'{requestNodeId}:PONG:'.encode(), address)

    # Handle JOIN requests
    def handle_join(self, requestNodeId, address):
        if requestNodeId not in self.workerNodes:
            requestNodeId = random.randbytes(4).hex()
            self.workerNodes[requestNodeId] = address
            logging.info('Node %s %s joined', requestNodeId, address)
        # Send a response with the node ID and ACK
        self.handle_response(f'{requestNodeId}:ACK:'.encode(), address)

    # Handle JOB requests
    def handle_job(self, requestNodeId, address, payload):
        # Check if there are any available workers
        if len(self.workerNodes) > 0:
            # PING the worker nodes in order to find an available worker
            for nodeId, nodeAddress in self.workerNodes.items():
                self.handle_response(f'{nodeId}:PING:'.encode(), nodeAddress)
                data, nodeAddress = self.serverSocket.recvfrom(1024)
                if self.handle_request(data, nodeAddress) == 'IDLE':
                    logging.info(f'Sending job to: {nodeId} {nodeAddress}')
                    self.handle_response(f'{nodeId}:JOB:{payload}'.encode(), nodeAddress)
                    data, nodeAddress = self.serverSocket.recvfrom(1024)
                    self.handle_request(data, nodeAddress)
                time.sleep(1)
            self.handle_response(f'{requestNodeId}:ACK_JOB:'.encode(), address)
        else:
            logging.warning('No workers joined')
            self.handle_response(f'{requestNodeId}:ERROR:No available workers'.encode(), address)

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
