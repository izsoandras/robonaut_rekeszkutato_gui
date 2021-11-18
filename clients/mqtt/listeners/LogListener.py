import logging
import msg_codecs.payload_codecs.LogCoder
from .MyMQTTllistener import MyMQTTlistener


class LogListener(MyMQTTlistener):
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

    def __init__(self, name: str, src_name: str, msg_recipes: list, broker, topic: str, username: str = None, pwd: str = None):
        MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic, username, pwd)

        self.src_name = src_name
        self.robot_logger = logging.getLogger(src_name)
        self.robot_logger.setLevel(logging.DEBUG)

    def build_coders(self, msg_recipes):
        rec = msg_recipes[0]
        self.payload_coders = {
            rec['type']: msg_codecs.payload_codecs.LogCoder(rec['type'])  # TODO: remove literal
        }

    def on_message(self, client, userdata, message):
        type_id, payload = self.msg_coder.deconstruct_message(message.payload)
        data = self.payload_coders[type_id].decode(payload)
        if data['level'] < 1 or data['level'] > 5:
            self.robot_logger.log(data['level'], data['message'])
        else:
            self.robot_logger.log(LogListener.levels[data['level'] - 1], data['message'])  # TODO: remove literal
