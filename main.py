import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import json
import multiprocessing

import my_gui
import my_mqtt
import my_mqtt.commands
from clients.mqtt.testing_tools import test_source

import logging
import os

ENABLE_TEST_SOURCE = False

DB_NAME = 'testdb'
DB_HOST = 'localhost'

LOGFIELD_LINE_NUM_BASE = 13
LOGFIELD_LINE_NUM_DIAGRAM = 6

root = tk.Tk()

tabs = None
plot_tab = None

mqtt_startstop_publisher = mqtt.Client('startstop_publisher')
test_producer_process = None


def load_conf():

    try:
        with open('conf.json') as f:
            conf_dict = json.load(f)

        global ENABLE_TEST_SOURCE

        global DB_NAME
        global DB_HOST

        ENABLE_TEST_SOURCE = conf_dict['enable_test_source']

        my_mqtt.HOST_NAME = conf_dict['mqtt_host']
        my_mqtt.USER_NAME = conf_dict['mqtt_user']
        my_mqtt.PASSWORD = conf_dict['mqtt_pwd']

        DB_HOST = conf_dict['database_host']
        DB_NAME = conf_dict['database_name']

        logger.debug('Values updated from conf file')
    except FileNotFoundError:
        logger.warning('Conf file not found')
        pass


def emergency_stop():
    mqtt_startstop_publisher.publish(my_mqtt.COMMAND_TOPIC, my_mqtt.commands.encode_emergency_stop())
    logger.info('Sent STOP message')


def send_start():
    mqtt_startstop_publisher.publish(my_mqtt.COMMAND_TOPIC, my_mqtt.commands.encode_start_command())
    logger.info('Sent START message')


def on_spacebar(event):
    emergency_stop()


def on_closing():
    global test_producer_process
    global root

    if test_producer_process is not None:
        test_producer_process.kill()

    logger.warning('Application closed')
    root.destroy()


def on_tab_change(event):
    tabs = event.widget
    if tabs.select():
        if tabs.index('current') == 2:
            tabs.nametowidget(tabs.select()).update_dropdown()  # here, 'notebook' could be any widget

        if tabs.index('current') == 1:
            log_field.set_visible_line_number(LOGFIELD_LINE_NUM_DIAGRAM)
            plot_tab.is_visible = True
        else:
            log_field.set_visible_line_number(LOGFIELD_LINE_NUM_BASE)
            plot_tab.is_visible = False


if __name__=="__main__":
    # args_parser = argparse.ArgumentParser()
    # args_parser.add_argument("--develop", help="Develop mode", action="store_true")
    # args = args_parser.parse_args()

    logger = logging.getLogger('robotlog')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('robot.log', mode='w')
    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.WARNING)

    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(c_format)
    file_handler.setFormatter(f_format)

    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.warning('Program start')
    logger.info('Logging is alive')

    load_conf()

    #
    # Set up influxdb connection

    influxDB = InfluxDBClient(DB_HOST)
    # check connection to database. Throws ConnectionError if not TODO: handle error
    try:
        influxDB.ping()
        logger.info('DB connection okay')
    except:
        tk.messagebox.showerror('DB error', 'Could not connect to InfluxDB')
        logger.error('DB connection ERROR')
        raise SystemExit

    dbs = influxDB.get_list_database()
    # create database if not exists
    if not {'name': DB_NAME} in dbs:
        influxDB.create_database(DB_NAME)

    # switch to database
    influxDB.switch_database(DB_NAME)

    mqtt_startstop_publisher.username_pw_set(my_mqtt.USER_NAME, my_mqtt.PASSWORD)
    mqtt_startstop_publisher.connect(my_mqtt.HOST_NAME)
    mqtt_startstop_publisher.loop_start()

    #
    # Build GUI                                                            # Main window
    root.title('RKI RobonAUT Diagnostics')
    root.iconbitmap("assets/icon.ico")

    # Emergency stop
    btn_emergency = tk.Button(master=root, text="EMERGENCY STOP", command=emergency_stop, bg='red')
    btn_emergency.pack(side=tk.BOTTOM, fill='x', anchor=tk.S)
    # Start
    btn_start = tk.Button(master=root, text="START", command=send_start, bg='green')
    btn_start.pack(side=tk.BOTTOM, anchor=tk.S)
    # Param setter
    param_frame = my_gui.SetParamsFrame(root)
    param_frame.pack(side=tk.RIGHT, fill=tk.Y)
    # Log field
    log_field = my_gui.ScreenLoggerFrame(root, LOGFIELD_LINE_NUM_BASE)
    log_field.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.S)

    # Tabs
    tabs = ttk.Notebook(root)                                                   # Tab control

    param_tab = tk.Frame(tabs)              # Parameter change tab
    # param_frame = my_gui.SetParamsFrame(param_tab)

    with open('assets/skill_course_2021_hor.json') as f:
        point_coords = json.load(f)

    image_frame = my_gui.SkillCourseFrame(param_tab, 'assets/skill_course_2021_hor.jpg', point_coords, highlightthickness=0)
    # param_frame.pack(side=tk.RIGHT, fill=tk.Y)
    image_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    plot_tab = my_gui.PlotFrame(tabs, influxDB)
    db_tab = my_gui.DBframe(tabs, influxDB)                                     # Tab with the data control functions

    # Add all tabs to the tab control
    tabs.add(param_tab, text='params')
    tabs.add(plot_tab, text='graphs')
    tabs.add(db_tab, text='data control')
    tabs.bind("<<NotebookTabChanged>>", on_tab_change)

    # expand: equal distribution of space between widgets that have non zero expand value, when parent is expanded
    # fill: the widget takes up all the space in both X and Y axis
    tabs.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


    logger.info('GUI set up')

    # Start test source
    # if args.develop:
    if os.environ.get('RKID_DEVELOP') == '1':
        if ENABLE_TEST_SOURCE:
            test_producer_process = multiprocessing.Process(target=test_source.run, args=(0.2,))
            test_producer_process.start()
            logger.info('Test source started')
        else:
            logger.info('Test source disabled')

    logger.info('-------SETUP COMPLETE----------')

    #
    # Start event loops
    root.bind("<space>", on_spacebar)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

