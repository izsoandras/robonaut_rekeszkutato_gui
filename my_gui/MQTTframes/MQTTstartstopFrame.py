import tkinter
import my_mqtt.listeners.MyMQTTllistener


class MQTTstartstopFrame(tkinter.Frame):
    def __init__(self, parent, mqtt_listener: my_mqtt.listeners.MyMQTTllistener.MyMQTTlistener, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.listener = mqtt_listener

        self.btn_start = tkinter.Button(master=self, text="Sub", command=self.on_btn_open)
        self.btn_stop = tkinter.Button(master=self, text="Unsub", command=self.on_btn_close, state='disabled')

        self.btn_stop.pack(side=tkinter.RIGHT)
        self.btn_start.pack(side=tkinter.RIGHT)

    def on_btn_open(self):
        self.btn_stop.config(state='normal')
        self.btn_start.config(state='disabled')

        self.listener.subscribe()

    def on_btn_close(self):
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')

        self.listener.unsubscribe()
