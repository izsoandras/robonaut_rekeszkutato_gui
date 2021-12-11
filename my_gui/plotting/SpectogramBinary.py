from .Spectogram import Spectogram
import numpy as np


class SpectogramBinary(Spectogram):
    def __init__(self, subplot, dholders: dict, recipe: dict, sample_num: int = 50, num_in_sample: int = 32):
        recipe['num_in_sample'] = num_in_sample
        Spectogram.__init__(self, subplot, dholders, recipe)

    def build_and_customize(self, recipe):
        super().build_and_customize(recipe)
        self.width = recipe['num_in_sample']
        self.data = np.indices((self.height, self.width)).sum(axis=0) % 2   # create checkboard like matrix
        self.quad = self.axes.pcolormesh(self.data)
        self.axs[recipe['lines'][0]['field']] = self.quad
        # self.animated.append(self.quad)


    def transform_data(self, data):
        new_data = [[int(x) for x in bin(d)[2:].zfill(self.width)][::-1] for d in data]
        return super().transform_data(new_data)
