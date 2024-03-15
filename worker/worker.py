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
        if response == 'PING':
            self.handle_response(f'{self.nodeId}:{self.status}:'.encode(), address)
        elif response == 'ACK':
            pass
        elif response == 'JOB':
            print(f'Starting job: {payload}')
            self.handle_response(f'{self.nodeId}:ACK_JOB:'.encode(), address)
            self.handle_job(address, payload)

    # Send a response
    def handle_response(self, data, address):
        self.workerSocket.sendto(data, address)
    
    # Handle a job
    def handle_job(self, address, payload):
        time.sleep(20)
        self.handle_response(f'{self.nodeId}:RESULT:{payload}'.encode(), address)

    # Run the server
    def run(self):
        self.handle_response(f'{self.nodeId}:JOIN:'.encode(), self.serverAddress)
        while True:
            print(f'Waiting for a job...{self.nodeId}')
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
