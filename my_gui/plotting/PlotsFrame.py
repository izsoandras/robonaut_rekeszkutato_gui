import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation
import matplotlib.pyplot
import LineDiagram
import CompassDiagram
import BarDiagram


class PlotsFrame(tkinter.Frame):
    def __init__(self, dataholders, recipe, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.fig = Figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.ani = matplotlib.animation.FuncAnimation(self.fig, self.update_view, interval=recipe['update_period'], blit=True) # TODO: remove literal

        self.plots = []

        layout = recipe['layout']  # TODO: kiszervezni
        rec_num = len(recipe['plots'])
        for idx in range(layout[0] * layout[1]):
            if idx < rec_num:
                plot_rec = recipe['plots'][idx]  # TODO: kiszervezni
                if plot_rec['type'] == 'compass':  # TODO: kiszervezni
                    axes = self.fig.add_subplot(layout[0], layout[1], idx+1, projection='polar')
                    new_plot = CompassDiagram.CompassDiagram(axes, dataholders, plot_rec)
                elif plot_rec['type'] == 'bar':
                    axes = self.fig.add_subplot(layout[0], layout[1], idx+1)
                    new_plot = BarDiagram.BarDiagram(axes, dataholders, plot_rec)
                else:
                    axes = self.fig.add_subplot(layout[0], layout[1], idx+1)
                    new_plot = LineDiagram.LineDiagram(axes, dataholders, plot_rec)

                self.plots.append(new_plot)

        self.fig.tight_layout()

    def update_view(self, frame):
        updateables = []
        for plot in self.plots:
            upd = plot.update_view()
            updateables.extend(upd)

        return updateables

