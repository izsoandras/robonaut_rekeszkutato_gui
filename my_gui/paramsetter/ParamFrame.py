import tkinter
import logging


class ParamFrame(tkinter.Frame):
    def __init__(self, parent, data_holder, msgs_recipe, mqtt_client, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)

        self.name = msgs_recipe.name
        self.logger = logging.getLogger('paramframe_' + self.name)






