from .MyMQTTllistener import MyMQTTlistener
from utils.InfluxDBproxy import InfluxDBproxy
import logging


class DatabbaseSaveListener(MyMQTTlistener):
    def __init__(self, dbproxy: InfluxDBproxy, msg_recipes: list, name: str, broker, topic: str, username: str = None,
                 pwd: str = None, dataholders: dict = None):
        MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic, username, pwd, dataholders)

        self.db = dbproxy
        self.isPaused = True
        self.logger = logging.getLogger('DBlistener')
        self.logger.setLevel(logging.DEBUG)

    def on_msg_hook(self, client, userdata, msg_type, data):
        if not self.isPaused:
            if self.db.save_data(data):
                self.logger.debug('Data saved!')
            else:
                self.logger.warning('Data could not be saved!')

    def pause(self):
        self.isPaused = True

    def resume(self):
        self.isPaused = False
