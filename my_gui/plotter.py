import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation
import matplotlib.pyplot
import numpy as np
import paho.mqtt.client as mqtt
import my_mqtt
import my_mqtt.telemetry
from datetime import datetime
from queue import Queue
import logging

ani = None


class PlotFrame(tkinter.Frame):
    """"""

    def __init__(self, parent, database, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.PLOT_UPDATE_PERIOD = 200  # [ms]
        self.DATAPOINT_NO = 50
        self.is_visible = False

        self.logger = logging.getLogger('robotlog')

        self.meas_time = 0
        self.influxdb = database
        self.queue = Queue()

        self.datas = {
            'batt': {
                'data_no': 50,
                't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                'aux': [0] * 50,
                'mot': [0] * 50
            },
            'front_line': {
                'data_no': 50,
                't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                'pos1': [0] * 50,
                'pos2': [0] * 50,
                'pos3': [0] * 50,
                'detection': [0] * 32
            },
            'back_line': {
                'data_no': 50,
                't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                'pos1': [0] * 50,
                'pos2': [0] * 50,
                'pos3': [0] * 50,
                'detection': [0] * 32
            },
            'speed': {
                # 'duty': {
                #     'data_no': 50,
                #     't': np.arange(-50, 0, 1).tolist(),
                #     'duty': [0] * 50
                # },
                'current': {
                    'data_no': 50,
                    't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                    'current': [0] * 50,
                    'setpoint': [0] * 50
                },
                'speed': {
                    'data_no': 50,
                    't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                    'current': [0] * 50,
                    'setpoint': [0] * 50
                },
                'distance': {
                    'data_no': 50,
                    't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                    'current': [0] * 50,
                    'setpoint': [0] * 50
                }
            },
            'side_dist': {
                'data_no': 50,
                't': np.arange(-self.DATAPOINT_NO + 1, 1, 1).tolist(),
                'left': [0] * 50,
                'right': [0] * 50
            },
            'orientation': {
                'data_no': 50,
                't': 0,
                'orientation': 0,
                'orientation_setp': 90,
            }
        }

        self.mqtt_client = mqtt.Client(my_mqtt.TELEMETRY_NAME)
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.username_pw_set(my_mqtt.USER_NAME, my_mqtt.PASSWORD)
        self.mqtt_client.connect(my_mqtt.HOST_NAME)
        self.mqtt_client.loop_start()

        self.measurement_name = ''

        t = np.arange(0, 3, .01)

        self.fr_btns = tkinter.Frame(self)
        self.en_meas_name = tkinter.Entry(self.fr_btns)
        self.btn_start = tkinter.Button(master=self.fr_btns, text="Start", command=self.on_btn_open)
        self.btn_stop = tkinter.Button(master=self.fr_btns, text="Stop", command=self.on_btn_close, state='disabled')
        self.en_meas_name.pack(side=tkinter.LEFT)
        self.btn_start.pack(side=tkinter.LEFT)
        self.btn_stop.pack(side=tkinter.LEFT)

        self.fig = Figure(figsize=(10, 5), dpi=100)

        self.plots = {
            'batt': {
                'voltage': {
                    'axes': None,  # self.fig.add_subplot(111),
                    'title': 'Battery voltages',
                    'lines': {
                        'aux': {
                            'ax': None,
                            # self.plots['voltage']['axes'].plot(t, 2 * np.sin(2 * np.pi * t), label='aux'),
                            'label': 'aux'
                        },
                        'mot': {
                            'ax': None,
                            # self.plots['voltage']['axes'].plot(t, 2 * np.sin(2 * np.pi * t), label='mot'),
                            'label': 'mot'
                        }
                    }
                },
                'build': self.build_batt,
                'update': self.update_batt

            },
            'front_line': {
                'position': {
                    'axes': None,
                    'title': 'Front line position',
                    'lines': {
                        'pos1': {
                            'ax': None,
                            'label': None
                        },
                        'pos2': {
                            'ax': None,
                            'label': None
                        },
                        'pos3': {
                            'ax': None,
                            'label': None
                        }
                    }
                },
                'detection': {
                    'axes': None,
                    'title': 'Front line detection',
                    'lines': {
                        'ax': None,
                        'label': None
                    }
                },
                'build': self.build_line,
                'update': self.update_line
            },
            'back_line': {
                'position': {
                    'axes': None,
                    'title': 'Back line position',
                    'lines': {
                        'pos1': {
                            'ax': None,
                            'label': 'pos1'
                        },
                        'pos2': {
                            'ax': None,
                            'label': 'pos2'
                        },
                        'pos3': {
                            'ax': None,
                            'label': 'pos3'
                        }
                    }
                },
                'detection': {
                    'axes': None,
                    'title': 'Back line detection',
                    'lines': {
                        'ax': None,
                        'label': None
                    }
                },
                'build': self.build_line,
                'update': self.update_line
            },
            'speed': {
                # 'duty': {
                #     'axes': None,
                #     'title': 'Duty cycle',
                #     'lines': {
                #         'ax': None,
                #         'label': 'Dutycycle'
                #     }
                # },
                'current': {
                    'axes': None,
                    'title': 'Current',
                    'lines': {
                        'current': {
                            'ax': None,
                            'label': 'Current'
                        },
                        'setpoint': {
                            'ax': None,
                            'label': 'Setpoint'
                        }
                    }
                },
                'speed': {
                    'axes': None,
                    'title': 'Speed',
                    'lines': {
                        'current': {
                            'ax': None,
                            'label': 'Current'
                        },
                        'setpoint': {
                            'ax': None,
                            'label': 'Setpoint'
                        }
                    }
                },
                'distance': {
                    'axes': None,
                    'title': 'Distance',
                    'lines': {
                        'current': {
                            'ax': None,
                            'label': 'Current'
                        },
                        'setpoint': {
                            'ax': None,
                            'label': 'Setpoint'
                        }
                    }
                },
                'build': self.build_speed,
                'update': self.update_speed
            },
            # 'side_dist': {
            #     'distance': {
            #         'axes': None,  # self.fig.add_subplot(111),
            #         'title': 'Side distances',
            #         'lines': {
            #             'left': {
            #                 'ax': None,
            #                 # self.plots['voltage']['axes'].plot(t, 2 * np.sin(2 * np.pi * t), label='aux'),
            #                 'label': 'left'
            #             },
            #             'right': {
            #                 'ax': None,
            #                 # self.plots['voltage']['axes'].plot(t, 2 * np.sin(2 * np.pi * t), label='mot'),
            #                 'label': 'right'
            #             }
            #         }
            #     },
            #     'build': self.build_side_dist,
            #     'update': self.update_side_dist
            #
            # },
            'orientation': {
                'orientation': {
                    'axes': None,  # self.fig.add_subplot(111),
                    'title': 'Car orientation',
                    'lines': {
                        'orientation': {
                            'ax': None,
                            # self.plots['voltage']['axes'].plot(t, 2 * np.sin(2 * np.pi * t), label='aux'),
                            'label': 'ori'
                        },
                        'orientation_setp': {
                            'ax': None,
                            # self.plots['voltage']['axes'].plot(t, 2 * np.sin(2 * np.pi * t), label='aux'),
                            'label': 'ori_setp'
                        }
                    }
                },
                'build': self.build_orientation,
                'update': self.update_orientation

            }
        }

        self.updateables = []
        hor = 3
        vert = 3
        idx = 1
        for key in self.plots.keys():
            increment, ext = self.plots[key]['build'](key, hor, vert, idx)
            self.updateables.extend(ext)
            idx = idx + increment

        self.fig.tight_layout(pad=1)
        # vert = 1
        # hor = int(len(self.plots.keys()) / vert)
        # for idx, key in enumerate(self.plots.keys()):
        #     plot = self.fig.add_subplot(hor, vert, idx+1)
        #
        #     self.plots[key]['axes'] = plot
        #
        #     for line in self.plots[key]['lines'].keys():
        #         self.plots[key]['lines'][line]['ax'], = plot.plot(t, 2 * np.sin(2 * np.pi * t), label=self.plots[key]['lines'][line]['label'])
        #
        # for plot in self.plots.keys():
        #     self.plots[plot]['axes'].set_title(self.plots[plot]['title'])
        #     self.plots[plot]['axes'].legend()

        # self.axes2 = self.fig.add_subplot(122)
        # self.line2, = self.axes1.plot(t, -2 * np.sin(2 * np.pi * t), label='mot')
        # self.axes1.legend()
        # self.line2, = self.axes2.plot(t, -2 * np.sin(2 * np.pi * t))
        global ani

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        # self.canvas.draw()

        self.fr_btns.pack(side=tkinter.TOP)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        ani = matplotlib.animation.FuncAnimation(self.fig, self.update_view, interval=200, blit=True)

        # self.master.after(self.PLOT_UPDATE_PERIOD, self.update_view)

    def on_btn_open(self):
        self.btn_stop.config(state='normal')
        self.btn_start.config(state='disabled')
        self.en_meas_name.config(state='disabled')

        self.measurement_name = str(datetime.now()) + '_'

        if self.en_meas_name.get():
            self.measurement_name = self.measurement_name + self.en_meas_name.get() + '_'

        self.mqtt_client.subscribe(my_mqtt.TELEMETRY_TOPIC)
        self.logger.info('Measurement start')

    def on_btn_close(self):
        self.btn_start.config(state='normal')
        self.en_meas_name.config(state='normal')
        self.btn_stop.config(state='disabled')

        self.mqtt_client.unsubscribe(my_mqtt.TELEMETRY_TOPIC)
        self.logger.info('Measurement finished')

    def on_message(self, client, userdata, message):
        """MQTT message receive handler.
        Runs on new thread. Decodes the message, logs it, and puts it in a queue for the GUI thread for display"""

        data = my_mqtt.telemetry.decode_telemetry(message.payload)

        if not data:
            return

        # dat = json.loads(str(message.payload.decode("utf-8")))
        # print("message received ", dat)
        # print("message topic=", message.topic)
        # print("message qos=", message.qos)
        # print("message retain flag=", message.retain)

        db_json = [{
            "measurement": self.measurement_name + data['type'],
            "fields": data['data'],
            "tags": {}
        }]

        self.influxdb.write_points(db_json)

        self.queue.put(data)

        # print("########################")

    def update_view(self, i):
        """Checks every period_time_ms milisec if new data has arrived. If new data is available it puts it from the queue
        to the list storage and gives it to the GUI for plotting"""
        has_new_data = False
        updated_lines = []
        while not self.queue.empty():
            new_data = self.queue.get()
            if new_data['type'] in self.plots.keys():

                # updated_lines.append()
                self.plots[new_data['type']]['update'](new_data)
                has_new_data = True
            else:
                pass
            # if new_data['type'] == 'batt':
            #     self.plots['batt']['update'](new_data)
            #     has_new_data = True

        return self.updateables
        # if has_new_data and self.is_visible:
        #     self.canvas.draw()
        #     self.canvas.flush_events()

        # self.master.after(self.PLOT_UPDATE_PERIOD, self.update_view)

    def build_batt(self, plot_key, hor, vert, idx):
        plot = self.fig.add_subplot(vert, hor, idx)
        plot.set_title(self.plots[plot_key]['voltage']['title'])
        plot.legend()

        self.plots[plot_key]['voltage']['axes'] = plot

        lines = []
        for line in self.plots[plot_key]['voltage']['lines'].keys():
            self.plots[plot_key]['voltage']['lines'][line]['ax'], = plot.plot(self.datas[plot_key]['t'],
                                                                              self.datas[plot_key][line], label=
                                                                              self.plots[plot_key]['voltage']['lines'][
                                                                                  line]['label'])

            lines.append(self.plots[plot_key]['voltage']['lines'][line]['ax'])

        # TODO: kiszervezni a hatarertekeket
        self.plots[plot_key]['voltage']['axes'].set_ylim([0, 14])
        self.plots[plot_key]['voltage']['axes'].set_xlim([-self.DATAPOINT_NO + 1, 0])

        # self.plots[plot_key]['voltage']['axes'].set_title(self.plots[plot]['voltage']['title'])
        # self.plots[plot_key]['voltage']['axes'].legend()
        # plot.set_title(self.plots[plot]['voltage']['title'])
        # plot.legend()

        return 1, lines

    def update_batt(self, new_data):
        data_type = new_data['type']
        # new_data['data']['t'] = self.datas[data_type]['t'][-1] + 1

        if len(self.datas[data_type]['t']) == self.datas[data_type]['data_no']:
            # self.datas[data_type]['t'].pop(0)
            self.datas[data_type]['aux'].pop(0)
            self.datas[data_type]['mot'].pop(0)

        # self.datas[data_type]['t'].append(new_data['data']['t'])
        self.datas[data_type]['aux'].append(new_data['data']['aux'])
        self.datas[data_type]['mot'].append(new_data['data']['mot'])

        plot_dict = self.plots[data_type]

        for line in plot_dict['voltage']['lines'].keys():
            if line != 't':
                # plot_dict['voltage']['lines'][line]['ax'].set_xdata(self.datas[data_type]['t'])
                plot_dict['voltage']['lines'][line]['ax'].set_ydata(self.datas[data_type][line])

        # plot_dict['voltage']['axes'].relim()
        # plot_dict['voltage']['axes'].autoscale_view()

    def build_line(self, key, hor, vert, idx):
        t = np.arange(0, 3, .01)
        pos_plot = self.fig.add_subplot(vert, hor, idx)
        pos_plot.set_title(self.plots[key]['position']['title'])

        bar_plot = self.fig.add_subplot(vert, hor, idx + 1)
        bar_plot.set_title(self.plots[key]['detection']['title'])

        self.plots[key]['position']['axes'] = pos_plot
        self.plots[key]['detection']['axes'] = bar_plot

        self.plots[key]['detection']['lines']['ax'] = bar_plot.bar(np.arange(0, 32, 1), [1, 0] * 16, animated=True)

        lines = self.plots[key]['detection']['lines']['ax'].patches
        for i in range(1, 4):
            self.plots[key]['position']['lines'][f'pos{i}']['ax'], = pos_plot.plot(self.datas[key]['t'],
                                                                                   self.datas[key][f'pos{i}'],
                                                                                   animated=True)
            lines.append(self.plots[key]['position']['lines'][f'pos{i}']['ax'])
            # self.plots[key]['position']['lines'][f'pos{i}']['ax']._animated=True

        # for bars in self.plots[key]['detection']['lines']['ax'].patches:
        #     bars._animated = True

        self.plots[key]['position']['axes'].set_ylim([0, 31])
        self.plots[key]['position']['axes'].set_xlim([-self.DATAPOINT_NO + 1, 0])

        return 2, lines

    def update_line(self, new_data):
        data_type = new_data['type']
        new_data = new_data['data']
        self.datas[data_type]['detection'] = new_data['detection']

        if len(self.datas[data_type]['t']) == self.datas[data_type]['data_no']:
            # self.datas[data_type]['t'].pop(0)
            for i in range(1, 4):
                self.datas[data_type][f'pos{i}'].pop(0)

        # self.datas[data_type]['t'].append(self.datas[data_type]['t'][-1] + 1)

        plot_dict = self.plots[data_type]

        for d, rect in zip(new_data['detection'], plot_dict['detection']['lines']['ax']):
            rect.set_height(int(d))

        for i in range(1, 4):
            self.datas[data_type][f'pos{i}'].append(new_data[f'pos{i}'])
            plot_dict['position']['lines'][f'pos{i}']['ax'].set_xdata(self.datas[data_type]['t'])
            plot_dict['position']['lines'][f'pos{i}']['ax'].set_ydata(self.datas[data_type][f'pos{i}'])

        # plot_dict['position']['axes'].relim()
        # plot_dict['position']['axes'].autoscale_view()

    def build_speed(self, key, hor, vert, idx):
        t = np.arange(0, 3, 0.1)
        # duty_plot = self.fig.add_subplot(vert, hor, idx)
        # duty_plot.set_title(self.plots[key]['duty']['title'])

        current_plot = self.fig.add_subplot(vert, hor, idx)
        current_plot.set_title(self.plots[key]['current']['title'])
        current_plot.set_ylim([-400, 400])
        current_plot.set_xlim([-self.DATAPOINT_NO + 1, 0])

        speed_plot = self.fig.add_subplot(vert, hor, idx + 1)
        speed_plot.set_title(self.plots[key]['speed']['title'])
        speed_plot.set_ylim([-500, 2000])
        speed_plot.set_xlim([-self.DATAPOINT_NO + 1, 0])

        distance_plot = self.fig.add_subplot(vert, hor, idx + 2)
        distance_plot.set_title(self.plots[key]['distance']['title'])
        distance_plot.set_ylim([0, 2000])
        distance_plot.set_xlim([-self.DATAPOINT_NO + 1, 0])

        # self.plots[key]['duty']['axes'] = duty_plot
        self.plots[key]['current']['axes'] = current_plot
        self.plots[key]['speed']['axes'] = speed_plot
        self.plots[key]['distance']['axes'] = distance_plot

        # self.plots[key]['duty']['lines']['ax'], = duty_plot.plot(t, 2 * np.sin(2 * np.pi * t))

        self.plots[key]['current']['lines']['current']['ax'], = current_plot.plot(self.datas['speed']['current']['t'],
                                                                                  self.datas['speed']['current'][
                                                                                      'current'])
        self.plots[key]['current']['lines']['setpoint']['ax'], = current_plot.plot(self.datas['speed']['current']['t'],
                                                                                   self.datas['speed']['current'][
                                                                                       'setpoint'])

        self.plots[key]['speed']['lines']['current']['ax'], = speed_plot.plot(self.datas['speed']['speed']['t'],
                                                                              self.datas['speed']['speed']['current'])
        self.plots[key]['speed']['lines']['setpoint']['ax'], = speed_plot.plot(self.datas['speed']['speed']['t'],
                                                                               self.datas['speed']['speed']['setpoint'])

        self.plots[key]['distance']['lines']['current']['ax'], = distance_plot.plot(
            self.datas['speed']['distance']['t'], self.datas['speed']['distance']['current'])
        self.plots[key]['distance']['lines']['setpoint']['ax'], = distance_plot.plot(
            self.datas['speed']['distance']['t'], self.datas['speed']['distance']['setpoint'])

        lines = [self.plots[key]['current']['lines']['current']['ax'],
                 self.plots[key]['current']['lines']['setpoint']['ax'],
                 self.plots[key]['speed']['lines']['current']['ax'],
                 self.plots[key]['speed']['lines']['setpoint']['ax'],
                 self.plots[key]['distance']['lines']['current']['ax'],
                 self.plots[key]['distance']['lines']['setpoint']['ax']
                 ]

        return 3, lines

    def update_speed(self, new_data):
        data_type = new_data['type']
        new_data = new_data['data']
        # new_data['t'] = self.datas[data_type]['current']['t'][-1] + 1

        # if len(self.datas[data_type]['duty']['t']) == self.datas[data_type]['duty']['data_no']:
        #     self.datas[data_type]['duty']['t'].pop(0)
        #     self.datas[data_type]['duty']['duty'].pop(0)
        #
        # self.datas[data_type]['duty']['t'].append(new_data['t'])
        # self.datas[data_type]['duty']['duty'].append(new_data['duty'])

        for plot in self.datas[data_type].keys():
            if plot == 'duty':
                continue

            if len(self.datas[data_type][plot]['current']) >= self.datas[data_type][plot]['data_no']:
                # self.datas[data_type][plot]['t'].pop(0)
                self.datas[data_type][plot]['current'].pop(0)
                self.datas[data_type][plot]['setpoint'].pop(0)

            # self.datas[data_type][plot]['t'].append(new_data['t'])
            self.datas[data_type][plot]['current'].append(new_data[plot])
            self.datas[data_type][plot]['setpoint'].append(new_data[plot + '_setp'])

        plot_dict = self.plots[data_type]

        # plot_dict['duty']['lines']['ax'].set_xdata(self.datas[data_type]['duty']['t'])
        # plot_dict['duty']['lines']['ax'].set_ydata(self.datas[data_type]['duty']['duty'])

        for plot in plot_dict.keys():
            if plot == 'build' or plot == 'update':
                continue

            if plot != 'duty':
                for line in plot_dict[plot]['lines'].keys():
                    if line != 't':
                        # plot_dict[plot]['lines'][line]['ax'].set_xdata(self.datas[data_type][plot]['t'])
                        plot_dict[plot]['lines'][line]['ax'].set_ydata(self.datas[data_type][plot][line])

            # plot_dict[plot]['axes'].relim()
            # plot_dict[plot]['axes'].autoscale_view()

    def build_side_dist(self, key, hor, vert, idx):
        t = np.arange(0, 3, 0.1)
        plot = self.fig.add_subplot(vert, hor, idx)
        plot.set_title(self.plots[key]['distance']['title'])
        plot.legend()
        plot.set_ylim([-2000, 2000])
        plot.set_xlim([-self.DATAPOINT_NO + 1, 0])

        self.plots[key]['distance']['axes'] = plot

        lines = []
        for line in self.plots[key]['distance']['lines'].keys():
            self.plots[key]['distance']['lines'][line]['ax'], = plot.plot(self.datas[key]['t'], self.datas[key][line],
                                                                          label=
                                                                          self.plots[key]['distance']['lines'][line][
                                                                              'label'])
            lines.append(self.plots[key]['distance']['lines'][line]['ax'])

        return 3, lines

    def update_side_dist(self, new_data):
        CARSIDE_OFFSET = 0  # 100
        data_type = new_data['type']
        # new_data['data']['t'] = self.datas[data_type]['t'][-1] + 1

        if len(self.datas[data_type]['left']) == self.datas[data_type]['data_no']:
            self.datas[data_type]['left'].pop(0)
            self.datas[data_type]['right'].pop(0)

        # self.datas[data_type]['t'].append(new_data['data']['t'])
        self.datas[data_type]['left'].append(new_data['data']['left'] + CARSIDE_OFFSET)
        self.datas[data_type]['right'].append(-1 * new_data['data']['right'] - CARSIDE_OFFSET)

        plot_dict = self.plots[data_type]

        for line in plot_dict['distance']['lines'].keys():
            if line != 't':
                # plot_dict['distance']['lines'][line]['ax'].set_xdata(self.datas[data_type]['t'])
                plot_dict['distance']['lines'][line]['ax'].set_ydata(self.datas[data_type][line])

        # plot_dict['distance']['axes'].relim()
        # plot_dict['distance']['axes'].autoscale_view()

    def build_orientation(self, key, hor, vert, idx):
        t = np.arange(0, 3, 0.1)

        plot = self.fig.add_subplot(vert, hor, idx, projection='polar')
        plot.set_title(self.plots[key]['orientation']['title'])
        # plot.legend()
        # plot.set_ylim([-1, 1])
        # plot.set_xlim([-1, 1])
        #
        # plot.set_aspect(1)
        # circle_artist = matplotlib.pyplot.Circle((0, 0), 1, animated=True, fill=False,color='k')
        # plot.add_artist(circle_artist)
        #
        # x1 = np.sin(np.deg2rad(self.datas[key]['orientation']))
        # y1 = np.cos(np.deg2rad(self.datas[key]['orientation']))
        #
        # x2 = np.sin(np.deg2rad(self.datas[key]['orientation_setp']))
        # y2 = np.cos(np.deg2rad(self.datas[key]['orientation_setp']))
        #
        # self.plots[key]['orientation']['axes'] = plot
        #
        #
        # self.plots[key]['orientation']['lines']['orientation']['ax'], = plot.plot([0, x1], [0,y1],
        #                                                                           label=
        #                                                                           self.plots[key]['orientation']['lines'][
        #                                                                               'orientation'][
        #                                                                               'label'])
        #
        # self.plots[key]['orientation']['lines']['orientation_setp']['ax'], = plot.plot([0, x2], [0, y2],
        #                                                                           label=
        #                                                                           self.plots[key]['orientation'][
        #                                                                               'lines'][
        #                                                                               'orientation_setp'][
        #                                                                               'label'])
        #
        # return 3, [self.plots[key]['orientation']['lines']['orientation']['ax'],
        #            self.plots[key]['orientation']['lines']['orientation_setp']['ax'], circle_artist]

        plot.set_theta_zero_location("N")
        plot.set_xticks(np.pi/180. * np.linspace(-180, 180, 8, endpoint=False))
        plot.set_thetalim(np.pi, -np.pi)
        plot.set_theta_direction(-1)
        plot.set_yticklabels([])

        rad = np.deg2rad(self.datas[key]['orientation'])
        rad_setp = np.deg2rad(self.datas[key]['orientation_setp'])

        self.plots[key]['orientation']['lines']['orientation']['ax'], = plot.plot([rad, rad],[0, 1])
        self.plots[key]['orientation']['lines']['orientation_setp']['ax'], = plot.plot([rad_setp, rad_setp], [0, 1])

        return 1, [self.plots[key]['orientation']['lines']['orientation']['ax'], self.plots[key]['orientation']['lines']['orientation_setp']['ax']]


    def update_orientation(self, new_data):
        data_type = new_data['type']

        # self.datas[data_type]['t'].append(new_data['data']['t'])
        self.datas[data_type]['orientation'] = new_data['data']['orientation']
        self.datas[data_type]['orientation_setp'] = new_data['data']['orientation_setp']

        plot_dict = self.plots[data_type]

        # x1 = np.sin(np.deg2rad(self.datas['orientation']['orientation']))
        # y1 = np.cos(np.deg2rad(self.datas['orientation']['orientation']))
        # x2 = np.sin(np.deg2rad(self.datas['orientation']['orientation_setp']))
        # y2 = np.cos(np.deg2rad(self.datas['orientation']['orientation_setp']))
        #
        # plot_dict['orientation']['lines']['orientation']['ax'].set_ydata([0, y1])
        # plot_dict['orientation']['lines']['orientation']['ax'].set_xdata([0, x1])
        #
        # plot_dict['orientation']['lines']['orientation_setp']['ax'].set_ydata([0, y2])
        # plot_dict['orientation']['lines']['orientation_setp']['ax'].set_xdata([0, x2])

        rad = np.deg2rad(self.datas['orientation']['orientation'])
        rad_setp = np.deg2rad(self.datas['orientation']['orientation_setp'])

        self.plots['orientation']['orientation']['lines']['orientation']['ax'].set_xdata([rad, rad])
        self.plots['orientation']['orientation']['lines']['orientation_setp']['ax'].set_xdata([rad_setp, rad_setp])

