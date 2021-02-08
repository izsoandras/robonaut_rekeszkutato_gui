import tkinter
import paho.mqtt.client as mqtt
import my_mqtt
import my_mqtt.log
from queue import Queue
import time

import logging


MAX_LINE_NO = 100


class ScreenHandler(logging.StreamHandler):
    def __init__(self, screenLogger):
        logging.StreamHandler.__init__(self)
        self.log_sink = screenLogger

    def emit(self, record):
        msg = self.format(record)
        self.log_sink.log_message(msg)


class ScreenLoggerFrame(tkinter.Frame):
    def __init__(self, parent, visible_line_num, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.UPDATE_LOG_MS = 200

        self.logger = logging.getLogger('robotlog')

        screenHandler = ScreenHandler(self)
        screenHandler.setLevel(logging.INFO)
        screen_formatter = logging.Formatter('%(levelname)s - %(message)s')
        screenHandler.setFormatter(screen_formatter)

        self.logger.addHandler(screenHandler)

        self.queue = Queue()

        self.mqtt_client = mqtt.Client(my_mqtt.LOGGER_NAME)
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.username_pw_set(my_mqtt.USER_NAME, my_mqtt.PASSWORD)
        self.mqtt_client.connect(my_mqtt.HOST_NAME)
        self.mqtt_client.subscribe(my_mqtt.LOGGER_TOPIC)
        self.mqtt_client.loop_start()

        self.visible_line_num = visible_line_num
        self.line_no = 0
        self.tb_logfield = tkinter.Text(self, height=visible_line_num, state=tkinter.DISABLED)
        self.sb_logscroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tb_logfield.yview)

        self.tb_logfield.configure(yscrollcommand=self.sb_logscroll.set)

        self.sb_logscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tb_logfield.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)

        self.master.after(self.UPDATE_LOG_MS, self.write_onscreen)

    def on_message(self, client, userdata, message):
        msg = my_mqtt.log.decode_log(message.payload)

        if msg is None:
            return

        if msg['level'] == 'info':
            self.logger.info(msg['message'])
        if msg['level'] == 'warning':
            self.logger.warning(msg['message'])
        if msg['level'] == 'error':
            self.logger.error(msg['message'])

    def log_message(self, message):
        self.queue.put(message)

    def write_onscreen(self):
        self.tb_logfield.config(state=tkinter.NORMAL)
        while not self.queue.empty():
            new_msg = self.queue.get()

            self.tb_logfield.insert(tkinter.END, '\n' + new_msg)

        self.line_no = int(self.tb_logfield.index(tkinter.END).split('.')[0]) - 1
        if self.line_no >= MAX_LINE_NO:
            self.tb_logfield.delete('1.0', f'{1+(self.line_no-MAX_LINE_NO)}.0')

        self.keep_end_visible_if_needed()

        self.tb_logfield.config(state=tkinter.DISABLED)
        self.master.after(self.UPDATE_LOG_MS, self.write_onscreen)

    def keep_end_visible_if_needed(self):
        if self.sb_logscroll.get()[1] > (self.line_no - 2) / self.line_no:
            self.tb_logfield.see(tkinter.END)
            return True
        else:
            return False

    def set_visible_line_number(self, visible_line_num: int):
        old_num = self.visible_line_num
        self.visible_line_num = visible_line_num
        self.tb_logfield.configure(height=visible_line_num)


