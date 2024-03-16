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

        # Only workers send JOINs
        elif requestCommand == 'JOIN':
            self.handle_join(requestNodeId, address)

        # Only request clients send JOBs
        elif requestCommand == 'JOB':
            self.handle_job(requestNodeId, address, payload)
        
        # Only workers send statuses
        elif requestCommand == 'IDLE' or requestCommand == 'BUSY':
            return requestCommand
        
        # Only workers send ACK_JOBs
        elif requestCommand == 'ACK_JOB':
            logging.info('Job accepted by %s %s', requestNodeId, self.workerNodes[requestNodeId])

        # Worker has cracked the hash
        elif requestCommand == 'RESULT':
            logging.info('Job result: %s', payload)
            self.result = payload

        # Worker has failed to crack the hash
        elif requestCommand == 'FAIL':
            logging.info(f'Job result: {requestCommand}')
            self.result = requestCommand

    # Send a response
    def handle_response(self, data, address):
        logging.info('Sending message: %s to %s', data.decode(), address)
        self.serverSocket.sendto(data, address)

    # Handle PING requests
    def handle_ping(self, requestNodeId, address):
        # Check if client pinging is in dict
        if requestNodeId not in self.requestClients:
            # Generate new ID for client
            requestNodeId = random.randbytes(4).hex()
            # Add client to dict
            self.requestClients[requestNodeId] = address
            logging.info('Client %s %s joined', requestNodeId, address)
        # Check if JOB is finished
        if self.result:
            # Failed to crack hash
            if self.result == 'FAIL':
                # Send result to client
                self.handle_response(f'{requestNodeId}:FAIL:'.encode(), address)
            # Succeeded in cracking hash
            else:
                # Send result to client
                self.handle_response(f'{requestNodeId}:RESULT:{self.result}'.encode(), address)
            # Remove client from dict once job is finished
            del self.requestClients[requestNodeId]
            # Reset result
            self.result = None
        # No result/no job active, send PONG to acknowledge
        else:
            # Send a response with the node ID and PONG 
            self.handle_response(f'{requestNodeId}:PONG:'.encode(), address)

    # Handle JOIN requests
    def handle_join(self, requestNodeId, address):
        # Check if worker joining is in dict
        if requestNodeId not in self.workerNodes:
            # Generate now ID for worker
            requestNodeId = random.randbytes(4).hex()
            # Add worker to dict
            self.workerNodes[requestNodeId] = address
            logging.info('Node %s %s joined', requestNodeId, address)
        # Send a response with the node ID and ACK
        self.handle_response(f'{requestNodeId}:ACK:'.encode(), address)

    # Handle JOB requests
    def handle_job(self, requestNodeId, address, payload):
        # Check if any workers have joined
        if len(self.workerNodes) > 0:
            # Find available workers
            for nodeId, nodeAddress in self.workerNodes.items():
                # PING the worker node to get its status
                self.handle_response(f'{nodeId}:PING:'.encode(), nodeAddress)
                # Receive response
                data, nodeAddress = self.serverSocket.recvfrom(1024)
                # Check if worker is available (IDLE or BUSY)
                if self.handle_request(data, nodeAddress) == 'IDLE':
                    # Send the job to the worker
                    logging.info(f'Sending job to: {nodeId} {nodeAddress}')
                    self.handle_response(f'{nodeId}:JOB:{payload}'.encode(), nodeAddress)
                    # Receive acknowledgment for the job
                    data, nodeAddress = self.serverSocket.recvfrom(1024)
                    # Handle request
                    self.handle_request(data, nodeAddress)
                # Wait before sending next request
                time.sleep(1)
            # Inform the client that the job was received
            self.handle_response(f'{requestNodeId}:ACK_JOB:'.encode(), address)
        # No workers have joined
        else:
            # Inform the client that no workers have joined, unable to fulfill request
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
