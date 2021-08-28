import my_mqtt.listeners.MyMQTTllistener
import logging
import my_mqtt.general.LogCoder


class LogListener(my_mqtt.listeners.MyMQTTllistener.MyMQTTlistener):
    def __init__(self, name: str, src_name: str, msg_recipes: list, broker, topic: str, username: str = None, pwd: str = None):
        my_mqtt.listeners.MyMQTTllistener.MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic, username, pwd)

        self.src_name = src_name
        self.robot_logger = logging.getLogger(src_name)

    def build_coders(self, msg_recipes):
        rec = msg_recipes[0]
        coders = {
            rec['type']: my_mqtt.general.LogCoder.LogCoder(rec['type'])  # TODO: remove literal
        }

        self.payload_coders = coders

    def on_msg_hook(self, client, userdata, message, data):
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        self.robot_logger.log(levels[data['level'] - 1], data['message'])  # TODO: remove literal
