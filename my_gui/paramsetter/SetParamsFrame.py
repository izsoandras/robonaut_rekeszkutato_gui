import my_gui.InheritableScrollableFrame
import logging
import tkinter
import my_gui.paramsetter.ParamFrame as pf
import threading
import yaml
from tkinter import filedialog


class SetParamsFrame(my_gui.InheritableScrollableFrame.ScrollableFrame):
    def __init__(self, parent, msgs_recipes: list, client, dataholders_by_id: dict, update_time: int = 20, *args, **kwargs):
        my_gui.InheritableScrollableFrame.ScrollableFrame.__init__(self,parent, *args,**kwargs)
        self.update_time = update_time
        self.logger = logging.getLogger('Paramsframe')

        self.paramframes = []
        for rec in msgs_recipes:
            if rec['fields']:
                self.paramframes.append(pf.ParamFrame(self, dataholders_by_id[rec['type']], rec, client)) # TODO: remove literal
                self.paramframes[-1].pack(side=tkinter.TOP, fill=tkinter.X)

        self.fr_buttons = tkinter.Frame(self)
        self.btn_sendall = tkinter.Button(self.fr_buttons, text="Send all", command=self.on_btn_sendall)
        self.btn_updateall = tkinter.Button(self.fr_buttons, text="Update all", command=self.on_btn_updateall)
        self.btn_saveall = tkinter.Button(self.fr_buttons, text="Save all", command=self.on_btn_saveall)

        self.btn_sendall.pack(side=tkinter.LEFT)
        self.btn_updateall.pack(side=tkinter.LEFT)
        self.btn_saveall.pack(side=tkinter.LEFT)
        self.fr_buttons.pack(side=tkinter.TOP)

        self.poll_update()

    def send_all(self):
        for frame in self.paramframes:
            frame.send_data()

    def on_btn_sendall(self):
        wrkr = threading.Thread(target=self.send_all)
        wrkr.start()

    def ask_update_all(self):
        for pf in self.paramframes:
            pf.ask_update()

    def on_btn_updateall(self):
        wrkr = threading.Thread(target=self.ask_update_all)
        wrkr.start()

    def on_btn_saveall(self):
        # TODO: do it on background thread
        f = filedialog.asksaveasfilename(title="Save parameters", filetypes=(("YAML files", "*.yaml"),))

        if f is None:
            return

        datas = [frame.get_current_data() for frame in self.paramframes]

        with open(f, 'w') as param_file:
            yaml.dump(datas, param_file)

    def update_view(self):
        for paramframe in self.paramframes:
            paramframe.update_view()

    def poll_update(self):
        self.update_view()
        self.master.after(self.update_time, self.poll_update)
