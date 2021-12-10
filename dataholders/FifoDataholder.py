from .DataHolder import DataHolder


class FifoDataholder(DataHolder):
    def __init__(self, name, fields, maxSize, views=None):
        DataHolder.__init__(self, name, fields, maxSize, views)

    def refreshData(self):
        new_data = []
        while not self.queue.empty():
            new_data.append(self.queue.get())

        new_num = len(new_data)

        if len(self.data.get(len(list(self.data.keys())))) + new_num < self.size:
            for key in self.data.keys():
                self.data[key].append()

    def getData(self, key=None):
        data = {}
        if key is None:
            for key in self.data.keys():
                data[key] = self.data[key].pop()
        else:
            data[key] = self.data[key].pop()

        return data