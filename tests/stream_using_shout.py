#!/usr/bin/env python

# usage: ./example.py /path/to/file1 /path/to/file2 ...
import shout
import sys
import time

s = shout.Shout()
print("Using libshout version %s" % shout.version())

s.host = '44.209.26.208'
# s.port = 8000
s.user = 'source'
s.password = '5Cb582u@duCd'
s.mount = "/live"
# s.format = 'mp3'
# s.format = 'vorbis' | 'mp3'
# s.protocol = 'http' | 'xaudiocast' | 'icy'
# s.name = ''
# s.genre = ''
# s.url = ''
# s.public = 0 | 1
# s.audio_info = { 'key': 'val', ... }
#  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
#   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

s.open()

total = 0
st = time.time()
for fa in sys.argv[1:]:
    print("opening file %s" % fa)
    f = open(fa, 'rb')
    s.set_metadata({'song': fa})

    nbuf = f.read(4096)
    while 1:
        buf = nbuf
        nbuf = f.read(4096)
        total = total + len(buf)
        if len(buf) == 0:
            break
        s.send(buf)
        s.sync()
    f.close()

    et = time.time()
    br = total*0.008/(et-st)
    print("Sent %d bytes in %d seconds (%f kbps)" % (total, et-st, br))

s.close()
