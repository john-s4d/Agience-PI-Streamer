import queue
import threading
from datetime import datetime

import adafruit_ssd1306
import board
import busio
import dirsync
import pyaudio
import paho.mqtt.client as mqtt 
from digitalio import DigitalInOut
from adafruit_debouncer import Debouncer

from utils import check_internet, initiate_button, noalsaerr, recording_thread, record_to_file, save_files, stream_audio

INPUT_DEVICES_INDEX = [7, 10, 20]
CLOUD_PATH = '/mount/usb'

def stream(p, input_device, button:Debouncer):
    queue_raw = queue.Queue()
    stop_event = threading.Event()
    record_thread = threading.Thread(target=recording_thread, args=(queue_raw, stop_event, p, input_device))
    stream_thread = threading.Thread(target=stream_audio, args=(queue_raw,))

    record_thread.start()
    stream_thread.start()

    while True:
        button.update()
        if button.fell:
            stop_event.set()
            break

    record_thread.join()
    queue_raw.put(None)
    stream_thread.join()


def main():
    # Create the I2C interface.
    i2c = busio.I2C(board.SCL, board.SDA)

    # 128x32 OLED Display
    reset_pin = DigitalInOut(board.D4)
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
    # Clear the display.
    display.fill(0)
    display.show()
    width = display.width
    height = display.height

    buttonA = initiate_button(board.D5)
    buttonB = initiate_button(board.D6)
    buttonC = initiate_button(board.D12)

    mqttBroker ="44.209.26.208" 
    port= 1883

    client = mqtt.Client("publisherr1")
    client.username_pw_set(username="audiostream", password="7snLBemg1T")
    client.connect(mqttBroker, port) 



    with noalsaerr():
        p = pyaudio.PyAudio()

    pressed = None

    while True:
        try: 
            connected = check_internet()
            buttonA.update()
            buttonB.update()
            buttonC.update()

            buttons = (buttonA, buttonB, buttonC)

            if buttonA.fell:
                pressed = 1
            elif buttonB.fell:
                pressed = 2
            elif buttonC.fell:
                pressed = 3

            if pressed is not None:
                print(f'Button {pressed} pressed')
                device_idx = INPUT_DEVICES_INDEX[pressed-1]
                button_pressed = buttons[pressed-1]
                display.text(f'Channel{pressed} is on', 0, 0, 1)
                display.show()
                if connected:
                    client.connect(mqttBroker)
                    client.publish("audio/stream", f"Channel{pressed} is on")
                    stream(p, device_idx, button=button_pressed)
                    client.publish("audio/stream", f"Channel{pressed} is off")
                else:
                    time_now = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f'./recordings/channel_{pressed}_{time_now}.ogg'
                    record_to_file(p, device_idx, button_pressed, filename)
                pressed = None
                display.fill(0)
                display.text(f'Channel{pressed} is off', 0, 0, 1)
                display.show()

            sy = threading.Thread(target=dirsync.sync, args=['recordings/', CLOUD_PATH, 'sync'])
            sy.start()

        except KeyboardInterrupt:
            print('Received KeyboardInterrupt, terminating...')
            p.terminate()
            break




if __name__ == '__main__':
    main()
