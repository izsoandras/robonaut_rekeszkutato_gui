import tkinter
import logging
import my_gui.paramsetter.paramviews.paramview_factory as pv_factory
from clients.mqtt.listeners import ParamListener
import threading
import copy


class ParamFrame(tkinter.Frame):
    def __init__(self, parent, data_holder, msgs_recipe, client: ParamListener, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)

        self.name = msgs_recipe['name']   # TODO: remove literal
        self.msg_id = msgs_recipe['type']   # TODO: remove literal
        self.logger = logging.getLogger('RKID.paramframe.' + self.name)
        self.client = client
        self.dataholder =data_holder

        self.lb_name = tkinter.Label(self, text=self.name)
        self.lb_name.pack(side=tkinter.TOP)

        try:
            self.param_views = pv_factory.structString2paramView(self, msgs_recipe['format'], msgs_recipe['fields']) # TODO: remove literals

            for view in self.param_views.values():
                view.pack(side=tkinter.TOP, fill=tkinter.X)
                view.tb_set_value.bind('<Return>',self.on_enter_press)

            self.fr_buttons = tkinter.Frame(self, bd=5)
            self.btn_send = tkinter.Button(self.fr_buttons, text='Send', command=self.on_btn_send)
            self.btn_move = tkinter.Button(self.fr_buttons, text='\u2B9C', command=self.on_btn_move)
            self.btn_refresh = tkinter.Button(self.fr_buttons, text='Refresh', command=self.on_btn_update)
            self.btn_send.pack(side=tkinter.LEFT)
            self.btn_move.pack(side=tkinter.LEFT)
            self.btn_refresh.pack(side=tkinter.LEFT)
            self.fr_buttons.pack(side=tkinter.TOP)
        except NotImplementedError as nie:
            self.logger.error(nie)
            self.param_views = {}

    def on_btn_send(self):
        wrkr = threading.Thread(target=self.send_data())
        wrkr.start()

    def on_enter_press(self, event):
        self.on_btn_send()
        self.logger.debug(f"Enter pressed in {self.name}")

    def get_new_data(self):
        data = {
            'name': self.name
        }
        for key in self.param_views.keys():
            data[key] = self.param_views[key].get_new_value()

        return data

    def get_current_data(self):
        data = {
            'name': self.name
        }
        for key in self.param_views.keys():
            data[key] = self.param_views[key].get_current_value()

        return data

    def send_data(self):
        try:
            data = self.get_new_data()
            self.client.send_message(self.msg_id, data)
        except ValueError as ve:
            self.logger.error(ve)

    def on_btn_update(self):
        wrkr = threading.Thread(target=self.ask_update)
        wrkr.start()

    def on_btn_move(self):
        for pv in self.param_views.values():
            pv.set_new_value(pv.get_current_value())

    def ask_update(self):
        self.client.ask_update(self.msg_id)

    def update_view(self):
        if self.dataholder.hasNew:
            data = copy.deepcopy( self.dataholder.getData())

            # TODO: miert van benne idx?
            if 'idx' in data.keys():
                data.pop('idx')
            if data is not None:
                for key in data.keys():
                    try:
                        self.param_views[key].set_view(data[key][-1])
                    except KeyError as ke:
                        print(ke)
