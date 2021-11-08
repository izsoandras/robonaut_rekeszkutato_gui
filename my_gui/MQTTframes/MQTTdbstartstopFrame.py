import tkinter
import my_gui.MQTTframes.MQTTstartstopFrame
import clients.mqtt.listeners.DatabaseSaveListener


class MQTTdbStartStopFrame(my_gui.MQTTframes.MQTTstartstopFrame.MQTTstartstopFrame):
    def __init__(self, parent, mqtt_listener: clients.mqtt.listeners.DatabaseSaveListener.DatabbaseSaveListener, *args,
                 **kwargs):
        super().__init__(parent, mqtt_listener, *args, **kwargs)

        self.en_name = tkinter.Entry(self)
        self.btn_rec = tkinter.Button(self, text="Rec", command=self.on_btn_start, state='disabled')
        self.btn_rec.pack(side=tkinter.RIGHT)
        self.en_name.pack(side=tkinter.RIGHT)

    def on_btn_start(self):
        if self.en_name.get():
            name = self.en_name.get()
        else:
            name = ''

        self.listener.resume(name)
        self.btn_rec.config(text="Stop", command=self.on_btn_stop)
        self.en_name.config(state='disabled')

    def on_btn_stop(self):
        self.listener.pause()
        self.btn_rec.config(text="Rec", command=self.on_btn_start)
        self.en_name.config(state='normal')

    def on_btn_open(self):
        super().on_btn_open()
        self.en_name.config(state='normal')
        self.btn_rec.config(state='normal')

    def on_btn_close(self):
        super().on_btn_close()
        self.on_btn_stop()
        self.btn_rec.config(state='disabled')
