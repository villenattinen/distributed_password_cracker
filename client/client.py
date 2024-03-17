import logging
import socket
import sys
import time

class Client:
    # Initialize client's ID as 0, server will assign a unique ID
    clientId = 0
    hashToCrack = ''
    passwordLength = 0

    # Initialize the client class
    def __init__(self, address, port, hashToCrack, passwordLength):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.hashToCrack = hashToCrack
        self.passwordLength = passwordLength

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
    try:
        client = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]) #'localhost', 9090) #
    except Exception as e:
        logging.error(f'Failed to launch client: {e}')
        print(f'Failed to launch client: {e}')
        print('Usage: client.py <server_address> <server_port> <hash_to_crack> <password_length>')
        sys.exit(1)
    
    # Set server status to UNKNOWN at the start
    serverStatus = 'UNKNOWN'

    print('Checking if server is up')
    # Try to establish connection with the server five times
    for i in range(5):
        try:
            client.send(f'{client.clientId}:PING:')
            serverStatus = client.receive()[0]
            if serverStatus == 'PONG':
                break
        except Exception as e:
            if i > 4:
                print('Server unavailable, terminating client')
                sys.exit(1)
            print('Server unavailable, retrying in 5 seconds')
            time.sleep(5)

    print('Server is up!')

    # Try to send a job to the server five times
    print('Checking if server is accepting jobs')
    for i in range(5):
        try:
            client.send(f'{client.clientId}:JOB:{client.hashToCrack};{client.passwordLength}')
            if client.receive()[0] == 'ACK_JOB':
                break
            print('Server not accepting jobs, retrying in 5 seconds')
        except Exception as e:
            if i > 4:
                print('Server unavailable, terminating client')
                sys.exit(1)
            print('Server not responding, retrying in 5 seconds')
        time.sleep(5)
    
    print('Job accepted by server')

    print('Checking if job is finished')
    while True:
        try:
            client.send(f'{client.clientId}:PING:')
            jobStatus, payload = client.receive()
            if jobStatus == 'RESULT':
                print(f'\nHash {client.hashToCrack} successfully cracked\nResult: {payload}\n')
                break
            elif jobStatus == 'FAIL':
                print(f'\nFailed to crack hash {client.hashToCrack}')
                break
            print('Server working, retrying in 5 seconds')
        except Exception as e:
            print('Server not responding, retrying in 5 seconds')
        time.sleep(5)

    print('\nAll done!')

    client.close()
