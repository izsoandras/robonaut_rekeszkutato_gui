import tkinter
import logging
import my_gui.paramsetter.paramviews.paramview_factory as pv_factory
import my_mqtt.listeners.MyMQTTllistener as mml
import threading


class ParamFrame(tkinter.Frame):
    def __init__(self, parent, data_holder, msgs_recipe, client: mml.MyMQTTlistener, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)

        self.name = msgs_recipe.name
        self.msg_id = msgs_recipe['type']   # TODO: remove literal
        self.logger = logging.getLogger('paramframe_' + self.name)
        self.client = client
        self.dataholder =data_holder

        self.lb_name = tkinter.Label(self, text=self.name)
        self.lb_name.pack(side=tkinter.TOP)

        self.param_views = pv_factory.structString2paramView(self, msgs_recipe['format'], msgs_recipe['fields']) # TODO: remove literals
        for view in self.param_views.values():
            view.pack(side=tkinter.TOP)

        self.fr_buttons = tkinter.Frame(self, bd=5)
        self.btn_send = tkinter.Button(self.fr_buttons, text='Send', command=self.on_btn_send)
        self.btn_update = tkinter.Button(self.fr_buttons, text='Update', command=self.on_btn_update)
        self.btn_send.pack(side=tkinter.LEFT)
        self.btn_update.pack(side=tkinter.LEFT)
        self.fr_buttons.pack(side=tkinter.TOP)

    def on_btn_send(self):
        data = {
            'name':self.name
        }
        for key in self.param_views.keys():
            data[key] = self.param_views[key].get_new_value()

        wrkr = threading.Thread(target=self.client.send_message, args=(self.msg_id,data))
        wrkr.start()

    def on_btn_update(self):
        wrkr = threading.Thread(target=self.client.ask_update, args=(self.msg_id))
        wrkr.start()

    def update_view(self):
        data = self.dataholder.getData()
        if data is not None:
            for key in data.keys():
                self.param_views[key].set_view(data[key][-1])
