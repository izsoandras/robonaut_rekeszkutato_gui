from .AbstractDiagram import AbstractDiagram
import matplotlib.pyplot
import numpy as np
import dataholders.SeriesDataHolder


class Spectogram(AbstractDiagram):

    def __init__(self, subplot, dholders: dict, recipe: dict, sample_num: int = 50, num_in_sample: int = 32):
        self.quad = None
        self.idx = 0

        if('flipud' in recipe.keys()):
            self.flipud = recipe['flipud']
        else:
            self.flipud = False

        if('fliplr' in recipe.keys()):
            self.fliplr = recipe['fliplr']
        else:
            self.fliplr = False

        self.width = num_in_sample
        self.height = sample_num
        self.data = np.zeros((self.width,self.height))
        AbstractDiagram.__init__(self, subplot, dholders, recipe)

        self.animated = [self.quad]
        if len(recipe['lines']) > 1:
            raise ValueError("Too much lines. Spectrogram can only display 1 dataset")

    def build_and_customize(self, recipe):

        dh = list(self.dataholders.values())[0]
        self.data = np.indices((self.height, self.width)).sum(axis=0) % 2   # create checkboard like matrix
        self.quad = self.axes.pcolormesh(self.data)
        self.axs[recipe['lines'][0]['field']] = self.quad

    def transform_data(self, data):
        mtx_data = np.array(data)

        if self.flipud:
            mtx_data = np.flipud(mtx_data)

        if self.fliplr:
            mtx_data = np.fliplr(self.fliplr)

        return mtx_data

    def update_data(self):
        data_key = list(self.axs.keys())[0]
        # self.data = - self.data
        # self.data = self.data + 1
        # self.data = np.zeros((self.height, self.width))
        # self.data[self.idx,:] = self.data[self.idx,:] + 1
        # self.idx = (self.idx + 1) % self.height

        for key in self.dataholders.keys():
            self.data = self.transform_data(self.dataholders[key].getData(data_key))

            self.quad.set_array(self.data.ravel())
