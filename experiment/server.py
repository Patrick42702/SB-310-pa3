import socket
import time

address = "localhost"
port = 15000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(None)
sock.bind((address, port))

while True:
    data, address = sock.recvfrom(1000)
    print(str(data.decode()))
