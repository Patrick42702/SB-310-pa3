'''
This file contains basic utility functions that you can use and can also make your helper functions here
'''
import binascii

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

# this function takes a socket and requests data, then return a tuple of the packet info
def get_packet(sock):
    raw_packet, address = sock.recvfrom(CHUNK_SIZE)
    packet_type, msg_len, message, checksum = parse_packet(raw_packet.decode())
    return packet_type, msg_len, message, checksum, address 

def parse_message(message):
    return message.split(" ")









