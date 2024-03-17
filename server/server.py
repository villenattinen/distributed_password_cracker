import logging
import random
import socket
import sys
import time

class Server:
    # Dict of worker clients (node ID: address)
    workerNodes = {}
    # Dict of request clients (node ID: address)
    requestClients = {}
    # Dict of received jobs (job ID: result)
    jobs = {}
    # Dict of active workers (node ID: job ID)
    activeWorkers = {}

    # Initialize the server class
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    # Handle incoming requests
    def handle_request(self, data, address):
        print(f'Received: {data.decode()} from {address}')
        logging.info(f'Received: {data.decode()} from {address}')
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
            logging.info(f'Job accepted by {requestNodeId} {self.workerNodes[requestNodeId]}')

        # Worker has cracked the hash
        elif requestCommand == 'RESULT':
            jobId, result = payload.split('=')
            logging.info(f'Job result: {payload} from {requestNodeId} {self.workerNodes[requestNodeId]}')
            self.jobs[jobId] = result

            # Remove worker from list of active workers
            if requestNodeId in self.activeWorkers:
                del self.activeWorkers[requestNodeId]
            # Send abort commands to other still active workers
            self.handle_abort()
            # Clear the list of active workers
            # TODO: make sure workers ACK the abort command
            self.activeWorkers.clear()

        # Worker has failed to crack the hash
        elif requestCommand == 'FAIL':
            logging.info(f'Job result: {requestCommand} from {requestNodeId} {self.workerNodes[requestNodeId]}')

            # Make sure the worker is still in the list of active workers
            if requestNodeId in self.activeWorkers:
                # Remove worker from list of active workers
                del self.activeWorkers[requestNodeId]
            # If all workers for that job have finished and no result is found update job status to FAIL
            if payload not in self.activeWorkers.values():
                self.jobs[payload] = requestCommand

    # Send a response
    def handle_response(self, data, address):
        logging.info(f'Sending: {data.decode()} to {address}')
        print(f'Sending: {data.decode()} to {address}')
        self.serverSocket.sendto(data, address)

    # Handle PING requests
    def handle_ping(self, requestNodeId, address):
        # Default response is PONG
        responseCommand = 'PONG'
        # Default payload is empty
        payload = ''

        # Check if client pinging is in dict
        if requestNodeId not in self.requestClients:
            # Generate new ID for client
            requestNodeId = random.randbytes(4).hex()
            # Add client to dict
            self.requestClients[requestNodeId] = address
            logging.info(f'New client {requestNodeId} {address} joined')

        # Check if the client ID matches a job ID 
        if requestNodeId in self.jobs:
            # Check if a result is available
            if self.jobs[requestNodeId]:
                # Failed to crack hash
                if self.jobs[requestNodeId] == 'FAIL':
                    # Set result as FAIL
                    responseCommand = 'FAIL'
                # Succeeded in cracking hash
                else:
                    # Set result and the payload as the cracked hash
                    responseCommand = 'RESULT'
                    payload = self.jobs[requestNodeId]

                # Remove client from dict once job is finished
                del self.requestClients[requestNodeId]
                # Remove job from dict once job is finished
                del self.jobs[requestNodeId]
        
        # Send a response with the node ID, response command and possible payload
        self.handle_response(f'{requestNodeId}:{responseCommand}:{payload}'.encode(), address)

    # Handle JOIN requests
    def handle_join(self, requestNodeId, address):
        # Check if worker joining is in dict
        if requestNodeId not in self.workerNodes:
            # Generate now ID for worker
            requestNodeId = random.randbytes(4).hex()
            # Add worker to dict
            self.workerNodes[requestNodeId] = address
            logging.info(f'Node {requestNodeId} {address} joined')
        # Send a response with the node ID and ACK
        self.handle_response(f'{requestNodeId}:ACK:'.encode(), address)

    # Handle JOB requests
    def handle_job(self, requestNodeId, address, payload):
        # Check if any workers have joined
        if len(self.workerNodes) > 0:
            # Add job to dict, use the client's ID as job ID
            self.jobs[requestNodeId] = None
            logging.info(f'New job added to queue: {requestNodeId}, {payload}')

            # Find available workers
            for nodeId, nodeAddress in self.workerNodes.items():
                # PING the worker node to get its status
                self.handle_response(f'{nodeId}:PING:'.encode(), nodeAddress)
                # Receive response
                try:
                    data, nodeAddress = self.serverSocket.recvfrom(1024)
                except Exception as e:
                    logging.warning(f'Worker {nodeId} {nodeAddress} not responding')
                    logging.info(f'Removing worker {nodeId} {nodeAddress} from list of available workers')
                    del self.workerNodes[nodeId]
                    continue
                # Check if worker is available (IDLE or BUSY)
                if self.handle_request(data, nodeAddress) == 'IDLE':
                    # Add worker to dict of available workers, set value as Job ID
                    self.activeWorkers[nodeId] = requestNodeId
                # Wait before sending next request
                time.sleep(1)
            # Inform the client that the job was received
            self.handle_response(f'{requestNodeId}:ACK_JOB:'.encode(), address)

            # Send the job to the available workers
            # TODO: Implement splitting the job to multiple workers
            for workerNodeId in self.activeWorkers:
                self.send_jobs(workerNodeId, self.workerNodes[workerNodeId], payload)

        # No workers have joined
        else:
            # Inform the client that no workers have joined, refuse the job
            logging.warning('No workers joined')
            self.handle_response(f'{requestNodeId}:ERROR:No available workers'.encode(), address)

    def send_jobs(self, nodeId, nodeAddress, hashToCrack):
        # Send the job to the worker
        logging.info(f'Sending job to: {nodeId} {nodeAddress}')
        self.handle_response(f'{nodeId}:JOB:{self.activeWorkers[nodeId]}={hashToCrack}'.encode(), nodeAddress)
        # Receive acknowledgment for the job
        data, nodeAddress = self.serverSocket.recvfrom(1024)
        # Handle request
        self.handle_request(data, nodeAddress)

    def handle_abort(self):
        logging.info('Aborting all active workers')
        # Send ABORT commands to all active workers
        for nodeId, _ in self.activeWorkers.items():
            self.handle_response(f'{nodeId}:ABORT:'.encode(), self.workerNodes[nodeId])

    # Run the server
    def run(self):
        logging.info('Server running')
        while True:
            print('Listening...')
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
