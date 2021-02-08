from my_mqtt.constants import *
import my_mqtt.background_coders
import struct

SERVOCAL_TYPE = 0x06
CURRSETP_TYPE = 0x07
SPDSETP_TYPE = 0x08
LPARAM_TYPE = 0x09
START_TYPE = 0x0A
STOP_TYPE = 0x0B
GATE_TYPE = 0x0C

# Depricated
# def encode_get_line_delta():
#     return my_mqtt.background_coders.construct_message(0x04, bytes(0))
#

# def encode_line_delta(data):
#     isCorrect = True
#
#     if data['type'] != 'line_delta':
#         my_mqtt.logger.warning('Wrong data type as line delta: ' + data['type'])
#         isCorrect = False
#
#     if not my_mqtt.background_coders.check_uint16(data['data']['delta']):
#         logger.warning('Line delta is out of range: ' + data['type']['delta'])
#         isCorrect = False
#
#     if not isCorrect:
#         return None
#
#     line_delta32 = struct.pack('>I', data['data']['delta'])
#
#     return my_mqtt.background_coders.construct_message(0x04, line_delta32[2:])
#
#
# def unpack_line_delta(data):
#     if len(data) != 2:
#         logger.error('Insufficient data bytes in line delta message: '+data.hex())
#
#     delta = struct.unpack('>H', data)[0]
#
#     return {
#         'delta': delta
#     }


def encode_get_servo_cal():
    return my_mqtt.background_coders.construct_message(SERVOCAL_TYPE, bytes(0))


def encode_servo_cal(servo_data):
    isCorrect = True

    if servo_data['type'] != 'servo_cal':
        logger.warning('Wrong data type as servo data: ' + servo_data['type'])
        isCorrect = False

    servo_data = servo_data['data']

    for key in servo_data.keys():
        isCorrect = my_mqtt.background_coders.check_uint16(servo_data[key], f'servo {key}') and isCorrect

    if not isCorrect:
        return None

    center132 = struct.pack('>H', servo_data['center1'])
    center232 = struct.pack('>H', servo_data['center2'])
    # delta32 = struct.pack('>I', servo_data['delta'])
    ESCmin32 = struct.pack('>H', servo_data['delta1'])
    ESCmax32 = struct.pack('>H', servo_data['delta2'])

    data = my_mqtt.background_coders.concat_fields(center132, center232, ESCmin32, ESCmax32)
    return my_mqtt.background_coders.construct_message(SERVOCAL_TYPE, data)


def unpack_servo_cal(data):
    if len(data) != 8:
        logger.error('Insufficient data bytes in servo cal message: '+data.hex())

    center1 = struct.unpack('>H', data[0:2])[0]
    center2 = struct.unpack('>H', data[2:4])[0]
    # delta = struct.unpack('>H', data[4:6])[0]
    ESCmin = struct.unpack('>H', data[4:6])[0]
    ESCmax = struct.unpack('>H', data[6:])[0]

    return {
        'center1':center1,
        'center2': center2,
        'delta1': ESCmin,
        'delta2': ESCmax
    }

# Depricated
# def encode_get_speed_control_params():
#     return my_mqtt.background_coders.construct_message(0x07, bytes(0))
#
#
# def encode_speed_control_params(speed_control_data):
#     isCorrect = True
#
#     if speed_control_data['type'] != 'speed_params':
#         logger.warning('Wrong data type as speed control data: ' + speed_control_data['type'])
#         isCorrect = False
#
#     if not isCorrect:
#         return False
#
#     speed_control_data = speed_control_data['data']
#
#     currentK = struct.pack('f', speed_control_data['currentK'])
#     currentZ = struct.pack('f', speed_control_data['currentZ'])
#     speedK = struct.pack('f', speed_control_data['speedK'])
#     speedZ = struct.pack('f', speed_control_data['speedZ'])
#
#     data = my_mqtt.background_coders.concat_fields(currentK, currentZ, speedK, speedZ)
#
#     return my_mqtt.background_coders.construct_message(0x07, data)
#
#
# def unpack_speed_control_params(data):
#     if len(data) != 16:
#         logger.error('Insufficient data bytes in speed control params message: '+data.hex())
#
#     currentK = struct.unpack('f', data[0:4])[0]
#     currentZ = struct.unpack('f', data[4:8])[0]
#     speedK = struct.unpack('f', data[8:12])[0]
#     speedZ = struct.unpack('f', data[12:])[0]
#
#     return {
#         'currentK': currentK,
#         'currentZ': currentZ,
#         'speedK': speedK,
#         'speedZ': speedZ
#     }


def encode_get_current_setpoint():
    return my_mqtt.background_coders.construct_message(CURRSETP_TYPE, bytes(0))


def encode_current_setpoint(data):
    isCorrect = True

    if data['type'] != 'current_setp':
        my_mqtt.logger.warning('Wrong data type as current setpoint: ' + data['type'])
        isCorrect = False

    if not isCorrect:
        return None

    current_setp = struct.pack('f', data['data']['setpoint'])

    return my_mqtt.background_coders.construct_message(CURRSETP_TYPE, current_setp)


def unpack_current_setpoint(data):
    if len(data) != 4:
        logger.error('Insufficient data bytes in current setpoint message: '+data.hex())

    setpoint = struct.unpack('f', data)[0]

    return{
        'setpoint':setpoint
    }


def encode_get_speed_setpoint():
    return my_mqtt.background_coders.construct_message(SPDSETP_TYPE, bytes(0))


def encode_speed_setpoint(data):
    isCorrect = True

    if data['type'] != 'speed_setp':
        my_mqtt.logger.warning('Wrong data type as speed setpoint: ' + data['type'])
        isCorrect = False

    if not isCorrect:
        return None

    speed_setp = struct.pack('f', data['data']['setpoint'])

    return my_mqtt.background_coders.construct_message(SPDSETP_TYPE, speed_setp)


def unpack_speed_setpoint(data):
    if len(data) != 4:
        logger.error('Insufficient data bytes in speed setpoint message: '+data.hex())

    setpoint = struct.unpack('f', data)[0]

    return{
        'setpoint':setpoint
    }


def encode_start_command():
    return my_mqtt.background_coders.construct_message(START_TYPE, bytes(0))


def unpack_start_command(data):
    if len(data) > 0:
        logger.warning('Unexpected data in START ack message: '+data.hex())

    return None


def encode_emergency_stop():
    return my_mqtt.background_coders.construct_message(STOP_TYPE, bytes(0))


def unpack_emergency_stop(data):
    if len(data) > 0:
        logger.warning('Unexpected data in STOP ack message: ' + data.hex())

    return None


def encode_get_line_params():
    return my_mqtt.background_coders.construct_message(LPARAM_TYPE, bytes(0))


def encode_line_params(data):
    isCorrect = True

    if data['type'] != 'line_param':
        my_mqtt.logger.warning('Wrong data type as line_parameters: ' + data['type'])
        isCorrect = False

    if not isCorrect:
        return None

    kszi = struct.pack('f', data['data']['kszi'])
    d0 = struct.pack('f', data['data']['d0'])
    dv = struct.pack('f', data['data']['dv'])

    data = my_mqtt.background_coders.concat_fields(kszi, d0, dv)

    return my_mqtt.background_coders.construct_message(LPARAM_TYPE, data)


def encode_get_gate():
    return my_mqtt.background_coders.construct_message(GATE_TYPE, bytes(0))


def unpack_line_params(data):
    if len(data) != 12:
        logger.error('Insufficient data bytes in line params message: '+data.hex())

    kszi = struct.unpack('f', data[0:4])[0]
    d0 = struct.unpack('f', data[4:8])[0]
    dv = struct.unpack('f', data[8:12])[0]

    return{
        'kszi':kszi,
        'd0': d0,
        'dv': dv
    }

def encode_gate(data):
    isCorrect = True

    if data['type'] != 'gate':
        my_mqtt.logger.warning('Wrong data type as gate: ' + data['type'])
        isCorrect = False

    if len(data['data']) != 1:
        my_mqtt.logger.error('More than 1 character for gate name: ' + data['data']['name'])
        isCorrect = False

    if not isCorrect:
        return None

    data = data['data']['name'].encode()

    return my_mqtt.background_coders.construct_message(GATE_TYPE, data)


def unpack_gate(data):
    name_char = str(data, 'utf-8')

    return {
        'name': name_char
    }


def decode_command(msg):
    if not my_mqtt.background_coders.validate_message(msg):
        return None

    # if(msg[1]) == 0x04:
    #     return {
    #         'type': 'line_delta',
    #         'data': unpack_line_delta(msg[2:])
    #     }
    if (msg[1]) == SERVOCAL_TYPE:
        return {
            'type': 'servo_cal',
            'data': unpack_servo_cal(msg[2:])
        }
    # elif (msg[1]) == 0x07:
    #     return {
    #         'type': 'speed_params',
    #         'data': unpack_speed_control_params(msg[2:])
    #     }
    elif (msg[1]) == CURRSETP_TYPE:
        return {
            'type': 'current_setp',
            'data': unpack_current_setpoint(msg[2:])
        }
    elif (msg[1]) == SPDSETP_TYPE:
        return {
            'type': 'speed_setp',
            'data': unpack_speed_setpoint(msg[2:])
        }
    elif (msg[1] == LPARAM_TYPE):
        return {
            'type': 'line_param',
            'data': unpack_line_params(msg[2:])
        }
    elif (msg[1]) == START_TYPE:
        return {
            'type': 'start',
            'data': unpack_start_command(msg[2:])
        }
    elif (msg[1]) == STOP_TYPE:
        return {
            'type': 'stop',
            'data': unpack_emergency_stop(msg[2:])
        }
    elif (msg[1]) == GATE_TYPE:
        return {
            'type': 'gate',
            'data': unpack_gate(msg[2:])
        }
    else:
        logger.warning('Wrong topic '+str(msg[1])+' in commands')