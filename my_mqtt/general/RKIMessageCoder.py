import struct


# TODO: move to other file/package
def concat_fields(*bytes_fields):
    ret = bytearray(0)
    for byts in bytes_fields:
        ret.extend(byts)

    return ret


class RKIMessageCoder:
    @staticmethod
    def construct_message(type, data):
        type32 = struct.pack('>I', type)

        for b in type32[0:-1]:
            if b != 0:
                raise ValueError('Type is over 0xFF: ' + type)

        if type >= 0xAA:
            raise ValueError('Type is over 0xAA: ' + type)

        type = type32[-1:]

        length32 = struct.pack('>I', len(data))
        length = length32[-1:]

        enc_msg = bytearray(0)
        enc_msg.extend(length)
        enc_msg.extend(type)
        enc_msg.extend(data)

        return enc_msg

    @staticmethod
    def deconstruct_message(msg):
        RKIMessageCoder.validate_message(msg)

        type = msg[1]
        payload = msg[2:]
        return type, payload

    @staticmethod
    def validate_message(msg):
        if len(msg) < 2:
            raise ValueError('Too few fields in message; ')
        elif msg[0] >= 0xAA:
            raise ValueError('Length field is over 0xAA; ')
        elif len(msg) - 2 != msg[0]:
            raise ValueError('Length field does not match with data field length: ' + str(len(msg) - 2) + ' != ' + str(
                msg[0]) + '; ')
        else:
            return True

