from DataHolder import DataHolder


class SeriesDataHolder(DataHolder):
    def __init__(self, fields, size, views=None):
        DataHolder.__init__(self,fields, size, views)

    def refreshData(self):
        new_data = []
        while not self.queue.empty():
            new_data.append(self.queue.get())

        new_num = len(new_data)
        idx_skip = 0
        if new_num > self.size:
            new_data = new_data[-self.size:]
            idx_skip = new_num - self.size
            new_num = self.size

        remain_num = self.size - new_num
        for field in self.fields:
            new_field_data = [nd[field] for nd in new_data]
            if remain_num > 0:
                self.data[field] = self.data[field][-remain_num:]
                self.data[field].extend(new_field_data)
            else:
                self.data[field] = new_field_data

        new_idxs_start = self.data[DataHolder.IDX][-1] + 1 + idx_skip
        new_idxs = list(range(new_idxs_start, new_idxs_start + new_num))
        if remain_num > 0:
            self.data[DataHolder.IDX] = self.data[DataHolder.IDX][-remain_num:]
            self.data[DataHolder.IDX].extend(new_idxs)
        else:
            self.data[DataHolder.IDX] = new_idxs

