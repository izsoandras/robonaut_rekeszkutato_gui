import matplotlib.pyplot
import my_gui.plotting.AbstractDiagram
import numpy as np


class CompassDiagram(my_gui.plotting.AbstractDiagram.AbstractDiagram):
    TAB_PALETTE = ['tab:blue', 'tab:orange', 'tab:green']  # TODO: outsource

    def __init__(self, subplot: matplotlib.pyplot.PolarAxes, dholders: dict, recipe: dict):
        recipe['ylim'] = [0, 1]
        my_gui.plotting.AbstractDiagram.AbstractDiagram.__init__(self, subplot, dholders, recipe)

    def build_and_customize(self, recipe):
        self.axes.set_theta_zero_location("N")
        self.axes.set_xticks(np.pi / 180. * np.linspace(-180, 180, 8, endpoint=False))
        self.axes.set_thetalim(np.pi, -np.pi)
        self.axes.set_theta_direction(-1)
        self.axes.set_yticklabels([])

        for idx, line_rec in enumerate(recipe['lines']):  # TODO: remove literal
            data = self.dataholder.getData(line_rec['field'])  # TODO: remove literal
            if data is not None:
                rad = np.deg2rad(data[-1])
                self.axs[line_rec['field']], = self.axes.plot([rad, rad], [0, 1])  # TODO: remove literal

                # if 'legend' in line_rec.keys():
                #     self.axs[line_rec['field']].set_label(line_rec['field'])
                #     self.has_legend = True
                #
                # self.annots[line_rec['field']] = self.axes.annotate(f'{data[-1]:.2f}', xy=(-49, 0),
                #                                                     # TODO: remove literal
                #                                                     xytext=(-60, -60 + idx * 10),
                #                                                     textcoords='offset points', animated=True,
                #                                                     color=CompassDiagram.TAB_PALETTE[idx],
                #                                                     weight='heavy')

    def update_data(self):
        for key in self.axs.keys():
            data = self.dataholder.getData(key)[-1]
            rad = np.deg2rad(data)
            self.axs[key].set_xdata([rad, rad])
            # self.annots[key].set_text(f'{data:.2f}')
