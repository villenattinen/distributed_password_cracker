import random
import socket
import subprocess
import sys
import threading
import time

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
            self.jobThread = threading.Thread(target=self.handle_job, args=(address, payload))
            self.jobThread.start()
        
        # Server sends ABORT to stop working
        elif response == 'ABORT':
            self.handle_abort()

    # Send a response
    def handle_response(self, data, address):
        self.workerSocket.sendto(data, address)
    
    # Handle a job
    def handle_job(self, address, payload):
        # Set status to BUSY
        self.status = 'BUSY'

        # Extract the job ID and hash from the payload
        jobId, hashToCrack = payload.split('=')

        """
        TEMPORARY IMPLEMENTATION only to simulate the time taken to work
        """
        # Randomly sleep between 5 and 20 seconds
        tempRandomSleepTime = random.randint(5,20)
        tempFailOrResult = random.randint(0,10)
        time.sleep(tempRandomSleepTime)
        while tempFailOrResult != 1 and tempFailOrResult != 0:
            if self.shouldAbort.is_set():
                return
            tempFailOrResult = random.randint(0,10)

        # Successful crack
        if tempFailOrResult == 1:
            crackedHash = 'salasana'
            self.handle_response(f'{self.nodeId}:RESULT:{jobId}={crackedHash}'.encode(), address)
        # Failed to crack
        else:
            self.handle_response(f'{self.nodeId}:FAIL:{jobId}'.encode(), address)
        # Reset status
        self.status = 'IDLE'

    # Handle an abort by closing the job thread
    def handle_abort(self):
        print('Aborting job')
        # Set event to terminate job thread
        self.shouldAbort.set()
        # Wait for job thread to terminate
        self.jobThread.join()
        # Clear the event
        self.shouldAbort.clear()
        # Reset status
        self.status = 'IDLE'

    # Run the server
    def run(self):
        self.handle_response(f'{self.nodeId}:JOIN:'.encode(), self.serverAddress)
        while True:
            print(f'Listening...')
            data, address = self.workerSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    # Start the worker
    worker = Worker('localhost', 9090) #sys.argv[1], sys.argv[2]) # 
    worker.run()
