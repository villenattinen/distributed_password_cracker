import socket
import sys
# import time


class Client:
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
        return data.decode()
    
    # Close the connection
    def close(self):
        self.clientSocket.close()

if __name__ == '__main__':
    # Start the client
    client = Client(sys.argv[1], sys.argv[2]) # 'localhost', 9090
    client.send('JOB')
    print(client.receive())
    client.close()
