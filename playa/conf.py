"""
playa.conf
~~~~~~~~~~

Represents the default values for all settings.

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import os
import os.path


class PlayaConfig(object):
    ROOT = os.path.normpath(os.path.dirname(__file__))

    DEBUG = True

    AUDIO_PATHS = []

    WEB_HOST = '0.0.0.0'
    WEB_PORT = 9000
    WEB_LOG_FILE = os.path.join(ROOT, 'playa.log')
    WEB_PID_FILE = os.path.join(ROOT, 'playa.pid')

    DATA_PATH = os.path.join(ROOT, 'data')

    SECRET_KEY = '_#(wkvb#@%%!x-dd!xt&i-1g5rylz4q&t6%m5u@3&7hyuqd437'

    DISQUS_PUBLIC = None
    DISQUS_SECRET = None
