'''
This file contains basic utility functions that you can use and can also make your helper functions here
'''
import binascii
import socket
import time
import random
import logging
import threading
from queue import Queue

MAX_NUM_CLIENTS = 10
TIME_OUT = 0.5 # 500ms
CHUNK_SIZE = 1400 # 1400 Bytes

# I store all of the constants I use here
ERR_USERNAME_UNAVAILABLE = "ERR_USERNAME_UNAVAILABLE"
ERR_SERVER_FULL = "ERR_SERVER_FULL"
RESPONSE_USERS_LIST = "RESPONSE_USERS_LIST"
REQUEST_USERS_LIST = "request_users_list"
LIST = "list"
JOIN = "join"
MSG = "msg"
START = "START"
DATA = "DATA"
END = "END"
ACK = "ACK"
RETRANSMIT = "RETRANSMIT"
DISCONNECT = "disconnect"
ERR_UNKNOWN_MSG = "ERR_UNKNOWN_MESSAGE"
TYPE_1 = 1
TYPE_2 = 2
TYPE_3 = 3
TYPE_4 = 4
TYPE_5 = 5


def validate_checksum(message):
    '''
    Validates Checksum of a message and returns true/false
    '''
    try:
        msg, checksum = message.rsplit('|', 1)
        msg += '|'
        return generate_checksum(msg.encode()) == checksum
    except BaseException:
        return False


def generate_checksum(message):
    '''
    Returns Checksum of the given message
    '''
    return str(binascii.crc32(message) & 0xffffffff)


def make_packet(msg_type="data", seqno=0, msg=""):
    '''
    This will add the header to your message.
    The formats is `<message_type> <sequence_number> <body> <checksum>`
    msg_type can be data, ack, end, start
    seqno is a packet sequence number (integer)
    msg is the actual message string
    '''
    body = "%s|%d|%s|" % (msg_type, seqno, msg)
    checksum = generate_checksum(body.encode())
    packet = "%s%s" % (body, checksum)
    return packet


def parse_packet(message):
    '''
    This function will parse the packet in the same way it was made in the above function.
    '''
    pieces = message.split('|')
    msg_type, seqno = pieces[0:2]
    checksum = pieces[-1]
    data = '|'.join(pieces[2:-1])
    return msg_type, seqno, data, checksum


def make_message(msg_type, msg_format, message=None):
    '''
    This function can be used to format your message according
    to any one of the formats described in the documentation.
    msg_type defines type like join, disconnect etc.
    msg_format is either 1,2,3 or 4
    msg is remaining. 
    '''
    if msg_format == 2:
        msg_len = 0
        return "%s %d" % (msg_type, msg_len)
    if msg_format in [1, 3, 4]:
        msg_len = len(message)
        return "%s %d %s" % (msg_type, msg_len, message)
    return ""

def get_input(s=""):
    return input(s)


# this function takes a sock and requests data, then return a tuple of the packet info
def get_packet(sock):
    raw_packet, address = sock.recvfrom(CHUNK_SIZE)
    raw_packet = raw_packet.decode()
    if not validate_checksum(raw_packet):
        return '', address
    return raw_packet, address

def send_ack(sock, destination, seqno):
    ack_packet = make_packet(ACK, seqno=int(seqno) +1)
    sock.sendto(str.encode(ack_packet), destination)
    return

# this function takes in a sock, destination, message
# It it supposed to transmit this message over to the receiver using our 
# basic tcp like protocol. 

class Sender():
    def __init__(self, message, sock, dest, sender_queue: Queue):
        self.message = message
        self.sock = sock
        self.dest = dest
        self.start_seq = random.randint(0, 50000)
        self.current_seq = self.start_seq
        self.packets = []
        self.sender_queue = sender_queue

    def transmit(self, packet):
        self.sock.sendto(packet.encode(), self.dest)

    def chunkify(self):
        packets = []
        message = self.message
        # just blindly cut the message into chunks of 1300 bytes and then form them
        # into packets and return the list of packets
        self.current_seq = self.start_seq + 1
        while len(self.message) > 1300:
            slice_message = self.message[0:1300]
            new_packet = make_packet(DATA, self.current_seq, msg=slice_message)
            packets.append(new_packet)
            self.current_seq += 1
            self.message = self.message[1300:]
        if len(self.message) > 0:
            last_packet = make_packet(DATA, self.current_seq, msg=self.message)
            packets.append(last_packet)
        self.message = message
        return packets

    def send_message(self):
        # Start by sending a start packet and waiting till it's acked
        self.packets = self.chunkify()
        self.current_seq = self.start_seq

        start_packet = make_packet(msg_type=START, seqno=self.current_seq)
        init_time = time.time()
        current_packet = start_packet
        end_packet_seq = 0
        self.transmit(start_packet)

        self.sock.settimeout(0.5)
        while True:
            try :
                data, address = get_packet(self.sock)
                if data:
                    msg_type, seqno, data, checksum = parse_packet(data)
                    seqno = int(seqno)

                    correct_ack = (seqno == self.current_seq + 1)

                    if correct_ack and len(self.packets) > 0:
                        init_time = time.time()
                        current_packet = self.packets.pop(0)
                        self.current_seq += 1 
                        msg_type, seqno, data, checksum = parse_packet(current_packet)
                        print(f"the sequence number for this packet is {int(seqno)}. It should be {self.current_seq}")
                        self.transmit(current_packet)

                        #this conditional means we just received the ack for the last data packet
                    elif correct_ack and len(self.packets) == 0 and end_packet_seq == 0:
                        init_time = time.time()
                        current_packet = make_packet(END, self.current_seq + 1)
                        end_packet_seq = self.current_seq + 1

                        # this condition means we received the ack for the end packet
                    elif seqno == end_packet_seq + 1:
                        print("received the correct sequence number from the server")
                        self.sock.settimeout(None)
                        return

                    else:
                        print("we aint supposed to hit this")
            except socket.timeout:
                elapsed_time = time.time() - init_time
                if elapsed_time >= TIME_OUT:
                    self.transmit(current_packet)
                    init_time = time.time()
# this function takes a sock, and receives a message. Upon receiving a start message,
# it should then buffer all subsequent messages and ACK when needed. Upon receiving an 
# end packet, it should parse all of the buffered messages together and return the message 
# intended for the receiver

class Receiver():
    def __init__(self, sock, receiver_queue: Queue):
        self.msg_buffer = {}
        self.final_msg = ""
        self.rec_address = None
        self.sock = sock
        self.event = threading.Event()
        self.receiver_queue = receiver_queue

    # this is our receiver message function. it will continually run for a connection instance.ConnectionError
    # upon receiving a start, clear the buffers. Upon receiving data packets, buffer them in the message buffer.BufferError
    # upon receiving an end packet, parse the message from the message buffer in the correct order and store it in final 
    # message. Then the receiver can pull the message from that field.
    def receive_message(self):
        while True:
            data, address = self.receiver_queue.get()
            if data:
                msg_type, seqno, data, checksum = parse_packet(data)
                if msg_type == START:
                    self.msg_buffer = {}
                    self.final_msg = ""
                    send_ack(self.sock, address, seqno)
                elif msg_type == DATA:
                    self.msg_buffer[seqno] = data
                    send_ack(self.sock, address, seqno)
                elif msg_type == END:
                    sort_keys = sorted(self.msg_buffer.keys())
                    for key in sort_keys:
                        self.final_msg += self.msg_buffer[key]
                        self.rec_address = address
                        self.event.set()
                    self.msgs_rec += 1
                    send_ack(self.sock, address, seqno)

    def get_msg(self):
        return self.final_msg

    def get_address(self):
        return self.rec_address

class Packager():
    def __init__(self, sock):
        self.receiver = Queue()
        self.sender = Queue()
        self.sock = sock

    def package(self):
        while True:
            try:
                packet, address = get_packet(self.sock)
                if packet:
                    msg_type, seqno, data, checksum = parse_packet(packet)
                    if msg_type == ACK:
                        print(f"putting this data packet on the queue: {packet}")
                        self.sender.put((packet, address))
                    else:
                        print(f"putting this data packet on the queue: {packet}")
                        self.receiver.put((packet, address))
            except socket.timeout:
                pass

def parse_message(message):
    return message.split(" ")











