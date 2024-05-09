import util
import socket
import random


if __name__ == "__main__":
    server_port = 15000
    server_addr = "127.0.0.1"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(None)
    sock.bind(('', random.randint(10000, 40000)))
    name = "client 1"
    message = "msg: client1 hello! How are you?" + ("IM good" * 300)
    sender = util.Sender(message, sock, (server_addr, server_port))
    sender.send_message()

