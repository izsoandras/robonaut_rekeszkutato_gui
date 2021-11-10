from .AbstractCoder import AbstractCoder
import ctypes


class uartCodecDecoder_t(ctypes.Structure):
    _fields_ = [("maxLen", ctypes.c_uint8), ("state", ctypes.c_int), ("length", ctypes.c_uint8),
                ("dataCnt", ctypes.c_uint8), ("type", ctypes.c_uint8), ("data", ctypes.POINTER(ctypes.c_uint8)),
                ("crc", ctypes.c_uint8)]

class RKIUartCoder(AbstractCoder):

    encodePayload = None
    decodePayload = None

    def __init__(self, maxLen: int):
        self.maxLen = maxLen

        uart_codec = ctypes.CDLL("./uart_codec.so")

        self.decoder = uartCodecDecoder_t()
        self.decoder.maxLen = maxLen
        self.decoder.data = (ctypes.c_uint8 * 169)()

        if RKIUartCoder.encodePayload is None:
            self.encodePayload = uart_codec.UartCodecCodePayload
            self.encodePayload.restype = ctypes.c_uint8

        if RKIUartCoder.decodePayload is None:
            self.decodePayload = uart_codec.UartCodecDecodeByte
            self.decodePayload.restype = ctypes.c_bool

    def next_byte(self, byte):
        return self.decodePayload(ctypes.pointer(self.decoder), ctypes.c_uint8(byte))

    @staticmethod
    def construct_message(type, data):
        pl = (ctypes.c_uint8 * len(data))(*data)
        enc_buff = (ctypes.c_ubyte*(2*len(data)))()
        length = RKIUartCoder.encodePayload(ctypes.c_uint8(type), pl, ctypes.c_uint8(len(data)), enc_buff)

        return enc_buff[0:length]

    @staticmethod
    def deconstruct_message(msg):
        pass

    @staticmethod
    def validate_message(msg):
        return True
