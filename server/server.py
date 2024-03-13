import socket

# handle work request
# hashcat/johntheripper
# bruteforce/wordlist
# default wordlist/dictionary
# communicate with worker
# send response back to client
# 

class Server:
    def __init__(self, address, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)
        self.serverSocket.bind(self.serverAddress)

    def handle_request(self, data, address):
        print('Received message:', data.decode(), 'from', address)
        response = 'Received message: ' + data.decode() 
        self.serverSocket.sendto(response.encode(), address)

    def handle_response(self, data, address):
        print('Received response:', data.decode(), 'from', address)
        response = 'Received response: ' + data.decode() 
        self.serverSocket.sendto(response.encode(), address)

    def run(self):
        while True:
            print('Waiting for a message...')
            data, address = self.serverSocket.recvfrom(1024)
            self.handle_request(data, address)

if __name__ == '__main__':
    server = Server('localhost', 9090)
    server.run()
