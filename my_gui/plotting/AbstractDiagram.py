import abc
import matplotlib.pyplot
import dataholders.SeriesDataHolder
import logging
from matplotlib.patches import Ellipse


class AbstractDiagram(metaclass=abc.ABCMeta):

    def __init__(self, subplot: matplotlib.pyplot.Axes, dholders: dict, recipe: dict):
        self.axes = subplot
        self.axs = {}
        self.annots = {}
        self.dataholders = {}
        self.new_data = False
        self.logger = logging.getLogger(f'RKID.plot.{recipe["title"]}')  # TODO: remove literal

        for line_rec in recipe['lines']:
            msg_name = line_rec['message']
            try:
                self.dataholders[msg_name] = dholders[msg_name]  # TODO: update for different source for different lines
            except KeyError:
                self.logger.warning(f'Dataholders do not have element: {msg_name}')
                self.dataholders[msg_name] = dataholders.SeriesDataHolder.SeriesDataHolder('dummy', [], 10)

            self.dataholders[msg_name].add_view(self)

        if 'ylim' in recipe.keys():
            self.axes.set_ylim(recipe['ylim'])

        if 'title' in recipe.keys():
            self.axes.set_title(recipe['title'])

        self.has_legend = False

        self.build_and_customize(recipe)

        if self.has_legend:
            self.axes.legend(loc='upper left', fontsize='x-small')

        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        x_diff = xlim[1] - xlim[0]
        y_diff = ylim[1] - ylim[0]
        pos = ((xlim[0]+xlim[1])/2, ylim[0]+y_diff/40)
        self.blinker = matplotlib.patches.Ellipse(pos,x_diff/40, y_diff/40, facecolor='limegreen', zorder=10)
        self.axes.add_patch(self.blinker)
        self.animated = list(self.axs.values()) + list(self.annots.values()) + [self.blinker]

    def update_view(self):
        # old_datas = [self.axs[key].get_ydata() for key in self.axs.keys()]

        if self.new_data:
            self.blinker.set_visible(not self.blinker.get_visible())

        self.update_data()
        self.new_data = False

        # for idx, key in enumerate(self.axs.keys()):
        #     if not old_datas[idx] == self.axs[key].get_ydata():
        #         print("new data")

        return self.animated

    @abc.abstractmethod
    def update_data(self):
        pass

    @abc.abstractmethod
    def build_and_customize(self, recipe):
        pass

    def get_msg_for_field(self, field_name):
        for dh_key in self.dataholders.keys():
            if field_name in self.dataholders[dh_key].fields:
                return dh_key

        raise KeyError(f"Couldn't find field {field_name} in any dataholder of plot {self.axes.get_title()}")

    def setOld(self):
        self.new_data = True
