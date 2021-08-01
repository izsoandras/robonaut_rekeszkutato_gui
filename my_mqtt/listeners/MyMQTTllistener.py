import paho.mqtt.client as mqtt
import abc


class MyMQTTlistener(metaclass=abc.ABCMeta):
    def __init__(self, name: str, broker, topic: str, username: str = None, pwd: str = None):
        self.mqtt_client = mqtt.Client(name)
        self.mqtt_client.on_message = self.on_message
        if username is not None and pwd is not None:
            self.mqtt_client.username_pw_set(username, pwd)

        self.mqtt_client.connect(broker)
        self.mqtt_client.loop_start()

    @abc.abstractmethod
    def on_message(self, client, userdata, message):
        pass

