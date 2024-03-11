import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific IP address and port
server_address = ('localhost', 12345)
sock.bind(server_address)

while True:
    print('Waiting for a message...')
    data, address = sock.recvfrom(1024)
    
    # Process the received data
    # ...

    # Send a response back to the client
    response = 'Hello, client!'
    sock.sendto(response.encode(), address)
