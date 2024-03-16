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
        self.clientSocket.sendto(message.encode(), self.serverAddress)
    
    # Receive a message
    def receive(self):
        data, address = self.clientSocket.recvfrom(1024)
        self.clientId, response, payload = data.decode().split(':')
        return response, payload

    # Close the connection
    def close(self):
        self.clientSocket.close()

if __name__ == '__main__':
    # Start the client
    client = Client('localhost', 9090) #sys.argv[1], sys.argv[2], sys.argv[3]) #
    serverStatus = 'UNKNOWN'

    print('PINGing server')
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

    print('Sending job')
    while True:
        client.send(f'{client.clientId}:JOB:asdf')
        if client.receive()[0] == 'ACK_JOB':
            break
        print('Server not accepting jobs, retrying in 5 seconds')
        time.sleep(5)
    print('Job accepted by server')

    print('PINGing server until JOB is finished')
    while True:
        client.send(f'{client.clientId}:PING:')
        jobStatus, payload = client.receive()
        if jobStatus == 'RESULT':
            print(f'Cracked: {payload}')
            break
        elif jobStatus == 'FAIL':
            print('Failed to crack hash')
            break
        print('Server working, retrying in 5 seconds')
        time.sleep(5)
    print('All done!')

    client.close()
