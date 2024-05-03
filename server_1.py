'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util


class Server:
    '''
    This is the main Server Class. You will  write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it.

        '''
        clients = [("hi", ("nums")) for x in range(0,10)]

        try:
            while True:
                raw_packet, address = self.sock.recvfrom(1024)
                packet = util.parse_packet(raw_packet.decode())
                packet_type, msg_len, message, checksum = packet
                # print(packet_type, msg_len, message, checksum)
                split_message = message.split(" ")
                msg_type, length = split_message[0], split_message[1]

                match msg_type:
                    case "join":
                        username = split_message[2]
                        users = [x[0] for x in clients]
                        print(len(clients))
                        if len(clients) >= util.MAX_NUM_CLIENTS:
                            self.sock.sendto(str.encode("ERR_SERVER_FULL"), address)
                        elif username in users:
                            self.sock.sendto(str.encode("ERR_USERNAME_UNAVAILABLE"), address)
                        elif (username, address) not in clients:
                            clients.append((username, address))
                        else:
                            raise Exception("None of the if conditions ran")
        except Exception as err:
            print(err)
# Do not change below part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
