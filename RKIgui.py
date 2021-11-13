import tkinter
from tkinter import ttk
from tkinter import messagebox
import my_gui.plotting.TelemeteryFrame
import logging
import logging.handlers
import utils.SettingsReader
import utils.InfluxDBproxy
import clients.mqtt.listeners.DatabaseSaveListener
import utils.telemetry_factory
from clients.mqtt.testing_tools import test_source
import multiprocessing
import my_gui.db_frames.DbExportFrame
import my_gui.logging.ScreenLogger
import clients.mqtt.listeners.LogListener
import my_gui.paramsetter.SetParamsFrame
import clients.mqtt.listeners.MyMQTTllistener
import utils.dataholder_factory
import clients.serial.RKIUartListener
import msg_codecs.frame_codecs.RKIUartCoder
import traceback


class RKIguiApp():
    # noinspection PyUnresolvedReferences
    def __init__(self, test_source_en=False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter('%(name)s:%(levelname)s:%(message)s'))

        file_handler = logging.FileHandler('app.log', mode='w')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        root_logger = logging.getLogger('RKID')  # TODO: outsource literal
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        self.logger = logging.getLogger('RKID.App')
        self.logger.warning('Application started')

        try:
            reader = utils.SettingsReader.SettingsReader()
            topics_rec, plots_rec, proto_data, db_data = reader.read_data()

            if reader.severe:
                messagebox.showerror('File not found', '\n'.join(reader.severe))

            self.dbproxy = utils.InfluxDBproxy.InfluxDBproxy(**db_data)

            # TODO: prepare data holders
            tel_dh_by_name, tel_dh_by_type = utils.telemetry_factory.build_dataholders(topics_rec[1:2], plots_rec)

            _, param_dh_by_type = utils.dataholder_factory.build_param_dataholders(topics_rec[2:3])

            self.log_listener = None
            if proto_data["proto"] == 'mqtt':
                mqtt_data = proto_data
                self.tel_listener = clients.mqtt.DatabbaseSaveListener(self.dbproxy,
                                                                                                      topics_rec[1]['messages'],  # TODO: ne szammal legyen indexolve
                                                                                                 'RKI telemetry',
                                                                                                      mqtt_data['broker'], 'tel',  # TODO: configurable topic
                                                                                                      mqtt_data['user'],
                                                                                                      mqtt_data['pwd'], tel_dh_by_type)

                self.log_listener = clients.mqtt.LogListener('RKI log',
                                                                              'RoboCar',
                                                                                   topics_rec[0]['messages'],
                                                                                   mqtt_data['broker'], 'log',  # TODO: configurable topic
                                                                                   mqtt_data['user'],
                                                                                   mqtt_data['pwd'])

                self.log_listener.subscribe()

                self.param_listener = clients.mqtt.listeners.MyMQTTllistener.MyMQTTlistener(topics_rec[2]['messages'],
                                                                                       'RKI parameters',
                                                                                            mqtt_data['broker'], 'param',
                                                                                            # TODO: configurable topic
                                                                                            mqtt_data['user'],
                                                                                            mqtt_data['pwd'], param_dh_by_type)

                robot_file_handler = logging.FileHandler('robot.log', mode='w')
                robot_file_handler.setFormatter(file_formatter)
                self.log_listener.robot_logger.addHandler(robot_file_handler)
                self.logger.info('Network setup done')
            elif proto_data["proto"] == 'serial':
                frame_coder = msg_codecs.frame_codecs.RKIUartCoder.RKIUartCoder(proto_data['max_len'])
                payload_coders = {}
                dhs = {**tel_dh_by_type, **param_dh_by_type}
                all_rec = topics_rec[1]['messages']
                all_rec.extend(topics_rec[2]['messages'])
                for recipe in all_rec:
                    payload_coders[recipe['type']] = msg_codecs.payload_codecs.PayloadCoder(**recipe)  # TODO: ne literal legyen
                serial_listener = clients.serial.RKIUartListener.RKIUartListener('Serial',
                                                                                 proto_data['port'],
                                                                                 frame_coder,
                                                                                 payload_coders,
                                                                                 dhs,
                                                                                 proto_data['baudrate'])
                self.param_listener = serial_listener
                self.tel_listener = serial_listener

            # Create GUI
            self.root = None
            self.init_window()
            self.param_frame = None
            self.init_paramframe(topics_rec[2]['messages'], param_dh_by_type, self.param_listener)  # TODO: remove literal
            self.log_frame = None
            self.init_logview()
            self.tabs = None
            self.init_tabs(tel_dh_by_name, plots_rec)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            self.logger.info('GUI set up')

            if test_source_en:
                self.test_producer_process = multiprocessing.Process(target=test_source.run, args=(0.2,))
                self.test_producer_process.start()
                self.logger.info('Test source started')
            else:
                self.test_producer_process = None

            self.logger.info('-------SETUP COMPLETE----------')
            self.root.mainloop()
        except Exception as ex:
            raise ex
            # tkinter.messagebox.showerror("Application error", traceback.format_exc())

    def init_window(self):
        self.root = tkinter.Tk()

        # Window attributes
        self.root.title('RKI RobonAUT Diagnostics')
        self.root.iconbitmap('assets/icon.ico')

    def init_logview(self):
        self.log_frame = my_gui.logging.ScreenLogger.ScreenLogger(self.root)
        logging.getLogger('RKID').addHandler(self.log_frame.logHandler)  # TODO: outsource literal
        if self.log_listener is not None:
            self.log_listener.robot_logger.addHandler(self.log_frame.logHandler)
        self.log_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X, anchor=tkinter.S)

    def init_paramframe(self, msgs_recipes, dh_by_type, client):
        # Params frame
        self.param_frame = my_gui.paramsetter.SetParamsFrame.SetParamsFrame(self.root, msgs_recipes, client, dh_by_type)
        self.param_frame.pack_parent(side=tkinter.RIGHT, fill=tkinter.Y)

    def init_tabs(self, dh_by_name, plot_rec):
        # Tabs
        self.tabs = ttk.Notebook(self.root)

        telemetry_tab = my_gui.plotting.TelemeteryFrame.TelemetryFrame(self.tabs, self.tel_listener, dh_by_name, plot_rec)
        db_tab = my_gui.db_frames.DbExportFrame.DBExportFrame(self.tabs, self.dbproxy)
        self.tabs.add(telemetry_tab, text='Graphs')
        self.tabs.add(db_tab, text='Database')

        self.tabs.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)

    def on_closing(self):
        self.logger.warning('Application closed')

        if self.test_producer_process is not None:
            self.test_producer_process.kill()

        self.dbproxy.stop_checking()
        self.root.destroy()


if __name__ == "__main__":
    app = RKIguiApp(False)
