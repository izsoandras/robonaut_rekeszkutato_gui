import unittest
import tkinter
from utils.telemetry_factory import build_plot_env_from_file
from utils.InfluxDBproxy import InfluxDBproxy


class MyTestCase(unittest.TestCase):
    def test_view(self):
        root = tkinter.Tk()
        proxy = InfluxDBproxy('localhost','test','plot_test_')
        listener, frame = build_plot_env_from_file( '../../settings/mqtt.yaml', '../../settings/msgs.yaml', '../../settings/plots.yaml', proxy, root)

        frame.pack()
        root.mainloop()


if __name__ == '__main__':
    unittest.main()
