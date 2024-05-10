import socket
import random 
import time
import util

server_port = 33131
server_addr = "0.0.0.0"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(None)
sock.bind(('', random.randint(10000, 40000)))
name = "client 1"

inp = ""
while True:
    inp = input("string to bombard: ")
    inp = inp * 500
    break

sender = util.Sender("disconnect: ", sock, (server_addr, server_port))
sender.send_message()
