import socket
import subprocess
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
        self.handle_response(data, address)

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
    worker = Worker('localhost', 9090)
    # Thread to handle communication with the server
    thread1 = threading.Thread(target=worker.run)
    # Thread to handle jobs
    #thread2 = threading.Thread(target=worker.handle_job)
    # Start threads
    thread1.start()
    #thread2.start()
