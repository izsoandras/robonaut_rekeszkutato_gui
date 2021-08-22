from .MyMQTTllistener import MyMQTTlistener
from utils.InfluxDBproxy import InfluxDBproxy
import logging
from datetime import datetime


class DatabbaseSaveListener(MyMQTTlistener):
    def __init__(self, dbproxy: InfluxDBproxy, msg_recipes: list, name: str, broker, topic: str, username: str = None,
                 pwd: str = None, dataholders: dict = None, meas_friendly_name=''):
        MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic, username, pwd, dataholders)

        self.db = dbproxy
        self.isPaused = True
        self.meas_friendly_name = meas_friendly_name
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

    def resume(self, measurement_friendly_name=None):
        if measurement_friendly_name is not None:
            self.meas_friendly_name=measurement_friendly_name

        self.db.prefix = f'{str(datetime.now())}_{self.meas_friendly_name}'
        self.isPaused = False
