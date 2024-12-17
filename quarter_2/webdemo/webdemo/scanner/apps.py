from django.apps import AppConfig
import os
import jpype
import jpype.imports
from jpype.types import *

class ScannerConfig(AppConfig):
    name = 'webdemo.scanner'

    def ready(self):
        path = os.path.dirname(os.path.abspath(__file__))
        jpype.startJVM(
            classpath=[
                os.path.join(path, 'core-3.5.3.jar'),
                os.path.join(path, 'javase-3.5.3.jar')
        ])
