import logging
import random
import socket
import subprocess
import sys
import threading
import time

"""
Worker class

"""

class Worker:
    # Intialize ID as 0, server will assign a unique ID
    nodeId = 0
    # Initialize status as IDLE, status will be BUSY when working
    status = 'IDLE'
    # Initialize jobThread as None, will be assigned a thread when working
    jobThread = None
    # Set shouldAbort as an event to terminate active job threads
    shouldAbort = threading.Event()

    # Initialize the worker class
    def __init__(self, address, port):
        self.workerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)

    # Handle incoming requests
    def handle_request(self, data, address):
        print(f'[WORKER]: Received: {data.decode()} from {address}')
        logging.info(f':Node[{self.nodeId}]: Received: {data.decode()} from {address}')
        # Data consists of nodeId:response:payload
        self.nodeId, response, payload = data.decode().split(':')

        # Server sends PING request to get worker's status
        if response == 'PING':
            self.handle_response(f'{self.nodeId}:{self.status}:'.encode(), address)

        # Server sends JOBs to crack hashes
        elif response == 'JOB':
            print(f'[WORKER]: Starting job: {payload}')
            # Send response to acknowledge the received JOB
            self.handle_response(f'{self.nodeId}:ACK_JOB:'.encode(), address)
            # Start job in a new thread to keep listening for other requests
            self.jobThread = threading.Thread(target=self.handle_job, args=(address, payload))
            self.jobThread.start()
        
        # Server sends ABORT to stop working
        elif response == 'ABORT':
            self.handle_abort()

    # Send a response
    def handle_response(self, data, address):
        print(f'[WORKER]: Sending: {data.decode()} to {address}')
        logging.info(f':Node[{self.nodeId}]: Sending: {data.decode()} to {address}')
        self.workerSocket.sendto(data, address)
    
    # Handle a job
    def handle_job(self, address, payload):
        # Set worker's status to BUSY
        self.status = 'BUSY'

        # Job status/cracked password
        cracked = None

        # Variable to simulate cracking
        randomInteger = random.randint(0, 10)

        # Extract the job ID and hash from the payload
        jobId, hashToCrack, lowerLimit, upperLimit, passwordLength = payload.split(';')
        print(f'[WORKER]: Starting Job ID: {jobId}, Hash: {hashToCrack}, Lower: {lowerLimit}, Upper: {upperLimit}, Length: {passwordLength}')
        logging.info(f':Node[{self.nodeId}]: Starting job with ID {jobId} and hash {hashToCrack}')

        # Simulate the job
        while randomInteger != 0 and randomInteger != 1:
            # Check if the job has been aborted, stop running if it has
            if self.shouldAbort.is_set():
                break
            randomInteger = random.randint(0, 30)
            time.sleep(randomInteger // 5)

        if randomInteger == 1:
            cracked = 'Psw123'

        # Job aborted
        if self.shouldAbort.is_set():
            print(f'[WORKER]: Job {jobId} aborted')
            logging.info(f':Node[{self.nodeId}]: Job {jobId} aborted')
            result = 'ABORT'
            payload = jobId
        else:
            # Successful crack
            if cracked:
                result = 'RESULT'
                payload = f'{jobId};{cracked}'
                logging.info(f':Node{self.nodeId} Job {jobId} finished with result: {cracked}')
            # Failed to crack
            else:
                result = 'FAIL'
                payload = jobId
                logging.info(f':Node[{self.nodeId}]: Job {jobId} unsuccessful')

        # Reset status of worker
        self.status = 'IDLE'
        self.handle_response(f'{self.nodeId}:{result}:{payload}'.encode(), address)

    # Handle an abort by closing the job thread
    def handle_abort(self):
        print('[WORKER]: Aborting job')
        logging.info(f':Node[{self.nodeId}]: Aborting job')
        # Set event to terminate job thread
        self.shouldAbort.set()
        # Wait for job thread to terminate
        self.jobThread.join()
        # Clear the event
        self.shouldAbort.clear()

    # Run the worker
    def run(self):
        logging.info(f'Trying to establish connection with server at {self.serverAddress}')

        # Try to join the server every 5 seconds for five times
        for i in range(5):
            try:
                self.handle_response(f'{self.nodeId}:JOIN:'.encode(), self.serverAddress)
                data, address = self.workerSocket.recvfrom(1024)
                self.handle_request(data, address)
                if data.decode().split(':')[1] == 'ACK':
                    break
            except Exception as e:
                if i > 4:
                    print('Server unavailable, terminating client')
                    sys.exit(1)
                print('Server unavailable, retrying in 5 seconds')
                logging.warning(f'Failed to connect to server at {self.serverAddress}: {e}')
            time.sleep(5)

        logging.info(f':Node[{self.nodeId}]: Connected to server at {self.serverAddress}')
        # Listen for incoming requests
        while True:
            data, address = self.workerSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        filename='worker.log',
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    # Start the worker
    logging.info('Starting worker')
    print('[WORKER]: Starting worker')
    try:
        worker = Worker(sys.argv[1], int(sys.argv[2])) # 'localhost', 9090) #
    except Exception as e:
        logging.error(f'Failed to launch worker: {e}')
        print(f'[WORKER]: Failed to launch worker: {e}')
        print('[WORKER]: Usage: worker.py <server_address> <server_port>')
        sys.exit(1)
    worker.run()
