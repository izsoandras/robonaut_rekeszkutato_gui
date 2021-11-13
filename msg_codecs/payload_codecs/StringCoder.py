from .PayloadCoder import PayloadCoder


class StringCoder(PayloadCoder):
    def __init__(self, name: str, type_byte: int, field):
        PayloadCoder.__init__(self, name, type_byte, 's', ['msg'])

    def encode(self, data: dict):
        pass

    def decode(self, payload):
        pass
