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
        clients = []

        try:
            while True:
                packet_type, msg_len, message, checksum, address = util.get_packet(self.sock)
                parsed_message = util.parse_message(message)
                command, length = parsed_message[0], parsed_message[1]
                users = [x[0] for x in clients]

                match command:
                    case util.JOIN:
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

                    case util.LIST:
                        sorted_users = sorted(users)
                        users_str = " ".join(sorted_users)
                        message = util.make_message(util.RESPONSE_USERS_LIST, util.TYPE_3, users_str)
                        packet = util.make_packet(msg=message)
                        self.sock.sendto(str.encode(packet), address)

                    case util.MSG:
                        # This code stips the number of users for the message, their usernames, and the message itself
                        user_num = parsed_message[2]
                        msg_users = parsed_message[3:(3 + int(user_num))]
                        msg_txt = " ".join(parsed_message[3 + int(user_num):])
                        sender = list(filter((lambda x: address == x[1]), clients))[0][0]

                        # Print sender username, print non existent if not connected
                        nonexist_users = list(filter((lambda x: x not in users), msg_users))
                        for recv in nonexist_users:
                            print(f"msg: {sender} to non-existent user {recv}")

                        # create a list of clients to send the message to
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

                    case util.DISCONNECT:
                        user = parsed_message[2]
                        clients.remove((user, address))
                        print(f"disconnected: {user}")

                    case _:
                        msg = util.make_message(util.ERR_UNKNOWN_MSG, util.TYPE_2)
                        clients.remove((user, address))
                        print(f"disconnected: {user} sent unknown command")




        except Exception as err:
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
