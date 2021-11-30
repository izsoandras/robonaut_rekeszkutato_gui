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
        self.mqtt_client = mqtt.Client(name)
        self.name = name
        self.mqtt_client.on_message = self.on_message
        if username is not None and pwd is not None:
            self.mqtt_client.username_pw_set(username, pwd)

        self.broker = broker
        self.isConnected = False
        self.connectStatusLogged = False
        self._stop = False
        self.checkThread = None
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_subscribe = self._on_subscribe
        self.mqtt_client.on_unsubscribe = self._on_unsubscribe
        self.checkThread = threading.Thread(target=self._connection_thread)
        self.checkThread.start()
        # self.start_checking()

        self.topic = topic
        self.is_subscribed = False
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
        self.is_subscribed = True
        ret = self.mqtt_client.subscribe(self.topic)
        res = ret[0]
        # if res is mqtt.MQTT_ERR_SUCCESS:
        #     self.logger.info(f'Subscribed to: {self.topic}')

    def unsubscribe(self):
        self.mqtt_client.unsubscribe(self.topic)
        self.logger.info(f'Unsubscribed from: {self.topic}')

    def _connection_thread(self):
        while not self.isConnected and not self._stop:
            try:
                self.mqtt_client.connect(self.broker)
            except ConnectionRefusedError as cre:
                self.logger.error(str(cre))
            except TimeoutError as te:
                self.logger.error(str(te))

            time.sleep(3)

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
        self.logger.warning("Stopping connection checking")
        self._stop = True
        self.checkThread.join()
        self.checkThread = None
        self.logger.warning("Connection check stopped")

    def start_checking(self):
        self._stop = False
        self.checkThread = threading.Thread(target=self._keep_connection)
        self.checkThread.start()

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.logger.warning(f"Client {self.name} to broker: {self.broker}")
            self.isConnected = True
            if self.is_subscribed:
                self.subscribe()
        elif rc == 1:
            self.logger.warning(f"Client {self.name} couldn't connect to broker: {self.broker}\nReason: Connection refused. Incorrect protocol version.")
        elif rc == 2:
            self.logger.warning(
                f"Client {self.name} couldn't connect to broker: {self.broker}\nReason: Connection refused. Invalid client ID.")
        elif rc == 3:
            self.logger.warning(
                f"Client {self.name} couldn't connect to broker: {self.broker}\nReason: Connection refused. Server unavailable.")
        elif rc ==4:
            self.logger.warning(
                f"Client {self.name} couldn't connect to broker: {self.broker}\nReason: Connection refused. Incorrect username or password.")
        elif rc == 5:
            self.logger.warning(
                f"Client {self.name} couldn't connect to broker: {self.broker}\nReason: Connection refused. Not authorized.")

    def _on_disconnect(self, client, userdata, reasonCode):
        self.isConnected = False
        self.logger.warning(
            f"Client {self.name} lost connection to broker {self.broker}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        self.logger.warning(f"CLient subscribed on topic {self.topic}")
        pass

    def _on_unsubscribe(self, client, userdata, mid):
        self.logger.warning(f"CLient unsubscribed from topic {self.topic}")
        pass


