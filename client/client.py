import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the server address and port
server_address = ('localhost', 12345)

# Send data to the server
message = b'Hello, server!'
client_socket.sendto(message, server_address)

# Receive response from the server
data, server = client_socket.recvfrom(1024)
print('Received:', data.decode())

# Close the socket
client_socket.close()
