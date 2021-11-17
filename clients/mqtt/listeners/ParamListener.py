import paho.mqtt.client as mqtt
import msg_codecs.frame_codecs
import msg_codecs.payload_codecs
import logging
from .MyMQTTllistener import MyMQTTlistener


class ParamListener(MyMQTTlistener):
    def __init__(self, msg_recipes: list, name: str, broker, topic_receive: str, topic_send: str, username: str = None, pwd: str = None,  dataholders: dict = None):
        MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic_receive, username, pwd,  dataholders)
        self.topic_send = topic_send

    def on_msg_hook(self, client, userdata, msg_type, data):
        self.logger.debug(f"Parameter received: {self.name}")

    def send_message(self, type_id: int, data: dict):
        coder = self.payload_coders[type_id]

        try:
            payload = coder.encode(data)
        except KeyError as ex:
            self.logger.error(ex)
            return

        msg = self.msg_coder.construct_message(type_id, payload)

        self.mqtt_client.publish(self.topic_send, msg)
        self.logger.debug(f"Data {data} sent on topic {self.topic_send} as {msg}")

    def ask_update(self, type_id: int):
        msg = self.msg_coder.construct_message(type_id, bytes(0))
        self.mqtt_client.publish(self.topic_send, msg)
        self.logger.debug(f"Asked for updates through {self.topic_send} for msg {type_id}")
