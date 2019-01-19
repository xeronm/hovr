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
import traceback
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from urllib.parse import urlsplit, urlunsplit
from dashboard.inventory import RecorderMethod, CameraState

THREAD_CHECK_TIMEOUT_SEC = 0.5

_recorder = None
logger = logging.getLogger('recorder')

def GetRecorder():
    global _recorder
    if _recorder == None:
        _recorder = RecorderManager()
    return _recorder

class Recorder(threading.Thread):

    def __init__(self, camera, profile, stop_time, subpath):
        super().__init__(target=self.main)
        self._event_done = threading.Event()
        self.camera = camera
        self.profile = profile
        self._event_done.clear()
        self.daemon = True
        self.start_time = timezone.localtime()
        self.stop_time = stop_time
        self.subpath = subpath
        self.start()

    @property
    def id(self):
        return self.ident

    def recycle(self, date_time):
        if not self.profile.recycle_timeout:
            return
        record_root = os.path.join(settings.HOVR_RECORDING_PATH, self.camera.name)
        for subdir in os.listdir(record_root):
            try:
                dtime = datetime.datetime.strptime(subdir, '%Y%m%d').replace(tzinfo=date_time.tzinfo)
                if date_time < dtime + datetime.timedelta(days=self.profile.recycle_timeout):
                    continue
                record_daypath = os.path.join(record_root, subdir)
                record_path = os.path.join(record_daypath, self.subpath)
                if os.path.isdir(record_path):
                    logger.info('Recyle: %s', record_path)
                    os.removedirs(record_path)
                if not os.listdir(record_daypath):
                    os.rmdir(record_daypath)
            except Exception as E:
                logger.error('Recorder:recycle Unhandled exception: %s', traceback.format_exc())


    def bind_recorder(self, date_time):
        self.record_path = os.path.join(settings.HOVR_RECORDING_PATH, self.camera.name, date_time.strftime('%Y%m%d'), self.subpath)

        urlc = urlsplit(self.camera.address)
        self.context = {
            'record_path': self.record_path,
            'camera_name': self.camera.name, 
            'camera_netloc': urlc.netloc,
            'camera_address': self.camera.address,
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
        #logger.info('player new piece "%s": %s %s', self.camera.name, self.record_url, args)

        i = vlc.Instance()
        mp = i.media_new(self.record_url, *args).player_new_from_media()
        mp.play()

        return mp

    def main(self):
        player = self.newPlayer()
        player_prev = None
        self.recorderVLC = player
        next_recylce_check = None
        try:
            while not self._event_done.isSet():
                date_time = timezone.localtime()
                if self.stop_time and self.stop_time < date_time:
                    break;
                self.piece_time = player.get_time()
                if self.piece_time/1000 >= self.record_length:
                    player_prev = player
                    player = self.newPlayer()
                elif player_prev and self.piece_time > 3000:
                    self.recorderVLC = player
                    player_prev.stop()
                    player_prev.release()
    
                time.sleep(THREAD_CHECK_TIMEOUT_SEC)
                if not next_recylce_check or date_time > next_recylce_check:
                    next_recylce_check = date_time + datetime.timedelta(minutes=10)
                    self.recycle(date_time)
        finally:
            if player_prev:
                player_prev.stop()
                player_prev.release()
            player.stop()
            player.release()

class RecorderHTTPGet(Recorder):

    def main(self):
        self.recorderHTTPGet = {}
        self.next_snapshot_time = None
        while not self._event_done.isSet():
            date_time = timezone.localtime()
            if not self.next_snapshot_time or self.next_snapshot_time < date_time:
                try:
                    self.next_snapshot_time = date_time + datetime.timedelta(seconds=self.profile.interval)
                    self.recorderHTTPGet['last_snapshot_time'] = date_time
                    self.bind_recorder(self.next_snapshot_time)
                    r = requests.get(self.record_url, auth=(self.camera.user_name, self.camera.password))
                    with open(self.record_filename, 'wb+') as f:
                        f.write(r.content)
                except Exception as E:
                    logger.error('RecorderHTTPGet:main Exception: %s', str(E))
            if self.stop_time and self.stop_time < date_time:
                break;
            time.sleep(THREAD_CHECK_TIMEOUT_SEC)


RECORDER_METHOD_MAP = {
    RecorderMethod.VLC: (RecorderVLC, 'video'),
    RecorderMethod.VLC_SNAP: (RecorderVLC, 'snapshot'),
    RecorderMethod.HTTP_GET: (RecorderHTTPGet, 'snapshot'),
}

class RecorderRef():
    def __init__(self, recorder):
        self.recorder = recorder
        self.update_time = None


class RecordingCamera():
    def __init__(self, camera):
        self.camera = camera
        self.id = camera.pk
        self.recorders = []

class RecorderManager():

    def __init__(self):
        self.recorders = {}
        self.worker_thread = threading.Thread(target = self.workerMain)
        self._event_done = threading.Event()

    def recordingCameras(self):
        recording_cameras = {}
        for k, r in self.recorders.items():
            item = recording_cameras.get(k[0])
            if not item:
                item = RecordingCamera(r.recorder.camera)
                recording_cameras[k[0]] = item
            item.recorders.append(r.recorder)
        return recording_cameras

    def workerMain(self):
        ScheduleIntervals = apps.get_model(app_label='inventory', model_name='ScheduleIntervals')
        while not self._event_done.isSet():
            time.sleep(THREAD_CHECK_TIMEOUT_SEC)
            try:
                date_time = timezone.localtime()
                schedules = {}
                for si in ScheduleIntervals.qsActiveIntervals(date_time):
                    next_switch = schedules.get(si.schedule)
                    next_switch2 = si.nextSwitchTime(date_time)
                    if next_switch is None or (next_switch[0] is not None and (next_switch[0] < next_switch2 or next_switch2 is None)):
                        schedules[si.schedule] = (next_switch2,)
                # update all active recorders
                for sh, nst in schedules.items():
                    for camera in sh.cameras.filter(state=CameraState.ENABLED):
                        for profile in [camera.recorder_profile, camera.recorder_profile2]:
                            reckey = (camera.pk, profile.pk)
                            recorderRef = self.recorders.get(reckey)
                            if recorderRef and not recorderRef.recorder.is_alive():
                                logger.warning('Recorder thread %d for camera "%s" is dead -> restart', recorderRef.recorder.ident, camera.name)
                                del self.recorders[reckey]
                                recorderRef = None
                            if not recorderRef:
                                recorder_class, subpath = RECORDER_METHOD_MAP[profile.method]
                                recorderRef = RecorderRef(recorder_class(camera, profile, nst[0], subpath))
                                logger.warning('Starting thread %d for camera "%s":"%s"', recorderRef.recorder.ident, camera.name, profile.name)
                                self.recorders[reckey] = recorderRef
                            recorderRef.update_time = date_time
                # remove obsoleted recorders
                for reckey, recorderRef in list([(k, r) for k, r in self.recorders.items() if r.update_time is None or r.update_time < date_time]):
                    del self.recorders[reckey]
                    logger.warning('Stoping thread %d for camera "%s"', recorderRef.recorder.ident, recorderRef.recorder.camera.name)
                    recorderRef.recorder.stop()
            except Exception as E:
                logger.error('workerMain: Unhandled exception: %s', traceback.format_exc())
                time.sleep(5)

        
        for recorderRef in list([r for k, r in self.recorders.items()]):
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

