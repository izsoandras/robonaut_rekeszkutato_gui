import struct
from my_mqtt.background_coders import construct_message


class MessageCoder:
    def __init__(self, name: str, typebyte: int, format: str, names: list, factors: list = None):

        try:
            self.checkPattern(name, typebyte, format, names)
        except AssertionError as ae:
            raise ae

        self.name = name
        self.typebyte = typebyte
        self.bytesFormat = format
        self.names = names

        if factors is not None:
            self.factors = factors
        else:
            self.factors = [1] * len(names)

    @staticmethod
    def checkPattern(name, typebyte, format, names):
        if typebyte > 0xAA:
            raise ValueError(f'Type byte for {name} pattern is over 0xFF')
        if typebyte < 0:
            raise ValueError(f'Type byte for {name} pattern should be non negative')

        try:
            bytesFieldNum = len(struct.unpack(format, bytes('\0' * struct.calcsize(format), 'utf8')))
        except struct.error as err:
            raise err

        if len(names) < bytesFieldNum:
            raise AssertionError(f'Pattern {name} does not have enough field name given!')
        if len(names) > bytesFieldNum:
            raise AssertionError(f'Pattern {name} does not have enough byte fields given!')

    def encode(self, data: dict):
        excludes = [key for key in self.names if key not in data.keys()]
        if len(excludes) > 0:
            raise KeyError(f'The following fields are missing from the passed {self.name} dictionary: {excludes}')

        values = [data[key] for key in self.names]
        payload = struct.pack(self.bytesFormat, *values)

        return construct_message(self.typebyte, payload)

    def decode(self, data_bytes):
        fields = struct.unpack(self.bytesFormat, data_bytes)

        ret = {}
        for idx, key in enumerate(self.names):
            ret[key] = fields[idx] * self.factors[idx]

        return ret

