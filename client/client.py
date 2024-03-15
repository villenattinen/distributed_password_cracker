import socket
import sys
# import time

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
        data, server = self.clientSocket.recvfrom(1024)
        self.clientId, response = data.decode().split(':')
        return response
    
    # Close the connection
    def close(self):
        self.clientSocket.close()

if __name__ == '__main__':
    # Start the client
    client = Client('localhost', 9090) #sys.argv[1], sys.argv[2]) #
    client.send(f'{client.clientId}:PING')
    print(client.receive())
    print(client.clientId)
    client.close()
