from influxdb import InfluxDBClient
import requests
import time
import threading
import logging


class InfluxDBproxy:
    def __init__(self, dbhost: str, dbname: str, measurement_prefix: str):
        self.database = InfluxDBClient(dbhost, timeout=1, retries=1)
        self.dbname = dbname
        self.prefix = measurement_prefix
        self.isConnected = False
        self.isChecked = False

        self.logger = logging.getLogger('RKID.DBproxy')
        self.logger.setLevel(logging.DEBUG)

        self.check_connection()
        if not self.isConnected:
            self.logger.warning(f'Could not connect to database at {dbhost}')

        self.checkThread = threading.Thread(target=self.check_loop)
        self.checkThread.start()

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
        while True:
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
