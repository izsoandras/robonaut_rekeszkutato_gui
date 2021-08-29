import abc
import matplotlib.pyplot
import dataholders.SeriesDataHolder
import logging


class AbstractDiagram(metaclass=abc.ABCMeta):

    def __init__(self, subplot: matplotlib.pyplot.Axes, dholders: dict, recipe: dict):
        self.axes = subplot
        self.axs = {}
        self.annots = {}
        self.logger = logging.getLogger(f'RKID.plot.{recipe["title"]}')  # TODO: remove literal

        msg_name = recipe['lines'][0]['message']
        try:
            self.dataholder = dholders[msg_name]  # TODO: update for different source for different lines
        except KeyError:
            self.logger.warning(f'Dataholders do not have element: {msg_name}')
            self.dataholder = dataholders.SeriesDataHolder.SeriesDataHolder('dummy', [], 10)

        if 'ylim' in recipe.keys():
            self.axes.set_ylim(recipe['ylim'])

        if 'title' in recipe.keys():
            self.axes.set_title(recipe['title'])

        self.has_legend = False

        self.build_and_customize(recipe)

        if self.has_legend:
            self.axes.legend(loc='upper left', fontsize='x-small')
        self.animated = list(self.axs.values()) + list(self.annots.values())

    def update_view(self):
        self.update_data()
        return self.animated

    @abc.abstractmethod
    def update_data(self):
        pass

    @abc.abstractmethod
    def build_and_customize(self, recipe):
        pass

