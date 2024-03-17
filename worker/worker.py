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
        print(f'Received: {data.decode()} from {address}')
        logging.info(f':Node[{self.nodeId}]: Received: {data.decode()} from {address}')
        # Data consists of nodeId:response:payload
        self.nodeId, response, payload = data.decode().split(':')

        # Server sends PING request to get worker's status
        if response == 'PING':
            self.handle_response(f'{self.nodeId}:{self.status}:'.encode(), address)

        # Server sends JOBs to crack hashes
        elif response == 'JOB':
            print(f'Starting job: {payload}')
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
        print(f'Sending: {data.decode()} to {address}')
        logging.info(f':Node[{self.nodeId}]: Sending: {data.decode()} to {address}')
        self.workerSocket.sendto(data, address)
    
    # Handle a job
    def handle_job(self, address, payload):
        # Set worker's status to BUSY
        self.status = 'BUSY'

        # Job status
        cracked = False

        # Extract the job ID and hash from the payload
        jobId, hashToCrack, lowerLimit, upperLimit, passwordLength = payload.split(';')
        print(f'Job ID: {jobId}, Hash: {hashToCrack}, Lower: {lowerLimit}, Upper: {upperLimit}, Length: {passwordLength}')
        print(f'Starting job with ID {jobId} and hash {hashToCrack}')
        logging.info(f':Node[{self.nodeId}]: Starting job with ID {jobId} and hash {hashToCrack}')

        # hashcat -m 0 -a 3 hash ?d*length --skip lower --limit upper
        hashcatCommand = f'hashcat -m 0 -a 3 {hashToCrack} ?a*{passwordLength} --skip {lowerLimit} --limit {upperLimit}'

        # Execute hashcat command using subprocess
        try:
            output = subprocess.check_output(hashcatCommand, shell=True)
            print(output.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Error executing hashcat command: {e}")
            logging.error(f':Node[{self.nodeId}]: Error executing hashcat command: {e}')
        """
        # Successful crack
        if tempFailOrResult == 1:
            crackedHash = 'salasana'
            logging.info(f':Node{self.nodeId} Job {jobId} finished with result: {crackedHash}')
            self.handle_response(f'{self.nodeId}:RESULT:{jobId};{crackedHash}'.encode(), address)
        """
        # Failed to crack
        if not cracked:
            logging.info(f':Node[{self.nodeId}]: Job {jobId} unsuccessful')
            self.handle_response(f'{self.nodeId}:FAIL:{jobId}'.encode(), address)

        # Reset status
        self.status = 'IDLE'

    # Handle an abort by closing the job thread
    def handle_abort(self):
        print('Aborting job')
        logging.info(f':Node[{self.nodeId}]: Aborting job')
        # Set event to terminate job thread
        self.shouldAbort.set()
        # Wait for job thread to terminate
        self.jobThread.join()
        # Clear the event
        self.shouldAbort.clear()
        # Reset status
        self.status = 'IDLE'

    # Run the worker
    def run(self):
        logging.info(f'Trying to establish connection with server at {self.serverAddress}')

        # Send a JOIN request to the server every 5 seconds until the server acknowledges it
        while True:
            try:
                self.handle_response(f'{self.nodeId}:JOIN:'.encode(), self.serverAddress)
                data, address = self.workerSocket.recvfrom(1024)
                self.handle_request(data, address)
                if data.decode().split(':')[1] == 'ACK':
                    break
            except Exception as e:
                logging.warning(f'Failed to connect to server at {self.serverAddress}, retrying in 5 seconds')
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
    try:
        worker = Worker(sys.argv[1], int(sys.argv[2])) # 'localhost', 9090) #
    except Exception as e:
        logging.error(f'Failed to launch worker: {e}')
        print(f'Failed to launch worker: {e}')
        print('Usage: worker.py <server_address> <server_port>')
        sys.exit(1)
    worker.run()
