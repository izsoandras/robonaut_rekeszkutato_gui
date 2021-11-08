import my_mqtt.listeners.MyMQTTllistener
import logging
import msg_codecs.payload_codecs.LogCoder


class LogListener(my_mqtt.listeners.MyMQTTllistener.MyMQTTlistener):
    def __init__(self, name: str, src_name: str, msg_recipes: list, broker, topic: str, username: str = None, pwd: str = None):
        my_mqtt.listeners.MyMQTTllistener.MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic, username, pwd)

        self.src_name = src_name
        self.robot_logger = logging.getLogger(src_name)
        self.robot_logger.setLevel(logging.DEBUG)

    def build_coders(self, msg_recipes):
        rec = msg_recipes[0]
        coders = {
            rec['type']: msg_codecs.payload_codecs.LogCoder(rec['type'])  # TODO: remove literal
        }

        self.msg_coder = msg_codecs.payload_codecs.LogCoder(rec['type'])

        self.payload_coders = coders

    def on_message(self, client, userdata, message):

        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        data = self.msg_coder.decode(message.payload)
        self.robot_logger.log(levels[data['level'] - 1], data['message'])  # TODO: remove literal
