import paho.mqtt.client as mqtt
import msg_codecs.frame_codecs
import msg_codecs.payload_codecs
import logging
from ...AbstractClient import AbstractClient
import time
import threading
import random


class MyMQTTlistener(AbstractClient):
    def __init__(self, msg_recipes: list, name: str, broker, topic: str, username: str = None, pwd: str = None,  dataholders: dict = None):
        AbstractClient.__init__(self, None, None, dataholders)
        self.mqtt_client = mqtt.Client(name+f" {str(random.randint(0,100))}")
        self.name = name
        self.mqtt_client.on_message = self.on_message
        if username is not None and pwd is not None:
            self.mqtt_client.username_pw_set(username, pwd)

        self.broker = broker
        self.isConnected = False
        self.connectStatusLogged = False
        self._stop = False
        self.checkThread = None
        self.mqtt_client.connect(self.broker)
        # self.start_checking()

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

    def _keep_connection(self):
        while not self._stop:
            if not self.mqtt_client.is_connected():
                try:
                    self.mqtt_client.connect(self.broker)

                    if not self.isConnected or not self.connectStatusLogged:
                        self.logger.info(f"Client {self.name} to broker: {self.broker}")
                        self.isConnected = True
                        self.connectStatusLogged = True
                        self.mqtt_client.loop_start()
                except TimeoutError as te:
                    if self.isConnected or not self.connectStatusLogged:
                        self.logger.warning(f"Client {self.name} lost connection to broker {self.broker} (timeout). Check if network is available.")
                        self.isConnected = False
                        self.connectStatusLogged = True

                except ConnectionRefusedError as cre:
                    if self.isConnected or not self.connectStatusLogged:
                        self.logger.warning(f"Client {self.name} lost connection to broker {self.broker} (refused). Check if broker is running.")
                        self.isConnected = False
                        self.connectStatusLogged = True

            time.sleep(0.5)

    def stop_checking(self):
        self._stop = True
        self.checkThread.join()
        self.checkThread = None

    def start_checking(self):
        self._stop = False
        self.checkThread = threading.Thread(target=self._keep_connection)
        self.checkThread.start()




