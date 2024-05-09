'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util
from queue import Queue
from threading import Thread


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

    def handle_packet(self, queue):
        #initalize vars
        seq_no = -1
        while True:
            packet = queue.get()
            if 

        pass

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it.

        '''
        # Store the connected clients in this list, in form (("name"), (address, port))
        clients = []

        # We will store 2 dictionaries, one for keeping track of threads when needing to terminate
        # and create them and associating them with the client's ip address their associated with.AssertionError
        # the second will be mapping the client's ip address to their packet queue, so that the threads can 
        # be blocked from running until a packet thats meant for it arrives on the correct queue. 
        # when a thread receives an END packet, it will terminate the thread after receiving an acknowledgement
        # that the receiver received that its ending the connection. 

        threads = {}
        queues = {}

        # Begin try block, catch all errors in the except block
        try:
            while True:
                rec_packet = util.get_packet(self.sock)
                if rec_packet == util.RETRANSMIT:
                    raise Exception(util.RETRANSMIT)

                # Implement threading logic here so that we pass the packet to the correct thread
                if rec_packet[0] == util.START:
                    # we need to create a thread for this IP
                    queues[rec_packet[4]] = Queue()
                    threads[rec_packet[4]] = Thread(target=self.handle_packet(queues[rec_packet[4]]))
                    queues[rec_packet[4]].put(rec_packet)



                parsed_message = util.parse_message(payload)
                command, length = parsed_message[0], parsed_message[1]

                # Use list comprehension to pull the users out of the tuples into its own list
                users = [x[0] for x in clients]

                # Match command with the command of the packet to know how we'll treat the data
                match command:

                    # packet is a JOIN packet
                    case util.JOIN:
                        # If serverfull or username taken, respond to the client
                        # with the necessary error, else let the client connect and
                        # add them to the list of connected clients. Anything else
                        # occurs raise an Exception
                        username = parsed_message[2]
                        message_type = ""
                        message_format = util.TYPE_2
                        if len(clients) >= util.MAX_NUM_CLIENTS or username in users:
                            message_type = util.ERR_SERVER_FULL if len(
                                clients) >= util.MAX_NUM_CLIENTS else util.ERR_USERNAME_UNAVAILABLE
                            msg = util.make_message(message_type, message_format)
                            packet = util.make_packet(msg=msg)
                            self.sock.sendto(str.encode(packet), address)
                        elif (username, address) not in clients:
                            clients.append((username, address))
                            print(f"join: {username}")
                        else:
                            raise Exception("None of the if conditions ran")

                    # Packet is a request_user_list packet
                    case util.LIST:
                        # Here we filter the sender's name out of the client array
                        # by using the address the sender sent the packet with. sort 
                        # the list of users lexographically, join them into a string
                        # with spaces between, and format it into the appropriate message,
                        # turn it into a packet and send it to the sender. print appropriately.
                        sender = list(filter((lambda x: address == x[1]), clients))[0][0]
                        sorted_users = sorted(users)
                        users_str = " ".join(sorted_users)
                        message = util.make_message(util.RESPONSE_USERS_LIST, util.TYPE_3, users_str)
                        packet = util.make_packet(msg=message)
                        print(f"request_users_list: {sender}")
                        self.sock.sendto(str.encode(packet), address)

                    # Packet is a msg packet
                    case util.MSG:
                        # This code stips the number of users for the message, their usernames,
                        # and the message itself. Also filters out the sender's username using
                        # their address
                        user_num = parsed_message[2]
                        msg_users = parsed_message[3:(3 + int(user_num))]
                        msg_txt = " ".join(parsed_message[3 + int(user_num):])
                        sender = list(filter((lambda x: address == x[1]), clients))[0][0]

                        # Print sender username, print non existent if not connected. Get 
                        # the non-connected usernames by filter out the usernames sent by 
                        # the sender against the connected client's list
                        print(f"msg: {sender}")
                        nonexist_users = list(filter((lambda x: x not in users), msg_users))
                        for recv in nonexist_users:
                            print(f"msg: {sender} to non-existent user {recv}")

                        # create a list of clients to send the message to by checking
                        # usernames sent by the sender against users in the connected
                        # clients list
                        exist_users = []
                        for client in clients:
                            if client[0] in msg_users:
                                exist_users.append(client)

                        # begin making forward packet
                        for usr in exist_users:
                            text = str(1) + " " + sender + " " + msg_txt
                            message = util.make_message(util.MSG, util.TYPE_4, text)
                            packet = util.make_packet(msg=message)
                            self.sock.sendto(str.encode(packet), usr[1])

                    # Packet is a disconnect packet
                    case util.DISCONNECT:
                        # get the user's username and remove them from the client list'
                        user = parsed_message[2]
                        clients.remove((user, address))
                        print(f"disconnected: {user}")

                    # Unknown packet received
                    case _:
                        msg = util.make_message(util.ERR_UNKNOWN_MSG, util.TYPE_2)
                        packet = util.make_packet(message=msg)
                        clients.remove((user, address))
                        print(f"disconnected: {user} sent unknown command")




        except Exception as err:
            if err.args[0] == util.RETRANSMIT:
                print("checksum was incorrect: dropping packet")
            tb = err.__traceback__
            print(err, tb.tb_lineno) 
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
