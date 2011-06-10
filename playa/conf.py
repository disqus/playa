"""
Represents the default values for all Sentry settings.
"""

import logging
import os
import os.path

class PlayaConfig(object):
    ROOT = os.path.normpath(os.path.dirname(__file__))

    DEBUG = True

    SQLITE3_DATABASE = os.path.join(ROOT, 'playa.db')

    AUDIO_PATHS = []

    WEB_HOST = '0.0.0.0'
    WEB_PORT = 9000
    WEB_LOG_FILE = os.path.join(ROOT, 'playa.log')
    WEB_PID_FILE = os.path.join(ROOT, 'playa.pid')