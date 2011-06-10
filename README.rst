Playa is a Python web service that streams music on whatever machine it's running under, as well as providing a web interface to manage what's playing.

**Playa is currently under development**

The current iteration, likely to change a lot:

.. image:: http://f.cl.ly/items/2s3E2I001Q3N0N29260s/by%20default%202011-06-09%20at%207.18.58%20PM.png

Install
=======

Installation is brutal, due to a couple of packages not being very nice. Please read the documentation on PyAudio and pymad for full installation instructions.

For now, we're going to assume you're on a UNIX based operating system.

1. Start by installing `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/>`_.

2. Continue on to `pymad <http://spacepants.org/src/pymad/>`_.

3. Install Playa::

    pip install https://github.com/disqus/playa/zipball/master

4. Start the service::

    playa start

5. Visit http://localhost:9000 in your browser.

Configuration
=============

Playa can be configured by either specifying ``--config=<filepath>`` or by creating a configuration file in ``~/playa/playa.conf.py``.

Example configuration::

    import os.path
    
    ROOT = os.path.normpath(os.path.dirname(__file__))

    DEBUG = True

    SQLITE3_DATABASE = os.path.join(ROOT, 'playa.db')

    AUDIO_PATHS = ['/usr/share/music/']

    WEB_HOST = '0.0.0.0'
    WEB_PORT = 9000
    WEB_LOG_FILE = os.path.join(ROOT, 'playa.log')
    WEB_PID_FILE = os.path.join(ROOT, 'playa.pid')

If you change configuration you'll need to ``playa restart``.

TODO
====

- Move indexes into SQLite database to avoid rebuilding continuously.
- Create IndexThread to monitor directories for changes.
- Refactor AudioPlayer public API to be part of AudioThread.
- Add dynamic playlists support via SQLite