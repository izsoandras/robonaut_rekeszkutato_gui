import abc


def concat_fields(*bytes_fields):
    ret = bytearray(0)
    for byts in bytes_fields:
        ret.extend(byts)

    return ret


class AbstractCoder(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def construct_message(type, data):
        pass

    @staticmethod
    @abc.abstractmethod
    def deconstruct_message(msg):
        pass

    @staticmethod
    @abc.abstractmethod
    def validate_message(msg):
        pass
