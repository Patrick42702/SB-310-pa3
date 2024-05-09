import socket
import util


address = "localhost"
port = 15000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(None)
sock.bind((address, port))

if __name__ == "__main__":
    receiver = util.Receiver(sock)
    while True:
        if len(receiver.final_msg) > 0:
            break
        receiver.receive_message()
    print(receiver.final_msg)
