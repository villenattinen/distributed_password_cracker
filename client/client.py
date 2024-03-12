import socket
# import time
# import sys

#   $ hashcat -m value -a value hashfile wordlist
#   excluding combination attacks, mask attacks


#   $ john --format=value hashfile
#   excluding zip-file, unshadow, etc.
#   
#   crack hashstring [] or crack -h/--help 
#   --help/-h               display the options
#   --hashcat/-cat          only crack using hashcat
#   --johntheripper/-john   only crack using johntheripper
#   --bruteforce/-bf        only crack using bruteforce
#   --wordlist/-wl          only crack using wordlist
#   --hashtype/-ht          specify the hash type manually
#   --exit/e                exit the program

class Client:
    def __init__(self, address, port):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverAddress = (address, port)

    def send(self, message):
        self.clientSocket.sendto(message.encode(), self.serverAddress)
    
    def receive(self):
        data, server = self.clientSocket.recvfrom(1024)
        return data.decode()
    
    def close(self):
        self.clientSocket.close()

if __name__ == '__main__':
    
    client = Client('localhost', 9090)
    client.send('Hello, server!')
    print(client.receive())
    client.close()
