import struct
from my_mqtt.constants import *

# def get_checksum(frame):
#     int_sum = sum(frame[0:-1])
#     checksum = struct.pack('>i', int_sum)
#     return checksum[-1]
#
#
# def encode_0xAA(data):
#     enc_data = bytearray(0)
#
#     for idx in range(len(data)):
#         enc_data.extend(data[idx:idx+1])
#         if data[idx] == 0x55:
#             enc_data.extend(bytearray.fromhex('AA'))
#
#     return enc_data
#
#
# def decode_0xAA(data):
#     dec_data = bytearray(0)
#
#     idx = 0
#     while idx < len(data):
#         dec_data.extend(data[idx:idx+1])
#         if data[idx] == 0x55:
#             if data[idx+1] == 0xAA:
#                 idx = idx+1
#             else:
#                 raise ValueError('Stuffing error in dataframe: '+data.hex())
#
#         idx = idx+1


def check_uint16(number, param_name=None):
    is_good = 2 ** 16 > number >= 0

    if not is_good and param_name is not None:
        logger.warning(f'Value for {param_name} is out of range: {number}')

    return is_good


def concat_fields(*bytes_fields):
    ret = bytearray(0)
    for byts in bytes_fields:
        ret.extend(byts)

    return ret


def construct_message(type, data):
    type32 = struct.pack('>I', type)

    for b in type32[0:-1]:
        if b != 0:
            logger.error('Type is over 0xFF: '+type)

    if type >= 0xAA:
        logger.error('Type is over 0xAA: ' + type)

    type = type32[-1:]

    length32 = struct.pack('>I', len(data))
    length = length32[-1:]

    enc_msg = bytearray(0)
    enc_msg.extend(length)
    enc_msg.extend(type)
    enc_msg.extend(data)

    return enc_msg


def validate_message(msg):
    log_msg = ''

    # if len(msg) < 4:
    #     log_msg = 'Too few fields in message'
    # elif len(msg)-4 != msg[1]:
    #     log_msg = 'Length field does not match with data field length'
    # elif get_checksum(msg) != msg[-1]:
    #     log_msg = 'Checksum does not match'
    if len(msg) < 2:
        log_msg = 'Too few fields in message; '
    elif msg[1] >= 0xAA:
        log_msg = 'Length field is over 0xAA; '
    elif len(msg)-2 != msg[0]:
        log_msg = 'Length field does not match with data field length: '+str(len(msg)-2)+' != '+str(msg[0])+'; '

    if log_msg:
        logger.warning(log_msg + str(msg))
        return False
    else:
        return True

