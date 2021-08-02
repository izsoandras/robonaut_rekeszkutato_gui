import paho.mqtt.client as mqtt
import abc


class MyMQTTlistener(metaclass=abc.ABCMeta):
    def __init__(self, msg_recipes, name: str, broker, topic: str, username: str = None, pwd: str = None, dataholders: dict = None):
        self.mqtt_client = mqtt.Client(name)
        self.mqtt_client.on_message = self.on_message
        if username is not None and pwd is not None:
            self.mqtt_client.username_pw_set(username, pwd)

        self.mqtt_client.connect(broker)
        self.mqtt_client.loop_start()

        self.dataholders = dataholders

        self.msg_coder = None
        self.payload_coders = None
        self.build_coders(msg_recipes)

    def build_coders(self, msg_recipes):
        
        pass

    def on_message(self, client, userdata, message):
        pass

    @abc.abstractmethod
    def on_msg_hook(self, client, userdata, message):
        pass

