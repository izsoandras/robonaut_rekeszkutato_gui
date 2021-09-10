import tkinter
import logging


class ParamFrame(tkinter.Frame):
    def __init__(self, parent, name, params, param_type, encode_send, encode_get, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)