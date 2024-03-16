import random
import socket
import subprocess
import sys
import threading
import time

class Worker:
    nodeId = 0
    status = 'IDLE'
    # Initialize the worker class
    def __init__(self, address, port):
        self.workerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)

    # Handle incoming requests
    def handle_request(self, data, address):
        print('Received:', data.decode(), 'from', address)
        self.nodeId, response, payload = data.decode().split(':')
        # Server sends PING request to get worker's status
        if response == 'PING':
            self.handle_response(f'{self.nodeId}:{self.status}:'.encode(), address)
        # Server sends ACKs to acknowledge results
        elif response == 'ACK':
            pass
        # Server sends JOBs to crack hashes
        elif response == 'JOB':
            print(f'Starting job: {payload}')
            # Send response to acknowledge the received JOB
            self.handle_response(f'{self.nodeId}:ACK_JOB:'.encode(), address)
            # Start working
            self.handle_job(address, payload)

    # Send a response
    def handle_response(self, data, address):
        self.workerSocket.sendto(data, address)
    
    # Handle a job
    def handle_job(self, address, payload):
        # TEMPORARY IMPLEMENTATION only to simulate the time taken to work
        jobId, hashToCrack = payload.split('=')
        # Randomly send a FAIL or a RESULT
        time.sleep(20)
        tempFailOrResult = random.randint(0,1)
        # Successful crack
        if tempFailOrResult == 1:
            crackedHash = 'salasana'
            self.handle_response(f'{self.nodeId}:RESULT:{jobId}={crackedHash}'.encode(), address)
        # Failed to crack
        else:
            self.handle_response(f'{self.nodeId}:FAIL:{jobId}'.encode(), address)

    # Run the server
    def run(self):
        self.handle_response(f'{self.nodeId}:JOIN:'.encode(), self.serverAddress)
        while True:
            print(f'Waiting for a job...')
            data, address = self.workerSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    # Start the worker
    worker = Worker('localhost', 9090) #sys.argv[1], sys.argv[2]) # 
    # Thread to handle communication with the server
    #thread1 = threading.Thread(target=worker.run)
    worker.run()
    # Start threads
    #thread1.start()
