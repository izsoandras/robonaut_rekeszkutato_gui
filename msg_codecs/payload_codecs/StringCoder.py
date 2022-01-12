from .PayloadCoder import PayloadCoder


class StringCoder(PayloadCoder):
    def __init__(self, name: str, type: int, fields, format='string'):
        if format != 'string':
            raise ValueError("Required format is string!")
        PayloadCoder.__init__(self, name, type, 's', fields)

    def encode(self, data: dict):
        return data[self.field_names[0]].encode('utf-8')

    def decode(self, payload):
        return payload.decode('utf-8', 'strict')
