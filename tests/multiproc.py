
import threading
import time
import queue

import pyaudio
import shout
from pydub import AudioSegment

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 30
INPUT_DEVICE_INDEX = 20

def recording_thread(queue, record_time):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=INPUT_DEVICE_INDEX,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    start_time = time.time()
    while time.time() - start_time < record_time:
        data = stream.read(CHUNK)
        frames.append(data)
        if (time.time() - start_time) % 1 < 0.01:
            queue.put(b''.join(frames))
            frames = []

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    queue.put(b''.join(frames))
    queue.put(None)


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

if __name__ == '__main__':
    queue = queue.Queue()
    record_thread = threading.Thread(target=recording_thread, args=(queue, 15))
    stream_thread = threading.Thread(target=stream_audio, args=(queue,))

    record_thread.start()
    stream_thread.start()

    record_thread.join()
    queue.put(None)
    stream_thread.join()
