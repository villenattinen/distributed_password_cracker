import socket
import subprocess
import sys
import threading

class Worker:
    # Initialize the worker class
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    # Handle incoming requests
    def handle_request(self, data, address):
        print('Received:', data.decode(), 'from', address)
        if data.decode() == 'PING':
            self.handle_response('PONG'.encode(), address)
        elif data.decode() == 'JOB':
            # Thread to handle jobs
            print('Starting job...')
            self.handle_response('ACK_JOB'.encode(), address)
        else:
            pass

    # Send a response
    def handle_response(self, data, address):
        self.serverSocket.sendto(data, address)

    # Run the server
    def run(self):
        while True:
            print('Waiting for a job...')
            data, address = self.serverSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    # Start the worker
    worker = Worker(sys.argv[1], sys.argv[2]) # 'localhost', 8080
    # Thread to handle communication with the server
    #thread1 = threading.Thread(target=worker.run)
    worker.run()
    # Start threads
    #thread1.start()
