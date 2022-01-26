import tkinter
import logging


class TelemetrySingleExtractFrame(tkinter.Frame):
    def __init__(self, parent, recipe, dataholder, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.dataholder = dataholder
        self.name = recipe["name"]
        self.labels = {}
        self.views = {}
        self.stvars = {}

        self.lb_name = tkinter.Label(self, text=self.name.upper())
        self.fr_views = tkinter.Frame(self)
        for idx, field in enumerate(recipe["fields"]):
            self.labels[field] = tkinter.Label(self.fr_views, text=field)
            self.stvars[field] = tkinter.StringVar()
            self.views[field] = tkinter.Entry(self.fr_views, state='readonly',
                                              textvariable=self.stvars[field],
                                              width=8, justify='left')

            self.labels[field].grid(row=idx, column=0, padx=10, sticky='E')
            self.views[field].grid(row=idx, column=1, padx=10, sticky='E')

        self.lb_name.pack(side=tkinter.TOP)
        self.fr_views.pack(side=tkinter.TOP,fill=tkinter.X, expand=True)

    def update_view(self):
        data = self.dataholder.getData()
        for key in self.views.keys():
            if type(data[key][-1]) == float:
                s = f'{data[key][-1]: .2f}'
            else:
                s = str(data[key][-1])
            self.stvars[key].set(s)
