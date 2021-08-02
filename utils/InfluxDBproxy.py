from influxdb import InfluxDBClient
import requests


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

    def check_connection(self):
        try:
            self.database.ping()
            return True
        except requests.exceptions.ConnectTimeout:
            return False

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

