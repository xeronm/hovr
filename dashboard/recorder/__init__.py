default_app_config = 'dashboard.recorder.apps.RecorderConfig'

import os  
import signal  
import sys  

from .recorder import GetRecorder

def signal_handler(*args):  
    GetRecorder().stopWorkerThread()
    sys.exit(0) 

signal.signal(signal.SIGINT, signal_handler) 