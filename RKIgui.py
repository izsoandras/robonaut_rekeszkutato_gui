import tkinter
from tkinter import ttk
from tkinter import messagebox
import my_gui.plotting.TelemeteryFrame
import logging
import utils.SettingsReader
import utils.InfluxDBproxy
import my_mqtt.listeners.DatabaseSaveListener
import utils.telemetry_factory
from my_mqtt.testing_tools import test_source
import multiprocessing


class RKIguiApp():
    # noinspection PyUnresolvedReferences
    def __init__(self, test_source_en=False):
        self.logger = logging.getLogger('App')
        self.logger.warning('Application started')

        reader = utils.SettingsReader.SettingsReader()
        topics_rec, plots_rec, mqtt_data, db_data = reader.read_data()

        if reader.severe:
            messagebox.showerror('File not found', '\n'.join(reader.severe))

        self.dbproxy = utils.InfluxDBproxy.InfluxDBproxy(**db_data)

        # TODO: prepare data holders
        dh_by_name, dh_by_type = utils.telemetry_factory.build_dataholders(topics_rec, plots_rec)

        self.tel_listener = my_mqtt.listeners.DatabaseSaveListener.DatabbaseSaveListener(self.dbproxy,
                                                                                         topics_rec[1]['messages'],  # TODO: ne szammal legyen indexolve
                                                                                         'RKI telemetry',
                                                                                         mqtt_data['broker'], 'tel',
                                                                                         mqtt_data['user'],
                                                                                         mqtt_data['pwd'], dh_by_type)

        # Create GUI
        self.root = None
        self.tabs = None
        self.init_gui(dh_by_name, plots_rec)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        if test_source_en:
            test_producer_process = multiprocessing.Process(target=test_source.run, args=(0.2,))
            test_producer_process.start()
            self.logger.info('Test source started')

        self.logger.info('-------SETUP COMPLETE----------')
        self.root.mainloop()

    def init_gui(self, dh_by_name, plot_rec):
        self.root = tkinter.Tk()

        # Window attributes
        self.root.title('RKI RobonAUT Diagnostics')
        self.root.iconbitmap('assets/icon.ico')

        # Tabs
        self.tabs = ttk.Notebook(self.root)

        telemetry_tab = my_gui.plotting.TelemeteryFrame.TelemetryFrame(self.tabs, self.tel_listener, dh_by_name, plot_rec)
        self.tabs.add(telemetry_tab, text='Graphs')

        self.tabs.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)

        self.logger.info('GUI set up')

    def on_closing(self):
        self.logger.warning('Application closed')
        self.root.destroy()


if __name__ == "__main__":
    app = RKIguiApp(True)
