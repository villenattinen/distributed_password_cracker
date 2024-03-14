import socket
import logging

# handle work request
# hashcat/johntheripper
# bruteforce/wordlist
# default wordlist/dictionary
# communicate with worker
# send response back to client

class Server:
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    def handle_request(self, data, address):
        print('Received:', data.decode(), 'from', address)
        logging.info('Received: %s from %s', data.decode(), address)
        self.handle_response(data, address)

    def handle_response(self, data, address):
        logging.info('Sending response: %s to %s', data.decode(), address)
        self.serverSocket.sendto(data, address)

    def run(self):
        logging.info('Server running')
        while True:
            print('Waiting for a message...')
            data, address = self.serverSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    logging.basicConfig(
        filename='server.log',
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logging.info('Launching server...')
    server = Server('localhost', 9090)
    server.run()
