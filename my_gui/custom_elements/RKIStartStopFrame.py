import tkinter
import logging
from clients.mqtt.listeners import ParamListener


class RKIStartStopFrame(tkinter.Frame):
    def __init__(self, parent, start_stop_client: ParamListener, start_msg_id: int, stop_msg_id: int, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.logger = logging.getLogger("RKID.RKIStartStopFrame")
        self.client = start_stop_client
        self.start_msg_id = start_msg_id
        self.stop_msg_id = stop_msg_id
        # Emergency stop
        self.btn_emergency = tkinter.Button(master=self, text="EMERGENCY STOP", command=self.send_emergency_stop, bg='red')
        self.btn_emergency.pack(side=tkinter.BOTTOM, fill='x', anchor=tkinter.S)
        # Start
        self.btn_start = tkinter.Button(master=self, text="START", command=self.send_start, bg='green')
        self.btn_start.pack(side=tkinter.BOTTOM, anchor=tkinter.S)

        self.master.bind("<space>", self.on_spacebar)

    def send_emergency_stop(self):
        self.client.send_message(self.stop_msg_id, {})
        self.logger.info('Sent STOP message')

    def send_start(self):
        self.client.send_message(self.start_msg_id, {})
        self.logger.info('Sent START message')

    def on_spacebar(self, event):
        self.btn_emergency.invoke()
