#!/usr/bin/python
# -*- coding: utf-8 -*-
import vlc
import time

mp = vlc.MediaPlayer()
m = vlc.Media('rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/2', 'sout=#file{dst=./data/1.mp4}', 'no-sout-all', 'sout-keep', 'rtsp-tcp')
mp.set_media(m)
mp.play()
time.sleep(30)
mp.stop()