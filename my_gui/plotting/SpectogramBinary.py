from .Spectogram import Spectogram


class SpectogramBinary(Spectogram):
    def __init__(self, subplot, dholders: dict, recipe: dict, sample_num: int = 50, num_in_sample: int = 32):
        Spectogram.__init__(self, subplot, dholders, recipe, sample_num, num_in_sample)

    def transform_data(self, data):
        new_data = [[int(x) for x in bin(d)[2:].zfill(self.width)][::-1] for d in data]
        return super().transform_data(new_data)
