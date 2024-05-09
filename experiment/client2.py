import time
import socket
import random 

server_port = 15000
server_addr = "localhost"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(None)
sock.bind(('', random.randint(10000, 40000)))
name = "client 2"


inp = ""
while True:
    inp = input("string to bombard: ")
    inp = inp * 500
    break

for i in range(0,10):
    sock.sendto(inp.encode(), (server_addr, server_port))
    time.sleep(0.25)
