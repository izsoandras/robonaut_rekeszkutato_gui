import logging
from ..AbstractClient import AbstractClient
import threading
import serial
import time
from msg_codecs.frame_codecs.RKIUartCoder import RKIUartCoder
import logging


class RKIUartListener(AbstractClient):
    def __init__(self, name: str, port: str, msg_coder: RKIUartCoder, payload_coders: dict, dataholders: dict, baudrate=115200):
        AbstractClient.__init__(self, msg_coder, payload_coders, dataholders)
        self.name = name
        self.port = serial.Serial(port, baudrate)
        self.logger = logging.getLogger(f'RKID.{name}')
        self.thread = None
        self.running = False
        self.logger = logging.getLogger(self.name)

    def listen_thread(self):
        while self.running:
            while self.port.in_waiting > 0:
                b = self.port.read()
                if self.msg_coder.next_byte(b):
                    coder = self.payload_coders[self.msg_coder.decoder.type]
                    data = coder.decode(self.msg_coder.decoder.data[0:self.msg_coder.decoder.length])

                    if self.dataholders is not None:
                        self.dataholders[self.msg_coder.decoder.type].pushData(data)

            time.sleep(0.01)

    def subscribe(self):
        self.running = True

        if self.thread is None:
            self.thread = threading.Thread(target=self.listen_thread)
            self.thread.start()

    def unsubscribe(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()

    def send_message(self, type: int, data: dict):
        coder = self.payload_coders[type]

        try:
            payload = coder.encode(data)
        except KeyError as ex:
            self.logger.error(ex)
            return

        msg = self.msg_coder.construct_message(type, payload)

        self.port.write(msg)
        self.logger.debug(f"Data {data} sent on serial {self.port.name} as {msg}")

    def ask_update(self, type: int):
        msg = self.msg_coder.construct_message(type, bytes(0))
        self.port.write(msg)
        self.logger.debug(f"Asked for updates on serial {self.port.name} for msg {type}")