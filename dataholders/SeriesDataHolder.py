from DataHolder import DataHolder


class SeriesDataHolder(DataHolder):
    def __init__(self, field, size, views):
        DataHolder.__init__(field, size, views)

    def refreshData(self):
        new_data = []
        while not self.queue.empty():
            new_data.append(self.queue.get())

        new_num = len(new_data)
        if new_num > self.size:
            new_data = new_data[-self.size:]
            new_num = self.size

        new_idxs_start = self.data[DataHolder.IDX][-1]
        new_data[DataHolder.IDX] = list(range(new_idxs_start, new_idxs_start + new_num))

        remain_num = self.size - new_num
        for field in self.fields:
            self.data[field] = self.data[field][-remain_num:]
            self.data[field].extend(new_data[field])

