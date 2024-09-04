import time
import urllib.request
from ctypes import *
from contextlib import contextmanager
from threading import Event

import digitalio
import pyaudio
import shout
from adafruit_debouncer import Debouncer
from pydub import AudioSegment


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 30
INPUT_DEVICE_INDEX = 7

SHOUT_HOST = '44.209.26.208'
SHOUT_PORT = 8000
SHOUT_USER = 'source'
SHOUT_PASSWORD = '5Cb582u@duCd'
SHOUT_MOUNT = "/live"

# SHOUT_FORMAT = 'mp3'
# SHOUT_FORMAT = 'vorbis' | 'mp3'
# SHOUT_PROTOCOL = 'http' | 'xaudiocast' | 'icy'
# SHOUT_NAME = ''
# SHOUT_GENRE = ''
# SHOUT_URL = ''
# SHOUT_PUBLIC = 0 | 1


def check_internet(host='http://google.com') -> bool:
    """Check if the internet is available."""
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

def initiate_button(board_pin):
    button_pin = digitalio.DigitalInOut(board_pin)
    button_pin.direction = digitalio.Direction.INPUT
    button_pin.pull = digitalio.Pull.UP
    button = Debouncer(button_pin)

    return button

def record_to_file(p: pyaudio.PyAudio, input_device:int, filename, button: Debouncer):
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=input_device,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        if button.fell:
            break

    raw_input = b''.join(frames)

    audio_segment = AudioSegment(
        raw_input, 
        sample_width=2, 
        frame_rate=44100, 
        channels=2
    )
    audio_segment.export(filename)

    print("Finished recording")


def recording_thread(queue, event:Event, p:pyaudio.PyAudio, input_device):

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=input_device,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    start_time = time.time()
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if (time.time() - start_time) % 1 < 0.01:
            queue.put(b''.join(frames))
            frames = []
        if event.is_set():
            break

    print("* done recording")

    stream.stop_stream()
    stream.close()
    queue.put(b''.join(frames))
    queue.put(None)


def save_files(address):
    pass

def stream_audio(queue):
    s = shout.Shout()
    s.host = '44.209.26.208'
    s.user = 'source'
    s.password = '5Cb582u@duCd'
    s.mount = "/live"
    # filename = 'out.ogg'
    total = 0
    # s.set_metadata({'song': filename})
    s.open()

    while True:
        data = queue.get()
        if not data:
            break

        raw_input = data

        audio_segment = AudioSegment(
            raw_input, 
            sample_width=2, 
            frame_rate=44100, 
            channels=2
        )
        ogg_data = audio_segment.export(format='ogg')
        nbuf = ogg_data.read(4096)
        while 1:
            buf = nbuf
            nbuf = ogg_data.read(4096)
            total = total + len(buf)
            if len(buf) == 0:
                break
            s.send(buf)
            s.sync()

    s.close()


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

