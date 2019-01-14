from django.apps import AppConfig
from .recorder import GetRecorder

class RecorderConfig(AppConfig):
    name = 'dashboard.recorder'
    recorder = None

    def ready(self):
        self.recorder = GetRecorder()
        self.recorder.startWorkerThread()
