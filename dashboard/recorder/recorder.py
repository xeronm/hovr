import os
import logging
import queue
import threading
import socket
import json
import vlc
import time
import datetime
import requests
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from urllib.parse import urlsplit, urlunsplit
from dashboard.inventory import RecorderMethod

THREAD_CHECK_TIMEOUT_SEC = 0.5

_recorder = None
logger = logging.getLogger('recorder')

def GetRecorder():
    global _recorder
    if _recorder == None:
        _recorder = RecorderManager()
    return _recorder

class Recorder(threading.Thread):

    def __init__(self, camera, profile, stop_time):
        super().__init__(target=self.main)
        self._event_done = threading.Event()
        self.camera = camera
        self.profile = profile
        self._event_done.clear()
        self.daemon = True
        self.start_time = timezone.localtime()
        self.stop_time = stop_time
        self.start()

    def bind_recorder(self, date_time):
        self.record_path = os.path.join(settings.HOVR_RECORDING_PATH, self.camera.name, date_time.strftime('%Y%m%d'))

        urlc = urlsplit(self.camera.address)
        self.context = {
            'record_path': self.record_path,
            'camera_name': self.camera.name, 
            'camera_netloc': urlc.netloc,
            'user_name': self.camera.user_name, 
            'password': self.camera.password, 
            'date_time': date_time.strftime('%Y%m%d_%H%M%S'),
            'day_quarter': int((date_time.hour+1)/6)
        }
        self.record_url = self.profile.render_url(**self.context)
        self.record_filename = self.profile.render_filename(**self.context)
        self.context['file_name'] = self.record_filename
        self.context['url'] = self.record_url

        path, filename = os.path.split(self.record_filename)
        os.makedirs(path, exist_ok=True)

    def main(self):
        while not self._event_done.isSet():
            pass

    def stop(self):
        self._event_done.set()


class RecorderVLC(Recorder):

    def newPlayer(self):
        self.piece_start_time = timezone.localtime()
        self.record_length = self.profile.interval
        self.bind_recorder(self.piece_start_time)

        args = list([a.render(**self.context) for a in self.profile.arguments.all()])
        logger.info('player new piece "%s": %s %s', self.camera.name, self.record_url, args)

        i = vlc.Instance()
        mp = i.media_new(self.record_url, *args).player_new_from_media()
        mp.play()

        return mp

    def main(self):
        player = self.newPlayer()
        player_prev = None
        while not self._event_done.isSet():
            date_time = timezone.localtime()
            if self.stop_time and self.stop_time < date_time:
                break;
            self.piece_time = player.get_time()
            if self.piece_time/1000 >= self.record_length:
                player_prev = player
                player = self.newPlayer()
            elif player_prev and self.piece_time > 2000:
                player_prev.stop()
                player_prev.release()

            time.sleep(THREAD_CHECK_TIMEOUT_SEC)

        player.stop()
        player.release()

class RecorderHTTPGet(Recorder):

    def main(self):
        self.next_snapshot_time = None
        while not self._event_done.isSet():
            date_time = timezone.localtime()
            if not self.next_snapshot_time or self.next_snapshot_time < date_time:
                self.next_snapshot_time = date_time + datetime.timedelta(seconds=self.profile.interval)
                self.bind_recorder(self.next_snapshot_time)
                r = requests.get(self.record_url, auth=(self.camera.user_name, self.camera.password))
                with open(self.record_filename, 'wb+') as f:
                    f.write(r.content)
            if self.stop_time and self.stop_time < date_time:
                break;
            time.sleep(THREAD_CHECK_TIMEOUT_SEC)


RECORDER_METHOD_MAP = {
    RecorderMethod.VLC: RecorderVLC,
    RecorderMethod.VLC_SNAP: RecorderVLC,
    RecorderMethod.HTTP_GET: RecorderHTTPGet,
}

class RecorderRef():
    def __init__(self, recorder):
        self.recorder = recorder
        self.update_time = None


class RecorderManager():

    def __init__(self):
        self.recorders = {}
        self.worker_thread = threading.Thread(target = self.workerMain)
        self._event_done = threading.Event()

    def workerMain(self):
        ScheduleIntervals = apps.get_model(app_label='inventory', model_name='ScheduleIntervals')
        while not self._event_done.isSet():
            time.sleep(THREAD_CHECK_TIMEOUT_SEC)
            date_time = timezone.localtime()
            schedules = {}
            for si in ScheduleIntervals.qsActiveIntervals(date_time):
                next_switch = schedules.get(si.schedule)
                next_switch2 = si.nextSwitchTime(date_time)
                if next_switch is None or (next_switch[0] is not None and (next_switch[0] < next_switch2 or next_switch2 is None)):
                    schedules[si.schedule] = (next_switch2,)
            # update all active recorders
            for sh, nst in schedules.items():
                for camera in sh.cameras.all():
                    for profile in [camera.recorder_profile, camera.recorder_profile2]:
                        reckey = (camera.pk, profile.pk)
                        recorderRef = self.recorders.get(reckey)
                        if recorderRef and not recorderRef.recorder.is_alive():
                            logger.warning('Recorder thread %d for camera "%s" is dead -> restart', recorderRef.recorder.ident, camera.name)
                            del self.recorders[reckey]
                            recorderRef = None
                        if not recorderRef:
                            recorderRef = RecorderRef(RECORDER_METHOD_MAP[profile.method](camera, profile, nst[0]))
                            logger.warning('Starting thread %d for camera "%s":"%s"', recorderRef.recorder.ident, camera.name, profile.name)
                            self.recorders[reckey] = recorderRef
                        recorderRef.update_time = date_time
            # remove obsoleted recorders
            for reckey, recorderRef in dict([(k, r) for k, r in self.recorders.items() if r.update_time is None or r.update_time < date_time]):
                del self.recorders[reckey]
                logger.warning('Stoping thread %d for camera "%s"', recorderRef.recorder.ident, recorderRef.camera.name)
                recorderRef.recorder.stop()


    def startWorkerThread(self):
        if os.environ.get('RUN_MAIN') != 'true':  
            return False

        if self.worker_thread.is_alive():
           logger.info('Worker thread is running')
           return True

        logger.info('Starting worker thread...')
        self._event_done.clear()
        self.worker_thread.daemon = True
        self.worker_thread.start()
        return True

    def stopWorkerThread(self, wait=False):
        if os.environ.get('RUN_MAIN') != 'true':  
            return False

        if not self.worker_thread.is_alive():
           logger.info('Worker thread is not running')
           return True

        logger.info('Stoping worker thread...')
        self._event_done.set()
        if wait:
            self.worker_thread.join()
        logger.info('Worker thread stoped.')
        return True

