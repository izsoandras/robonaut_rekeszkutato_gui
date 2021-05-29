import paho.mqtt.client as mqtt
import time
from datetime import datetime
import numpy as np
import json

import my_mqtt
import my_mqtt.log
import my_mqtt.telemetry
import my_mqtt.commands
import my_mqtt.navigation
import os


def run(period_sec):
    # Create client instance
    # Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
    client = mqtt.Client('test_source')

    # Connect to broker
    # connect(host, port=1883, keepalive=60, bind_address="")
    client.connect('localhost')

    
    with open('assets/skill_course_routes.json') as course_file:
        course_dict = json.load(course_file)

    det_idx = 1
    det_dir = 1

    next_mtx = np.array(course_dict['Next'])
    x = bytearray(1)
    curr_node = 0
    goal_node = 0

    while True:
        # Battery simulation
        batt_data = {
            'type': 'batt',
            'data': {
                'aux': 9*(1+0.2*(np.random.rand()-0.5)),
                'mot': 12*(1+0.2*(np.random.rand()-0.5))
            }
        }
        enc_data = my_mqtt.telemetry.encode_batt_data(batt_data)
        client.publish(my_mqtt.TELEMETRY_TOPIC, enc_data)

        # Front line sensor simulation
        line_data = {
            'type': 'front_line',
            'data': {'detection': '0' * 32,
                     'num': 2,
                     'pos1': 14.34*(1+0.2*(np.random.rand()-0.5)),
                     'pos2': 16.34*(1+0.2*(np.random.rand()-0.5)),
                     'pos3': 18.34*(1+0.2*(np.random.rand()-0.5))
                     }
        }

        detection = ['0'] * 32
        detection[det_idx] = '1'
        line_data['data']['detection'] = ''.join(detection)
        if det_idx >= 30 or det_idx <= 0:
            det_dir = -1 * det_dir

        det_idx = det_idx + det_dir

        enc_data = my_mqtt.telemetry.encode_line_data(line_data)
        client.publish(my_mqtt.TELEMETRY_TOPIC, enc_data)

        # Back line sensor
        line_data['type'] = 'back_line'
        enc_data = my_mqtt.telemetry.encode_line_data(line_data)
        client.publish(my_mqtt.TELEMETRY_TOPIC, enc_data)

        # Speed data
        speed_data = {
            'type': 'speed',
            'data': {
                'duty': 128,
                'current': int(250*(1+0.2*(np.random.rand()-0.5))),
                'current_setp': 250,
                'speed': int(600*(1+0.2*(np.random.rand()-0.5))),
                'speed_setp': 600,
                'distance': int(500*(1+0.2*(np.random.rand()-0.5))),
                'distance_setp': 500
            }
        }

        enc_data = my_mqtt.telemetry.encode_speed_data(speed_data)
        client.publish(my_mqtt.TELEMETRY_TOPIC, enc_data)

        ## Side distance
        side_distance_data = {
            'type': 'side_dist',
            'data': {
                'left': int(300*(1+0.05*(np.random.rand()-0.5))),
                'right': int(250*(1+0.05*(np.random.rand()-0.5)))
            }
        }

        enc_data = my_mqtt.telemetry.encode_side_distance(side_distance_data)
        # client.publish(my_mqtt.TELEMETRY_TOPIC, enc_data)

        ## Orientation
        orientation_data = {
            'type': 'orientation',
            'data': {
                'orientation': 180 * (1+0.1*(np.random.rand()-0.5)),
                'orientation_setp': 180 * (1+0.05*(np.random.rand()-0.5))
            }
        }

        enc_data = my_mqtt.telemetry.encode_orientation(orientation_data)
        client.publish(my_mqtt.TELEMETRY_TOPIC, enc_data)

        # Parameters
        ## Servo
        servo_data = {
            'type': 'servo_cal',
            'data': {
                'center1': 1499,
                'center2': 1499,
                'delta1': 1059,
                'delta2': 1859
            }
        }

        enc_data = my_mqtt.commands.encode_servo_cal(servo_data)
        client.publish(my_mqtt.PARAMS_TOPIC, enc_data)

        ## Current setp
        data = {
            'type': 'current_setp',
            'data': {
                'setpoint': 3
            }
        }

        enc_data = my_mqtt.commands.encode_current_setpoint(data)
        client.publish(my_mqtt.PARAMS_TOPIC, enc_data)

        ## Speed setp
        data = {
            'type': 'speed_setp',
            'data': {
                'setpoint': 32
            }
        }

        enc_data = my_mqtt.commands.encode_speed_setpoint(data)
        client.publish(my_mqtt.PARAMS_TOPIC, enc_data)

        ## Line params
        data = {
            'type': 'line_param',
            'data': {
                'kszi': 1.5,
                'd0': 3,
                'dv': 5
            }
        }

        enc_data = my_mqtt.commands.encode_line_params(data)
        client.publish(my_mqtt.PARAMS_TOPIC, enc_data)

        ## Gate
        data = {
            'type': 'gate',
            'data': {
                'name': 'B'
            }
        }

        enc_data = my_mqtt.commands.encode_gate(data)
        client.publish(my_mqtt.PARAMS_TOPIC, enc_data)

        # Navigation
        ## navi
        data = {
            'type': 'navi',
            'data': {
                     'position': 14,
                     'dir': -3,
                     'next_goal': 14,
                     'last_gate': 14,
                     'orient': -1
                     }
        }

        enc_data = my_mqtt.navigation.encode_navi_data(data)
        client.publish(my_mqtt.COURSE_POS_TOPIC, enc_data)

        # LOG
        log_data = {
            'level': 'warning',
            'message': 'test message: ' + str(datetime.now())
        }

        enc_data = my_mqtt.log.encode_log(log_data)
        client.publish(my_mqtt.LOGGER_TOPIC, enc_data)

        time.sleep(period_sec)


def get_path(next_mtx, start_point, end_point):
    if next_mtx[start_point][end_point] is not None:
        curr_point = start_point
        path = [start_point]
        while curr_point != end_point:
            curr_point = int(next_mtx[int(curr_point)][end_point])
            path.append(curr_point)

    else:
        path = []

    return path


if __name__ == "__main__":
    run(0.01)
