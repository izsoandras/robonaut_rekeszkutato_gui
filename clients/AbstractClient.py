import abc
import msg_codecs.frame_codecs
import msg_codecs.payload_codecs
from dataholders.DataHolder import DataHolder


class AbstractClient(metaclass=abc.ABCMeta):
    def __init__(self, msg_coder: msg_codecs.frame_codecs.AbstractCoder, payload_coder: msg_codecs.payload_codecs.AbstractCoder, dhs: DataHolder):
        self.msg_coder = msg_coder
        self.payload_coders = payload_coder
        self.dataholders = dhs
