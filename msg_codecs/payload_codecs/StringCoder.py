from .PayloadCoder import PayloadCoder


class StringCoder(PayloadCoder):
    def __init__(self, name: str, type: int, fields, format='string'):
        if format != 'string':
            raise ValueError("Required format is string!")

        if len(fields) != 1:
            raise ValueError("String message must have exactly 1 field!")

        PayloadCoder.__init__(self, name, type, 's', fields)

    def encode(self, data: dict):
        return data[self.field_names[0]].encode('utf-8')

    def decode(self, payload):
        return {self.field_names[0]: payload.decode('utf-8', 'strict')}
