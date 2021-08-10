from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation
import matplotlib.pyplot
import dataholders.SeriesDataHolder
import logging


class LineDiagram:
    LINES = 'lines'
    YLIM = 'ylim'
    FIELD = 'field'
    LEGEND = 'legend'

    TAB_PALETTE = ['tab:blue', 'tab:orange', 'tab:green']

    def __init__(self, subplot: matplotlib.pyplot.Axes, dholders: dict, recipe: dict):
        self.axes = subplot
        self.axs = {}
        self.annots = {}
        self.logger = logging.getLogger(f'plot.{recipe["title"]}')  # TODO: remove literal

        msg_name = recipe['lines'][0]['message']
        try:
            self.dataholder = dholders[msg_name]  # TODO: update for different source for different lines
        except KeyError:
            self.logger.warning(f'Dataholders do not have element: {msg_name}')
            self.dataholder = dataholders.SeriesDataHolder.SeriesDataHolder('dummy', [], 10)

        datanum = self.dataholder.size
        self.axes.set_xlim([-datanum + 1, 0])
        if LineDiagram.YLIM in recipe.keys():
            self.axes.set_ylim(recipe[LineDiagram.YLIM])

        if 'title' in recipe.keys():
            self.axes.set_title(recipe['title'])

        has_legend = False
        for idx, line_rec in enumerate(recipe[LineDiagram.LINES]):
            data = self.dataholder.getData(line_rec[LineDiagram.FIELD])
            if data is not None:
                self.axs[line_rec[LineDiagram.FIELD]], = self.axes.plot(list(range(-datanum + 1, 1)),
                                                                        data)

                if LineDiagram.LEGEND in line_rec.keys():
                    self.axs[line_rec[LineDiagram.FIELD]].set_label(line_rec[LineDiagram.LEGEND])
                    has_legend = True

                self.annots[line_rec[LineDiagram.FIELD]] = self.axes.annotate(f'{data[-1]:.2f}', xy=(-49, 0),
                                                                              xytext=(1, 2 + idx * 10),
                                                                              textcoords='offset points', animated=True,
                                                                              color=LineDiagram.TAB_PALETTE[idx],
                                                                              weight='heavy')

        if has_legend:
            self.axes.legend()

        self.animated = list(self.axs.values()) + list(self.annots.values())

    def update_view(self):
        if self.dataholder.hasNew:
            for key in self.axs.keys():
                data = self.dataholder.getData(key)
                self.axs[key].set_ydata(data)
                self.annots[key].set_text(f'{data[-1]:.2f}')

            return self.animated
        else:
            return []
