import logging
import threading
from clients.mqtt.listeners import ParamListener
import time
import dataholders.FifoDataholder


class Pinger(object):
    def __init__(self, mqtt_client: ParamListener, dataholders: dict, type_id: int, on_connection:list, interval=0.5, timeout=0.1):
        self.interval = interval
        self.timeout = timeout
        self.dataholder = dataholders[type_id]
        self.isConnected = False
        self.client = mqtt_client
        self.type_id = type_id
        self._stopped = True
        self.conn_callbacks = on_connection

        self.logger = logging.getLogger('RKID.pinger')
        self.check_thread = None

    def start_reqing(self):
        self._stopped = False
        self.check_thread = threading.Thread(target=self.ping_req)
        self.check_thread.start()

    def stop_reqing(self):
        self._stopped = True

    def join_reqing(self):
        self._stopped = True
        self.check_thread.join()
        self.check_thread = None

    def ping_req(self):
        while not self._stopped:
            self.client.ask_update(self.type_id)
            time.sleep(self.timeout)

            if self.dataholder.hasNew:
                self.dataholder.getData()
                if not self.isConnected:
                    self.logger.info('Connected to Car')
                    for func in self.conn_callbacks:
                        func()

                self.isConnected = True
            else:
                if self.isConnected:
                    self.logger.info('Lost connection to Car')

                self.isConnected = False

            time.sleep(self.interval - self.timeout)

