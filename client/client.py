import logging
import socket
import sys
import time

class Client:
    clientId = 0
    # Initialize the client class
    def __init__(self, address, port):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)

    # Send a message
    def send(self, message):
        logging.info(f'Sending: {message} to {self.serverAddress}')
        self.clientSocket.sendto(message.encode(), self.serverAddress)
    
    # Receive a message
    def receive(self):
        data, address = self.clientSocket.recvfrom(1024)
        logging.info(f'Received: {data.decode()} from {address}')
        self.clientId, response, payload = data.decode().split(':')
        return response, payload

    # Close the connection
    def close(self):
        logging.info('Closing connection')
        self.clientSocket.close()

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        filename='client.log',
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    # Start the client
    print('Starting client')
    logging.info('Starting client')
    client = Client('localhost', 9090) #sys.argv[1], sys.argv[2], sys.argv[3]) #
    serverStatus = 'UNKNOWN'
    hashToCrack = 'asdf'

    print('Checking if server is up')
    while True:
        try:
            client.send(f'{client.clientId}:PING:')
            serverStatus = client.receive()[0]
        except Exception as e:
            pass
        if serverStatus == 'PONG':
            break
        print('Server unavailable, retrying in 5 seconds')
        time.sleep(5)
    print('Server is up!')

    print('Checking if server is accepting jobs')
    while True:
        client.send(f'{client.clientId}:JOB:{hashToCrack}')
        if client.receive()[0] == 'ACK_JOB':
            break
        print('Server not accepting jobs, retrying in 5 seconds')
        time.sleep(5)
    print('Job accepted by server')

    print('Checking if job is finished')
    while True:
        client.send(f'{client.clientId}:PING:')
        jobStatus, payload = client.receive()
        if jobStatus == 'RESULT':
            print(f'\nHash {hashToCrack} successfully cracked\nResult: {payload}\n')
            break
        elif jobStatus == 'FAIL':
            print(f'\nFailed to crack hash {hashToCrack}')
            break
        print('Server working, retrying in 5 seconds')
        time.sleep(5)
    print('\nAll done!')

    client.close()
