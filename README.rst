Playa is a Python web service that streams music on whatever machine it's running under, as well as providing a web interface to manage what's playing.

**Playa is currently under development**

The current iteration, likely to change a lot:

.. image:: http://f.cl.ly/items/1l2U2g1F1V173245453s/by%20default%202011-06-16%20at%208.32.15%20PM.png

Install
=======

For now, we're going to assume you're on a OS X, as it hasn't been tested elsewhere.

1. Start by installing `VLC Player <http://videolan.org/>`_ (specifically you need libvlc).

2. Install Playa::

    pip install https://github.com/disqus/playa/zipball/master

3. Start the service::

    playa start

4. Visit http://localhost:9000 in your browser.

Configuration
=============

Playa can be configured by either specifying ``--config=<filepath>`` or by creating a configuration file in ``~/playa/playa.conf.py``.

Example configuration::

    import os.path
    
    ROOT = os.path.normpath(os.path.dirname(__file__))

    DEBUG = True

    AUDIO_PATHS = ['/usr/share/music/']

    WEB_HOST = '0.0.0.0'
    WEB_PORT = 9000
    WEB_LOG_FILE = os.path.join(ROOT, 'playa.log')
    WEB_PID_FILE = os.path.join(ROOT, 'playa.pid')

    DATA_PATH = os.path.join(ROOT, 'data')


If you change configuration you'll need to ``playa restart``.

TODO
====

- Replace infinite directory looping behavior with inotify/MacFS event apis in AudioIndex
- Refactor AudioPlayer public API to be part of AudioThread.
- Add dynamic playlists support
- Add more controls (next/prev track proper, shuffle/repeat)
- Add autoplay/party shuffle type controls
- Add ajax polling to Now Playing interface