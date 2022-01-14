import struct
from .PayloadCoder import PayloadCoder


class LogCoder(PayloadCoder):
    def __init__(self, msg_type: int):
        PayloadCoder.__init__(self, 'log', msg_type, 'Bs', ['level', 'message'])

    def encode(self, data: dict):
        excludes = [key for key in self.field_names if key not in data.keys()]
        if len(excludes) > 0:
            raise KeyError(f'The following fields are missing from the passed {self.name} dictionary: {excludes}')

        if len(data['message']) > 0xAA-1:
            raise OverflowError(f'Message is longer than 0xAA ({0xAA}), cannot encode!')

        if data['level'] < 1 or data['level'] > 5:
            raise ValueError(f'Level should be between 1-5, not {data["level"]}')

        level_enc = struct.pack('B', data['level'])
        msg_enc = data['message'].encode()

        return level_enc + msg_enc

    def decode(self, payload):
        level = payload[0]
        try:
            message = str(payload[1:], 'utf-8')
        except UnicodeDecodeError as ude:
            message = str(ude) + f'message: {payload[1:].hex()}'

        return {
            'name': self.name,
            'level': level,
            'message': message
        }