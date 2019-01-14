import vlc
import time

i = vlc.Instance('-vvv', '--vout=vdummy')

#m = i.media_new('rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/2', 'sout=#transcode{scodec=none}:http{dst=:8000/live/stream.flv}', 'no-sout-all', 'no-sout-keep', 'rtsp-tcp', 'rtsp-frame-buffer-size=1048576')

#m = i.media_new('rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/2', 'sout=#transcode{scodec=none}:std{access=http,dst=:8000/live/stream.flv}', 'no-sout-all', 'no-sout-keep', 'rtsp-tcp', 'network-caching=1500', 'rtsp-frame-buffer-size=1048576', 'sout-mux-caching=15000')

m = i.media_new('rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/1', 'sout=#transcode{scodec=none}:file{dst=/hovr_data/1.mp4,overwrite}}', 'no-sout-all', 'no-sout-keep', 'rtsp-tcp', 'network-caching=1500', 'rtsp-frame-buffer-size=1048576', 'sout-mux-caching=5000')

#m = i.media_new('rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/1', 'sout=#transcode{scodec=none}:duplicate{dst=file{dst=/hovr_data/1.mp4,overwrite},dst=std{access=http{mime=video/x-flv},mux=ffmpeg{mux=flv},dst=:8000/live/stream.flv}}', 'no-sout-all', 'no-sout-keep', 'rtsp-tcp', 'network-caching=2000', 'rtsp-frame-buffer-size=1048576')
#m = i.media_new('rtsp://nvruser:nvruser123456@192.168.6.10/Streaming/Channels/1', 'sout=#transcode{scodec=none}:file{dst=/hovr_data/1.mp4,overwrite}}', 'no-sout-all', 'no-sout-keep', 'rtsp-tcp', 'network-caching=2000', 'rtsp-frame-buffer-size=1048576')
mp = m.player_new_from_media()

mp.play()
time.sleep(40)
mp.stop()