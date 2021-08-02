from influxdb import InfluxDBClient
import requests
import time
import threading
import logging


class InfluxDBproxy:
    def __init__(self, dbhost: str, dbname: str, measurement_prefix: str):
        self.database = InfluxDBClient(dbhost, timeout=1, retries=1)
        self.prefix = measurement_prefix
        self.isConnected = False

        dbs = self.database.get_list_database()
        # create database if not exists
        if not {'name': dbname} in dbs:
            self.database.create_database(dbname)

        # switch to database
        self.database.switch_database(dbname)

        self.logger = logging.getLogger('DBproxy')
        self.logger.setLevel(logging.DEBUG)
        self.checkThread = threading.Thread(target=self.check_loop)
        self.checkThread.start()

    def check_connection(self):
        try:
            self.database.ping()
            if not self.isConnected:
                self.logger.warning('Connected to database')

            self.isConnected = True
            return True
        except requests.exceptions.ConnectTimeout:
            if self.isConnected:
                self.logger.warning('Disconnected from database')

            self.isConnected = False
            return False

    def check_loop(self):
        self.check_connection()
        time.sleep(3)

    def save_data(self, data: dict):
        name = data.pop('name')
        db_json = [{
            "measurement": self.prefix + name,
            "fields": data,
            "tags": {}
        }]

        if self.isConnected:
            try:
                self.database.write_points(db_json)
                return True
            except requests.exceptions.ConnectTimeout:
                return False
        else:
            return False

