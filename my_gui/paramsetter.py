import tkinter
import json
import my_mqtt
import my_mqtt.commands
import paho.mqtt.client as mqtt
import logging
from queue import Queue


# Source: https://blog.tecladocode.com/tkinter-scrollable-frames/
class ScrollableFrame(tkinter.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tkinter.Canvas(self)
        scrollbar = tkinter.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tkinter.Frame(canvas)  # TODO: leszármazás helyett ez legyen a SetParamsFrame

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"), width=self.scrollable_frame.winfo_width()
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        # canvas.configure(highlightbackground='pink', highlightthickness=1)


class SetParamsFrame(ScrollableFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.logger = logging.getLogger('robotlog')

        self.mqtt_client = mqtt.Client(my_mqtt.CONTROL_PARAMS_NAME)
        self.mqtt_client.username_pw_set(my_mqtt.USER_NAME, my_mqtt.PASSWORD)
        self.mqtt_client.connect(my_mqtt.HOST_NAME)
        self.mqtt_client.subscribe(my_mqtt.PARAMS_TOPIC)
        self.mqtt_client.on_message = self.on_msg_parameters
        self.mqtt_client.loop_start()

        servo_parameters = ['center1', 'center2', 'delta1', 'delta2']
        serve_param_types = ['int']*5

        curr_setpoint = ['setpoint']
        curr_param_types = ['float']

        speed_set_params = ['setpoint']
        speed_setp_param_types = ['float']

        speed_control_params = ['currentK', 'currentZ', 'speedK', 'speedZ']
        speed_control_params_types = ['float']*4

        line_params = ['kszi', 'd0', 'dv']
        line_params_types = ['float']*3

        gate_params = ['name']
        gate_types = ['char']

        self.param_frames = {
            'servo_cal': ParamsFrame(self.scrollable_frame, 'servo_cal', servo_parameters, serve_param_types, my_mqtt.commands.encode_servo_cal,
                                     my_mqtt.commands.encode_get_servo_cal),
            'current_setp': ParamsFrame(self.scrollable_frame, 'current_setp', curr_setpoint, curr_param_types, my_mqtt.commands.encode_current_setpoint,
                                        my_mqtt.commands.encode_get_current_setpoint),
            'speed_setp': ParamsFrame(self.scrollable_frame, 'speed_setp', speed_set_params, speed_setp_param_types, my_mqtt.commands.encode_speed_setpoint,
                                        my_mqtt.commands.encode_get_speed_setpoint),
            'line_param': ParamsFrame(self.scrollable_frame, 'line_param', line_params, line_params_types, my_mqtt.commands.encode_line_params,
                                        my_mqtt.commands.encode_get_line_params),
            'gate': ParamsFrame(self.scrollable_frame, 'gate', gate_params, gate_types, my_mqtt.commands.encode_gate,
                                        my_mqtt.commands.encode_get_gate)
        }

        # self.param_set_dict = {}
        # self.param_disp_dict = {}
        #
        # for i in range(len(parameters)):
        #     row = i % 2
        #     col = math.floor(i/2)
        #
        #     tkinter.Label(self.fr_params, text=parameters[i]).grid(row=row, column=col*3, sticky='E', padx=5)
        #
        #     entry = tkinter.Entry(self.fr_params, width=8, justify='right')
        #     entry.insert(0, '0.0')
        #     self.param_set_dict[parameters[i]] = entry
        #     entry.grid(row=row, column=col*3+1, sticky='W')
        #
        #     strVar = tkinter.StringVar()
        #     entry = tkinter.Entry(self.fr_params, state='readonly', textvariable=strVar, width=8, justify='left')
        #     strVar.set('0.0')
        #     self.param_disp_dict[parameters[i]] = strVar
        #     entry.grid(row=row, column=col * 3 + 2, sticky='W')

        for param in self.param_frames.keys():
            self.param_frames[param].pack()

            # TODO: only hotfix, remove!!!
            self.param_frames[param].send_message = self.send_message

        self.fr_btns = tkinter.Frame(self.scrollable_frame)
        self.btn_send = tkinter.Button(self.fr_btns, text="Send all", command=self.on_btn_sendall)
        self.btn_send.pack(side=tkinter.LEFT)
        self.btn_get = tkinter.Button(self.fr_btns, text="Get all", command=self.on_btn_getall)
        self.btn_get.pack(side=tkinter.LEFT)
        self.btn_save = tkinter.Button(self.fr_btns, text="Save", command=self.on_btn_saveall)
        self.btn_save.pack(side=tkinter.LEFT)
        self.fr_btns.pack()

    def on_btn_sendall(self):
        for name in self.param_frames.keys():
            self.param_frames[name].on_btn_send()

        self.logger.info('Parameters sent')

    def on_btn_getall(self):
        for name in self.param_frames.keys():
            self.param_frames[name].on_btn_update()

        self.logger.debug('Parameter request sent')

    def on_btn_saveall(self):
        param_save = []
        for params in self.param_frames.keys():
            param_save.append(self.param_frames[params].get_param_dict())

        with open('parameters.json', 'w') as outfile:
            json.dump(param_save, outfile)

        self.logger.info('Parameters saved')

    def on_msg_parameters(self, client, userdata, message):
        my_mqtt.logger.debug(f'Parameter message received')
        param_dict = my_mqtt.commands.decode_command(message.payload)

        # TODO: fix that start and stop messages dont trigger redraw
        if param_dict['type'] != 'start' and param_dict['type'] != 'stop':
            self.param_frames[param_dict['type']].queue_new_value(param_dict)

    def send_message(self, enc_msg):
        self.mqtt_client.publish(my_mqtt.COMMAND_TOPIC, enc_msg)


class ParamsFrame(tkinter.Frame):
    lab_name = 'lab_name'
    tb_edit = 'tb_edit'
    stVar_view = 'stVar_view'
    num_type = 'num_type'

    INT = 'int'
    FLOAT = 'float'
    CHAR = 'char'

    def __init__(self, parent, name, params, param_type, encode_send, encode_get, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)
        self.name = name
        self.encode_send = encode_send
        self.encode_get = encode_get

        self.queue = Queue()
        self.UPDATE_PARAM_MS = 50

        # TODO: only hotfix, remove
        self.send_message = None

        # self.configure(highlightbackground='gray', highlightthickness=1)

        self.lb_name = tkinter.Label(self, text=self.name)
        self.lb_name.pack()

        self.fr_params = tkinter.Frame(self)

        reg_int = parent.register(ParamsFrame.validate_int)
        reg_float = parent.register(ParamsFrame.validate_float)
        reg_char = parent.register(ParamsFrame.validate_char)

        self.param_controls = {}
        for idx, param in enumerate(params):
            self.param_controls[param] = {
                self.lab_name: tkinter.Label(self.fr_params, text=param),
                self.tb_edit: tkinter.Entry(self.fr_params, width=8, justify='right'),
                self.stVar_view: tkinter.StringVar(),
                self.num_type: param_type[idx]
            }

            entry = tkinter.Entry(self.fr_params, state='readonly', textvariable=self.param_controls[param][self.stVar_view],
                                  width=8, justify='left')

            if self.param_controls[param][self.num_type] == 'int':
                self.param_controls[param][self.tb_edit].config(validate='key', validatecommand=(reg_int, '%P'))
                self.param_controls[param][self.tb_edit].insert(0, '0')
                self.param_controls[param][self.stVar_view].set('0')
            elif self.param_controls[param][self.num_type] == 'float':
                self.param_controls[param][self.tb_edit].config(validate='key', validatecommand=(reg_float, '%P'))
                self.param_controls[param][self.tb_edit].insert(0, '0.0')
                self.param_controls[param][self.stVar_view].set('0.0')
            elif self.param_controls[param][self.num_type] == 'char':
                self.param_controls[param][self.tb_edit].config(validate='key', validatecommand=(reg_char, '%P'))
                self.param_controls[param][self.tb_edit].insert(0, 'A')
                self.param_controls[param][self.stVar_view].set('A')

            self.param_controls[param][self.lab_name].grid(row=idx, column=0)
            self.param_controls[param][self.tb_edit].grid(row=idx, column=1)
            entry.grid(row=idx, column=2)

        self.fr_params.pack()

        self.fr_buttons = tkinter.Frame(self, bd=5)
        self.btn_send = tkinter.Button(self.fr_buttons, text='Send', command=self.on_btn_send)
        self.btn_update = tkinter.Button(self.fr_buttons, text='Update', command=self.on_btn_update)
        self.btn_send.pack(side=tkinter.LEFT)
        self.btn_update.pack(side=tkinter.LEFT)
        self.fr_buttons.pack()

        self.master.after(self.UPDATE_PARAM_MS, self.refresh_view)

    def get_param_dict(self):
        param_dict = {
            'type': self.name,
            'data': {}
        }

        for param in self.param_controls.keys():
            if self.param_controls[param][self.tb_edit] == '':
                my_mqtt.logger.info(f'Parameter {param} is empty!')
                return

            if self.param_controls[param][self.num_type] == self.INT:
                param_dict['data'][param] = int(self.param_controls[param][self.tb_edit].get())
            elif self.param_controls[param][self.num_type] == self.FLOAT:
                param_dict['data'][param] = float(self.param_controls[param][self.tb_edit].get())
            elif self.param_controls[param][self.num_type] == self.CHAR:
                param_dict['data'][param] = self.param_controls[param][self.tb_edit].get().strip()

        return param_dict

    def on_btn_send(self):
        param_dict = self.get_param_dict()

        enc_msg = self.encode_send(param_dict)
        my_mqtt.logger.info('Sending parameters: '+self.name)
        self.send_message(enc_msg)

    def on_btn_update(self):
        enc_msg = self.encode_get()
        self.send_message(enc_msg)

    def queue_new_value(self, param_data):
        if param_data['type'] != self.name:
            my_mqtt.logger.warning(f'Wrong data type for parameter {self.name}')
        else:
            self.queue.put(param_data)

    def refresh_view(self):
        new_data = None

        while not self.queue.empty():
            new_data = self.queue.get()

        if new_data is not None:
            my_mqtt.logger.debug(f'Update view for parameter {self.name}')
            param_data = new_data['data']
            for param in param_data.keys():
                self.param_controls[param][self.stVar_view].set(str(param_data[param]))

        self.master.after(self.UPDATE_PARAM_MS, self.refresh_view)

    @staticmethod
    def validate_int(input):
        if input.isdigit():
            return True
        elif input == '':
            return True
        else:
            return False

    @staticmethod
    def validate_float(input):
        if input == '':
            return True

        try:
            float(input)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_char(input):
        return True

