import paho.mqtt.client as mqtt
import abc
import my_mqtt.general
import logging


class MyMQTTlistener(metaclass=abc.ABCMeta):
    def __init__(self, msg_recipes: list, name: str, broker, topic: str, username: str = None, pwd: str = None,  dataholders: dict = None):
        self.mqtt_client = mqtt.Client(name)
        self.mqtt_client.on_message = self.on_message
        if username is not None and pwd is not None:
            self.mqtt_client.username_pw_set(username, pwd)

        self.mqtt_client.connect(broker)
        self.topic = topic
        self.mqtt_client.loop_start()

        self.dataholders = dataholders

        self.msg_coder = my_mqtt.general.RKIMessageCoder()
        self.payload_coders = None
        self.build_coders(msg_recipes)

        self.logger = logging.getLogger(f'RKID.{name}')
        self.logger.setLevel(logging.DEBUG)

    def build_coders(self, msg_recipes):
        coders = {}
        for recipe in msg_recipes:
            coders[recipe['type']] = my_mqtt.general.PayloadCoder(**recipe) # TODO: ne literal legyen

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

    def send_message(self, type: int, data: dict):
        coder = self.payload_coders[type]

        try:
            payload = coder.encode(data)
        except KeyError as ex:
            self.logger.error(ex)
            return

        msg = self.msg_coder.construct_message(type, payload)

        self.mqtt_client.publish(self.topic, msg)
        self.logger.debug(f"Data {data} sent on topic {self.topic} as {msg}")



