import struct
import my_mqtt
import my_mqtt.background_coders

BATT_TYPE = 0x01
FRONTL_TYPE = 0x02
BACKL_TYPE = 0x03
SPEEDCTRL_TYPE = 0x04
SIDEDIST_TYPE = 0x05
ORIENTATION_TYPE = 0x0E


def encode_batt_data(battery_dict):
    isCorrect = True
    FACTOR = 209.0 / 45500

    type = bytearray(1)

    if battery_dict['type'] != 'batt':
        my_mqtt.logger.warning('Wrong data type as battery: '+battery_dict['type'])
        isCorrect = False

    type[0] = BATT_TYPE
    battery_dict = battery_dict['data']

    if battery_dict['aux'] >= 2**16 or battery_dict['aux'] < 0:
        my_mqtt.logger.warning('Aux is out of range: '+battery_dict['aux'])
        isCorrect = False

    if battery_dict['aux'] >= 2**16 or battery_dict['aux'] < 0:
        my_mqtt.logger.warning('Aux is out of range: '+battery_dict['aux'])
        isCorrect = False

    if not isCorrect:
        return None

    aux32 = struct.pack('>I', int(battery_dict['aux'] / FACTOR))
    aux = aux32[2:]

    mot32 = struct.pack('>I', int(battery_dict['mot'] / FACTOR))
    mot = mot32[2:]

    data = bytearray(0)
    data.extend(aux)
    data.extend(mot)

    l = struct.pack('>I', len(data))
    length = l[-1:]

    enc_msg = bytearray(0)
    enc_msg.extend(length)
    enc_msg.extend(type)
    enc_msg.extend(data)

    return enc_msg


def unpack_batt_data(data):
    FACTOR = 209.0/45500

    aux_bin = int.from_bytes(data[0:2], 'big')
    mot_bin = int.from_bytes(data[2:4], 'big')

    aux_volt = aux_bin * FACTOR
    mot_volt = mot_bin * FACTOR

    return {'aux': aux_volt,
            'mot': mot_volt}

# TODO: update for new telemetry
def encode_line_data(line_dict):
    isCorrect = True
    type = bytearray(1)

    if line_dict['type'] == 'front_line':
        type[0] = FRONTL_TYPE
    elif line_dict['type'] == 'back_line':
        type[0] = BACKL_TYPE
    else:
        my_mqtt.logger.warning('Wrong data type as line data: ' + line_dict['type'])
        isCorrect = False


    line_dict = line_dict['data']

    if len(line_dict['detection']) != 32:
        my_mqtt.logger.warning('Detection length is not 32!')
        isCorrect = False

    if line_dict['num'] < 0 or line_dict['num'] >= 2**8:
        my_mqtt.logger.warning('Num does not fit in 1 byte')
        isCorrect = False

    # Depricated
    # if line_dict['threshold'] >= 2**32 or line_dict['threshold'] < 0:
    #     my_mqtt.logger.warning('Threshold value is out of range: ' + str(line_dict['threshold']))
    #     isCorrect = False
    #
    # for idx in range(0, 32):
    #     if line_dict['adc'+str(idx)] >= 2 ** 32 or line_dict['threshold'] < 0:
    #         my_mqtt.logger.warning('Wrong adc'+str(idx)+' value: '+str(line_dict['adc'+str(idx)]))
    #         isCorrect = False


    if not isCorrect:
        return None

    detect = struct.pack('>I', int(line_dict['detection'], 2))
    num = struct.pack('B', line_dict['num'])
    pos1 = struct.pack('>f', line_dict['pos1'])
    pos2 = struct.pack('>f', line_dict['pos2'])
    pos3 = struct.pack('>f', line_dict['pos3'])

    data = my_mqtt.background_coders.concat_fields(detect, num, pos1, pos2, pos3)

    return my_mqtt.background_coders.construct_message(type[0], data)


def unpack_line_data(frame):
    detection = '{0:032b}'.format(int.from_bytes(frame[0:4], 'big'))[::-1]

    num = struct.unpack('B', frame[4:5])[0]
    pos1 = struct.unpack('f', frame[5:9])[0]
    pos2 = struct.unpack('f', frame[9:13])[0]
    pos3 = struct.unpack('f', frame[13:17])[0]

    # Depricated
    # threshold = int.from_bytes(frame[8:10], 'big')

    ret = {
        'detection': detection,
        'num': num,
        'pos1': pos1,
        'pos2': pos2,
        'pos3': pos3,
    }


    return ret


def encode_speed_data(speed_dict):
    isCorrect = True

    type = bytearray(1)

    if speed_dict['type'] != 'speed':
        my_mqtt.logger.warning('Wrong data type as speed: '+speed_dict['type'])
        isCorrect = False

    type[0] = SPEEDCTRL_TYPE
    speed_dict = speed_dict['data']

    if speed_dict['duty'] >= 2**16 or speed_dict['duty'] < 0:
        my_mqtt.logger.warning('Duty cycle is out of range: ' + speed_dict['duty'])
        isCorrect = False

    # TODO: Check for distance value to fit in 32 bits

    if not isCorrect:
        return None

    dutycycle32 = struct.pack('>I', speed_dict['duty'])
    dutycycle = dutycycle32[2:]

    current = struct.pack('>f', speed_dict['current'])
    current_setp = struct.pack('>f', speed_dict['current_setp'])
    speed = struct.pack('>f', speed_dict['speed'])
    speed_setp = struct.pack('>f', speed_dict['speed_setp'])
    distance = struct.pack('>I', speed_dict['distance'])
    distance_setp = struct.pack('>I', speed_dict['distance_setp'])

    data = bytearray(0)
    data.extend(dutycycle)
    data.extend(current)
    data.extend(current_setp)
    data.extend(speed)
    data.extend(speed_setp)
    data.extend(distance)
    data.extend(distance_setp)

    l = struct.pack('>I', len(data))
    length = l[-1:]

    enc_msg = bytearray(0)
    enc_msg.extend(length)
    enc_msg.extend(type)
    enc_msg.extend(data)

    return enc_msg


def unpack_speed_data(data):
    duty_cycle = struct.unpack('>H', data[0:2])[0]

    current = struct.unpack('f', data[2:6])[0]
    current_setp = struct.unpack('f', data[6:10])[0]

    speed = struct.unpack('f', data[10:14])[0]
    speed_setp = struct.unpack('f', data[14:18])[0]

    distance = struct.unpack('>I', data[18:22])[0]
    distance_setp = struct.unpack('>I', data[22:])[0]

    return {
        'duty': duty_cycle,
        'current': current,
        'current_setp': current_setp,
        'speed': speed,
        'speed_setp': speed_setp,
        'distance': distance,
        'distance_setp': distance_setp
    }


def encode_side_distance(side_dist_dict):
    isCorrect = True

    if side_dist_dict['type'] != 'side_dist':
        my_mqtt.logger.warning(f'Wrong data type as side distance: ' + side_dist_dict['type'])
        isCorrect = False

    side_dist_dict = side_dist_dict['data']

    left_dist = struct.pack('>I', side_dist_dict['left'])
    right_dist = struct.pack('>I', side_dist_dict['right'])

    data = my_mqtt.background_coders.concat_fields(left_dist, right_dist)
    return my_mqtt.background_coders.construct_message(SIDEDIST_TYPE, data)
    



def unpack_side_distance(data):
    left_dist = struct.unpack('>I', data[0:4])[0]
    right_dist = struct.unpack('>I', data[4:8])[0]

    return {
        'left': left_dist,
        'right': right_dist
    }


def encode_orientation(orientation_dict):
    isCorrect = True

    if orientation_dict['type'] != 'orientation':
        my_mqtt.logger.warning(f'Wrong data type as orientation: ' + orientation_dict['type'])
        isCorrect = False

    if not isCorrect:
        return None

    orientation_dict = orientation_dict['data']

    ori = struct.pack('f', orientation_dict['orientation'])
    ori_setp = struct.pack('f', orientation_dict['orientation_setp'])

    data = my_mqtt.background_coders.concat_fields(ori, ori_setp)

    return my_mqtt.background_coders.construct_message(ORIENTATION_TYPE, data)


def unpack_orientation(data):
    ori = struct.unpack('f', data[0:4])[0]
    ori_setp = struct.unpack('f', data[4:8])[0]

    return {
        'orientation': ori,
        'orientation_setp': ori_setp
    }


def decode_telemetry(msg):
    if not my_mqtt.background_coders.validate_message(msg):
        return None

    if msg[1] == BATT_TYPE:
        return {
                'type': 'batt',
                'data': unpack_batt_data(msg[2:])
                }
    elif msg[1] == FRONTL_TYPE:
        return {
            'type': 'front_line',
            'data': unpack_line_data(msg[2:])
        }
    elif msg[1] == BACKL_TYPE:
        return {
            'type': 'back_line',
            'data': unpack_line_data(msg[2:])
        }
    elif msg[1] == SPEEDCTRL_TYPE:
        return {
            'type': 'speed',
            'data': unpack_speed_data(msg[2:])
        }
    elif msg[1] == SIDEDIST_TYPE:
        return {
            'type': 'side_dist',
            'data': unpack_side_distance(msg[2:])
        }
    elif msg[1] == ORIENTATION_TYPE:
        return {
            'type': 'orientation',
            'data': unpack_orientation(msg[2:])
        }
    else:
        my_mqtt.logger.warning('Wrong topic '+str(msg[1])+' in telemetry')

