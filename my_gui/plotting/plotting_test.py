import unittest
import tkinter
from utils.telemetry_factory import build_plot_env_from_file
from utils.InfluxDBproxy import InfluxDBproxy
import multiprocessing
from my_mqtt.testing_tools import test_source
from my_gui.MQTTframes.MQTTstartstopFrame import MQTTstartstopFrame


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.root = tkinter.Tk()
        self.proxy = InfluxDBproxy('localhost', 'test', 'plot_test_')
        self.listener, self.frame = build_plot_env_from_file('../../settings/mqtt.yaml', '../../settings/msgs.yaml',
                                                   '../../settings/plots.yaml', self.proxy, self.root)




    def test_view_static(self):
        self.frame.pack()
        self.root.mainloop()

    def test_view_dynamic(self):
        self.frame.pack()
        self.listener.subscribe()
        test_producer_process = multiprocessing.Process(target=test_source.run, args=(1,))
        test_producer_process.start()

        self.root.mainloop()

    def test_startstop(self):
        self.startstop = MQTTstartstopFrame(self.root, self.listener)
        self.startstop.pack()
        self.frame.pack()
        test_producer_process = multiprocessing.Process(target=test_source.run, args=(1,))
        test_producer_process.start()

        self.root.mainloop()


if __name__ == '__main__':
    unittest.main()
