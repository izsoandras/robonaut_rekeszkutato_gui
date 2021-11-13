from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation
import matplotlib.pyplot
import dataholders.SeriesDataHolder
import logging
import my_gui.plotting.AbstractDiagram


class LineDiagram(my_gui.plotting.AbstractDiagram.AbstractDiagram):
    LINES = 'lines'
    YLIM = 'ylim'
    FIELD = 'field'
    LEGEND = 'legend'

    TAB_PALETTE = ['tab:blue', 'tab:orange', 'tab:green']

    def __init__(self, subplot: matplotlib.pyplot.Axes, dholders: dict, recipe: dict):
        my_gui.plotting.AbstractDiagram.AbstractDiagram.__init__(self, subplot, dholders, recipe)

    def build_and_customize(self, recipe):
        keys = list(self.dataholders.keys())
        if all(self.dataholders[keys[0]].size == self.dataholders[curr_key].size for curr_key in keys[1:]):
            datanum = self.dataholders[keys[0]].size
        else:
            raise ValueError(f"Not all dataholders has the same length in plot {self.axes.get_title()}")

        self.axes.set_xlim([-datanum + 1, 0])
        self.axes.set_xticklabels([])
        for idx, line_rec in enumerate(recipe[LineDiagram.LINES]):
            data = self.dataholders[line_rec["message"]].getData(line_rec[LineDiagram.FIELD])   # TODO: remove literal
            if data is not None:
                self.axs[line_rec[LineDiagram.FIELD]], = self.axes.plot(list(range(-datanum + 1, 1)),
                                                                        data)

                if LineDiagram.LEGEND in line_rec.keys():
                    self.axs[line_rec[LineDiagram.FIELD]].set_label(line_rec[LineDiagram.LEGEND])
                    self.has_legend = True

                self.annots[line_rec[LineDiagram.FIELD]] = self.axes.annotate(f'{data[-1]:.2f}', xy=(-49, 0),
                                                                              xytext=(1, 2 + idx * 10),
                                                                              textcoords='offset points', animated=True,
                                                                              color=LineDiagram.TAB_PALETTE[idx],
                                                                              weight='heavy')

    def update_data(self):
        for key in self.axs.keys():
            dh_key = self.get_msg_for_field(key)

            data = self.dataholders[dh_key].getData(key)

            self.axs[key].set_ydata(data)
            self.annots[key].set_text(f'{data[-1]:.2f}')

