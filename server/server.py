import logging
import socket
import sys
import time

class Server:
    workerAddress = ('localhost', 8080)
    commandResponsePairs = {
        'PING': 'PONG',
        'JOB': 'JOB',
        'ACK_JOB': 'ACK_JOB'
    }

    # Initialize the server class
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    # Handle incoming requests
    def handle_request(self, data, address):
        print('Received:', data.decode(), 'from', address)
        logging.info('Received: %s from %s', data.decode(), address)
        if data.decode() == 'PING':
            self.handle_response('PONG'.encode(), address)
        elif data.decode() == 'JOB':
            self.handle_response('JOB'.encode(), self.workerAddress)
            self.handle_response('Job sent'.encode(), address)
        elif data.decode() == 'ACK_JOB':
            print('Job sent successfully')
        else:
            pass

    # Send a response
    def handle_response(self, data, address):
        logging.info('Sending message: %s to %s', data.decode(), address)
        self.serverSocket.sendto(data, address)

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
    server = Server(sys.argv[1], sys.argv[2]) # 'localhost', 9090
    server.run()
