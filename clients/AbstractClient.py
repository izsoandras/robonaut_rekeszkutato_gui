import abc
import msg_codecs.frame_codecs
import msg_codecs.payload_codecs
from dataholders.DataHolder import DataHolder


class AbstractClient(metaclass=abc.ABCMeta):
    def __init__(self, msg_coder: msg_codecs.frame_codecs.AbstractCoder, payload_coders: dict, dhs: dict):
        self.msg_coder = msg_coder
        self.payload_coders = payload_coders
        self.dataholders = dhs
