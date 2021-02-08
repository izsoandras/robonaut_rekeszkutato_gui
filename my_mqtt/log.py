import my_mqtt.background_coders
from my_mqtt.constants import *


def encode_log(log_msg):

    if len(log_msg['level']) + len(log_msg['message']) >= 0xAA:
        logger.warning('Too long message, cannot send')
        return None

    if log_msg['level'] == 'error':
        lvl = 'ERR'.encode()
    elif log_msg['level'] == 'info':
        lvl = 'INFO'.encode()
    elif log_msg['level'] == 'warning':
        lvl = 'WARN'.encode()
    else:
        logger.warning('Unexpected log level: '+log_msg['level'])
        return None

    data = bytearray(lvl)
    data.extend(log_msg['message'].encode())

    length = bytearray(1)
    length[0] = len(data)

    type = bytearray(1)
    type[0] = 0x00

    enc_msg = bytearray(0)
    enc_msg.extend(length)
    enc_msg.extend(type)
    enc_msg.extend(data)

    return enc_msg


def decode_log(msg):
    if not my_mqtt.background_coders.validate_message(msg):
        return None

    if msg[1] != 0x00:
        logger.warning('Wrong topic: '+str(msg[1])+' in log')
        return None

    log_message = str(msg[2:], 'utf-8')

    ret = {}
    if log_message[0:3] == 'ERR':
        ret['level'] = 'error'
        ret['message'] = log_message[3:]
    elif log_message[0:4] == 'INFO':
        ret['level'] = 'info'
        ret['message'] = log_message[4:]
    elif log_message[0:4] == 'WARN':
        ret['level'] = 'warning'
        ret['message'] = log_message[4:]
    else:
        logger.warning('Wrong level prefix: '+log_message)
        ret = None

    return ret


