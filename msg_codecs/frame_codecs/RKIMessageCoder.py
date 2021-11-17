from .AbstractCoder import AbstractCoder
import struct


class RKIMessageCoder(AbstractCoder):
    @staticmethod
    def construct_message(type_id, data):
        type32 = struct.pack('>I', type_id)

        if type_id > 0xFF:
            raise ValueError('Type is over 0xFF: ' + type_id)

        type_byte = struct.pack('b', type_id)

        enc_msg = bytearray(0)
        enc_msg.extend(type_byte)
        enc_msg.extend(data)

        return enc_msg

    @staticmethod
    def deconstruct_message(msg):
        RKIMessageCoder.validate_message(msg)

        type_id = msg[0]
        payload = msg[1:]
        return type_id, payload

    @staticmethod
    def validate_message(msg):
        if len(msg) < 1:
            raise ValueError('Too few fields in message; ')
        else:
            return True
