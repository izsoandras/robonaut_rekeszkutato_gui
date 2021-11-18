import paho.mqtt.client as mqtt
import msg_codecs.frame_codecs
import msg_codecs.payload_codecs
import logging
from ...AbstractClient import AbstractClient


class MyMQTTlistener(AbstractClient):
    def __init__(self, msg_recipes: list, name: str, broker, topic: str, username: str = None, pwd: str = None,  dataholders: dict = None):
        AbstractClient.__init__(self, None, None, dataholders)
        self.mqtt_client = mqtt.Client(name)
        self.name = name
        self.mqtt_client.on_message = self.on_message
        if username is not None and pwd is not None:
            self.mqtt_client.username_pw_set(username, pwd)

        self.mqtt_client.connect(broker)
        self.topic = topic
        self.mqtt_client.loop_start()

        self.dataholders = dataholders

        self.msg_coder = msg_codecs.frame_codecs.RKIMessageCoder()  # TODO: configurable msg coder
        self.payload_coders = None
        self.build_coders(msg_recipes)

        self.logger = logging.getLogger(f'RKID.{name}')
        self.logger.setLevel(logging.DEBUG)

    def build_coders(self, msg_recipes):
        coders = {}
        for recipe in msg_recipes:
            coders[recipe['type']] = msg_codecs.payload_codecs.PayloadCoder(**recipe) # TODO: ne literal legyen

        self.payload_coders = coders

    def on_message(self, client, userdata, message):
        msg_type, payload = self.msg_coder.deconstruct_message(message.payload)
        data = self.payload_coders[msg_type].decode(payload)

        self.logger.debug(f'Message received in {client} on topic {message.topic}: {str(message.payload)}')

        if self.dataholders is not None:
            self.dataholders[msg_type].pushData(data)

        self.on_msg_hook(client, userdata, message, data)

    def on_msg_hook(self, client, userdata, msg_type, data):
        pass

    def subscribe(self):
        self.mqtt_client.subscribe(self.topic)
        self.logger.info(f'Subscribed to: {self.topic}')

    def unsubscribe(self):
        self.mqtt_client.unsubscribe(self.topic)
        self.logger.info(f'Unsubscribed from: {self.topic}')





