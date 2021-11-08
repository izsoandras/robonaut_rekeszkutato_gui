import abc


class AbstractCoder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def encode(self, data: dict):
        pass

    @abc.abstractmethod
    def decode(self, data):
        pass
