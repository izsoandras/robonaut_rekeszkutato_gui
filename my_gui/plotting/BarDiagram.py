import matplotlib.pyplot
import my_gui.plotting.AbstractDiagram
import numpy as np


class BarDiagram(my_gui.plotting.AbstractDiagram.AbstractDiagram):
    def __init__(self, subplot: matplotlib.pyplot.Axes, dholders: dict, recipe: dict):
        my_gui.plotting.AbstractDiagram.AbstractDiagram.__init__(self, subplot, dholders, recipe)
        self.animated = []
        for key in self.axs.keys():
            self.animated.extend(self.axs[key].patches)

    def build_and_customize(self, recipe):
        for line_rec in recipe['lines']:  # TODO: remove literal
            s = self.dataholder.size
            if s % 2 == 0:
                ys = [1, 0] * int(s/2)
            else:
                ys = [1, 0] * int((s-1)/2) + [1]

            self.axs[line_rec['field']] = self.axes.bar(np.arange(0, s, 1), ys)

    def update_data(self):
        for key in self.axs.keys():
            datas = self.dataholder.getData(key)
            for data, rect in zip(datas, self.axs[key]):
                rect.set_height(data)


