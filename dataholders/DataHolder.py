from queue import Queue
import abc
import logging


class DataHolder(metaclass=abc.ABCMeta):
    IDX = 'idx'

    def __init__(self, name, fields, size, views=None):
        if views is None:
            views = []

        self.name = name
        self.hasNew = False
        self.data = {}
        self.fields = fields
        self.size = size
        self.views = views
        self.queue = Queue()
        self.logger = logging.getLogger(f'DHs.{self.name}') # TODO: forget literal

        for field in fields:
            self.data[field] = [0] * size

        self.data['idx'] = list(range(-size, 0))

    def isNew(self):
        return self.hasNew

    @abc.abstractmethod
    def refreshData(self):
        pass

    def getData(self, key=None):
        if self.hasNew:
            self.hasNew = False # TODO: check thread safety
            self.refreshData()

        if key is None:
            return self.data
        else:
            try:
                return self.data[key]
            except KeyError:
                self.logger.warning(f'Couldn\'t find key {key}. {self.fields}')
                return None

    def pushData(self, newData: dict):
        del newData['name']  # TODO: remove literal
        if all(key in self.fields for key in newData.keys()):
            if all(field in list(newData.keys()) for field in self.fields):
                self.queue.put(newData)
                self.hasNew = True
            else:
                raise KeyError(
                    f'NewData does not have every key from fields. Fields: {self.fields}, Keys: {list(newData.keys())}')
        else:
            raise KeyError(
                f'NewData has keys that are not in fields. Fields: {self.fields}, Keys: {list(newData.keys())}')

    def alertAllViews(self):
        for view in self.views:
            view.setOld()

