import dataholders.DataHolder

class FixedDataholder(dataholders.DataHolder.DataHolder):
    def __init__(self, name, fields, size, views=None):
        dataholders.DataHolder.DataHolder.__init__(self, name, fields, size, views)
        self.data_buff = []

    def refreshData(self):
        replace_buff = []
        while not self.queue.empty():
            self.data_buff.append(self.queue.get())
            if len(self.data_buff) == self.size:
                replace_buff = self.data_buff
                self.data_buff = []

        if len(replace_buff) > 0:
            for field in self.fields:
                data = [rb[field] for rb in replace_buff]
                self.data[field] = data

