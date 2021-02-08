import paho.mqtt.client as mqtt
import sys

if __name__ == "__main__":
    host_name = sys.argv[1]
    topic = sys.argv[2]

    mqtt_publisher = mqtt.Client('test_publisher')
    mqtt_publisher.connect(host_name)
    mqtt_publisher.loop_start()

    input_str = ''

    while input_str is not 'q':
        print('Enter a series of hexadecimal values (eg.: 00 ab f5 4c), or q to quit:')
        input_str = input()
        if input_str is not 'q':
            msg = bytes.fromhex(input_str)
            mqtt_publisher.publish(topic, msg)
            print('Message sent to '+topic+' with host '+host_name)
            print(msg)


