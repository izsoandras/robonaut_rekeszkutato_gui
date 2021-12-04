from influxdb import InfluxDBClient
import requests
import time
import threading
import logging
from queue import Queue


class InfluxDBproxy:
    def __init__(self, dbhost: str, dbname: str, measurement_prefix: str):
        self.database = InfluxDBClient(dbhost, timeout=1, retries=1)
        self.dbname = dbname
        self.prefix = measurement_prefix
        self.isConnected = False
        self.isChecked = False
        self._stop = False

        self._data_queue = Queue()
        self._run_consumer = False
        self._consumer_thread = None

        self.logger = logging.getLogger('RKID.DBproxy')
        self.logger.setLevel(logging.DEBUG)

        self.check_connection()
        if not self.isConnected:
            self.logger.warning(f'Could not connect to database at {dbhost}')

        self.checkThread = threading.Thread(target=self.check_loop)
        self.checkThread.start()

    def stop_checking(self):
        self.logger.info("Stopping database proxy")
        self._stop = True
        if self.checkThread is not None:
            self.checkThread.join()
            self.checkThread = None
            self.logger.info("Database proxy stopped")

    def check_connection(self):
        self._perform_on_db(self.database.ping)
        return self.isConnected

    def _set_connected(self):
        if not self.isConnected:
            self.logger.warning('Connected to database')
            self.isConnected = True

    def _set_disconnected(self):
        if self.isConnected:
            self.logger.warning('Disconnected from database')
            self.isConnected = False

    def check_loop(self):
        while not self._stop:
            prev_status = self.isChecked
            new_status = self.check_connection()

            if not prev_status and new_status:
                self.prepare_db()

            time.sleep(3)

    def prepare_db(self):
        dbs = self.database.get_list_database()
        # create database if not exists
        if not {'name': self.dbname} in dbs:
            self.database.create_database(self.dbname)

        # switch to database
        self.database.switch_database(self.dbname)
        self.isChecked = True

    def save_data(self, data: dict):
        name = data.pop('name')
        db_json = [{
            "measurement": self.prefix + '_' + name,
            "fields": data,
            "tags": {}
        }]

        if self.isConnected:
            try:
                self.database.write_points(db_json)
                return True
            except requests.exceptions.ConnectTimeout:
                self.isChecked = False
                self.logger.warning('Connection lost to DB')
                return False
        else:
            return False

    def get_list_measurements(self):
        if self.isConnected:
            measurements = self._perform_on_db(self.database.get_list_measurements)

            names = []
            for measurement in measurements:
                names.append(measurement['name'])

            return names

        raise ConnectionError("Isn't connected to database!")

    def get_measurement(self, measurement_name: str):
        # influxdb  only supports bind params in WHERE clause
        # https://docs.influxdata.com/influxdb/v1.7/tools/api/#bind-parameters
        return self._perform_on_db(self.database.query,
                                   query=f'SELECT * FROM "{measurement_name}"')

    def delete_measurement(self, measurement_name: str):
        self._perform_on_db(self.database.drop_measurement, measurement_name)

    def _perform_on_db(self, function, *args, **kwargs):
        try:
            ret = function(*args, **kwargs)
            self._set_connected()
            return ret
        except requests.exceptions.ConnectTimeout:
            self._set_disconnected()

    def push_data(self, data):
        self._data_queue.put(data)

    def _consumer_function(self):
        while self._run_consumer:
            msg_num = 0
            line_protocol_data = []
            while not self._data_queue.empty():
                while msg_num < 5000 and not self._data_queue.empty():
                    data = self._data_queue.get()
                    line_protocol_data.append(self.data2lineprotocol(data))
                try:
                    self.database.write_points(line_protocol_data, protocol='line')
                except requests.exceptions.ConnectTimeout:
                    self.logger.warning('Connection lost to DB')

            time.sleep(0.010)

    def data2lineprotocol(self, data: dict):
        name = data.pop('name')
        measurement = self.prefix + '_' + name
        measurement = measurement.replace(' ', '_')

        fields = [f'{str(key)}={str(data[key])}'.replace(' ','_') for key in data.keys()]
        line = f'{measurement} {",".join(fields)}'
        return line

    def start_consumer(self):
        self._consumer_thread = threading.Thread(target=self._consumer_function)
        self._run_consumer = True
        self._consumer_thread.start()

    def stop_consumer(self):
        self._run_consumer = False
        if self._consumer_thread is not None:
            self._consumer_thread.join()

            self._consumer_thread = None
