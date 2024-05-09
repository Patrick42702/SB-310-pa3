import socket
import util


address = "127.0.0.1"
port = 15000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(None)
sock.bind((address, port))

if __name__ == "__main__":
    receiver = util.Receiver(sock)
    print(receiver.sock)
    receiver.receive_message()
    print(receiver.final_msg)
