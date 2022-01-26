import tkinter
import logging
from .TelemetrySingleExtractFrame import TelemetrySingleExtractFrame
from tkinter import ttk


class TelemetryExtractFrame(tkinter.Frame):
    def __init__(self, parent, recipes, dataholders_by_name, *args, **kwargs):
        tkinter.Frame.__init__(self, parent,*args,**kwargs)
        self.logger = logging.getLogger('RKID.TelExtract')

        self.extract_frames = []

        sep = ttk.Separator(self, orient='vertical')
        sep.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=True, padx=10)
        for rec in recipes:
            self.extract_frames.append(TelemetrySingleExtractFrame(self, rec, dataholders_by_name[rec['name']]))
            self.extract_frames[-1].pack(side=tkinter.TOP, fill=tkinter.X, expand=True)
            sep = ttk.Separator(self, orient='horizontal')
            sep.pack(side=tkinter.TOP,fill=tkinter.X, expand=True,pady=10)

        self.continous_update()

    def update_view(self):
        for fr in self.extract_frames:
            fr.update_view()

    def continous_update(self):
        self.update_view()
        self.master.after(100, self.continous_update)
