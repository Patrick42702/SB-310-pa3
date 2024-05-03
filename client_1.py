'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util

'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''

class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username

    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message. 
        Use make_message() and make_util() functions from util.py to make your first join packet
        Waits for userinput and then process it
        '''

        # We need to create the JOIN message and packet, then send it to the server
        message = util.make_message(util.JOIN, 1, self.name)
        packet = util.make_packet(msg=message)
        self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))
        print(f"join: {self.name}")
        while True:

            inp = util.get_input()
            input_args = inp.split(" ")
            command = input_args[0]

            match command:
                case util.LIST:
                    msg = util.make_message(util.LIST, util.TYPE_2)
                    packet = util.make_packet(msg=msg)
                    self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))


    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        while True:
            packet_type, msg_len, message, checksum, address = util.get_packet(self.sock) 
            parsed_message = util.parse_message(message)
            command, length = parsed_message[0], parsed_message[1]
            match command:
                case util.ERR_SERVER_FULL:
                    print("disconnected: server full")
                    raise SystemExit
                case util.ERR_USERNAME_UNAVAILABLE:
                    print("disconnected: username not available")
                    raise SystemExit
                case util.RESPONSE_USERS_LIST:
                    users = parsed_message[2:]
                    f_users = " ".join(users)
                    print(f"list: {f_users}")
                case _:
                    pass 




# Do not change below part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=", "window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        print("exiting")
        sys.exit()
