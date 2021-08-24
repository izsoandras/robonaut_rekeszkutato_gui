import tkinter
import my_gui.plotting.PlotsFrame
import my_gui.MQTTframes.MQTTdbstartstopFrame
import my_mqtt.listeners.MyMQTTllistener


class TelemetryFrame(tkinter.Frame):
    def __init__(self, parent, mqtt_listener: my_mqtt.listeners.MyMQTTllistener.MyMQTTlistener, dataholders_by_name: dict, plot_rec: dict, *args,
                 **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.fr_startstop = my_gui.MQTTframes.MQTTdbstartstopFrame.MQTTdbStartStopFrame(self, mqtt_listener)
        self.plot_frame = my_gui.plotting.PlotsFrame.PlotsFrame(dataholders_by_name, plot_rec, self)

        self.fr_startstop.pack(side=tkinter.TOP)
        self.plot_frame.pack(side=tkinter.TOP)

