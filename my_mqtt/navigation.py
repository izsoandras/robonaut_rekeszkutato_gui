import struct
import my_mqtt
import my_mqtt.background_coders

NAVI_TYPE = 0x0D


def encode_navi_data(data):
    isCorrect = True

    if data['type'] != 'navi':
        my_mqtt.logger.warning('Wrong data type as navi: ' + data['type'])
        isCorrect = False

    # TODO: rendes ellenorzes

    data = data['data']

    position = struct.pack('B', data['position'])
    dir = struct.pack('b', data['dir'])
    next_goal = struct.pack('B', data['next_goal'])
    last_gate = struct.pack('B', data['last_gate'])
    orient = struct.pack('b', data['orient'])

    data = my_mqtt.background_coders.concat_fields(position, dir, next_goal, last_gate, orient)
    return my_mqtt.background_coders.construct_message(NAVI_TYPE, data)


def unpack_navi_data(data):
    position = struct.unpack('B', data[0:1])[0]
    dir = struct.unpack('b', data[1:2])[0]
    next_goal = struct.unpack('B', data[2:3])[0]
    last_gate = struct.unpack('B', data[3:4])[0]
    orient = struct.unpack('b', data[4:5])[0]

    return {'position': position,
            'dir': dir,
            'next_goal': next_goal,
            'last_gate': last_gate,
            'orient': orient
            }


def decode_navigation(msg):
    if not my_mqtt.background_coders.validate_message(msg):
        return None

    if (msg[1]) == NAVI_TYPE:
        return {
            'type': 'navi',
            'data': unpack_navi_data(msg[2:])
        }
    else:
        my_mqtt.logger.warning('Wrong topic ' + str(msg[1]) + ' in navigation')
