#!/usr/bin/env python
import eventlet
import os
import os.path
import sys

from daemon.daemon import DaemonContext
from daemon.runner import DaemonRunner, make_pidlockfile
from eventlet import wsgi
from optparse import OptionParser

from playa import VERSION, app

class PlayaServer(DaemonRunner):
    pidfile_timeout = 10
    start_message = u"started with pid %(pid)d"

    def __init__(self, host=None, port=None, pidfile=None,
                 logfile=None, daemonize=False, debug=False):
        if not logfile:
            logfile = app.config['WEB_LOG_FILE']

        logfile = os.path.realpath(logfile)
        pidfile = os.path.realpath(pidfile or app.config['WEB_PID_FILE'])
        
        if daemonize:
            detach_process = True
        else:
            detach_process = False

        self.daemon_context = DaemonContext(detach_process=detach_process)
        self.daemon_context.stdout = open(logfile, 'w+')
        self.daemon_context.stderr = open(logfile, 'w+', buffering=0)

        self.pidfile = make_pidlockfile(pidfile, self.pidfile_timeout)

        self.daemon_context.pidfile = self.pidfile

        self.host = host or app.config['WEB_HOST']
        self.port = port or app.config['WEB_PORT']

        self.debug = debug

        # HACK: set app to self so self.app.run() works
        self.app = self

    def execute(self, action):
        self.action = action
        if self.daemon_context.detach_process is False and self.action == 'start':
            # HACK:
            self.run()
        else:
            self.do_action()

    def run(self):
        upgrade()

        # Pull in audio player
        from playa.ext.audio import AudioPlayer

        app.player = AudioPlayer(app)

        if self.debug:
            app.run(host=self.host, port=self.port, debug=self.debug)
        else:
            wsgi.server(eventlet.listen((self.host, self.port)), app)

def upgrade():
    pass

def main():
    command_list = ('start', 'stop', 'restart', 'upgrade')
    args = sys.argv
    if len(args) < 2 or args[1] not in command_list:
        print "usage: playa [command] [options]"
        print
        print "Available subcommands:"
        for cmd in command_list:
            print "  ", cmd
        sys.exit(1)

    parser = OptionParser(version="%%prog %s" % VERSION)
    parser.add_option('--config', metavar='CONFIG')
    if args[1] == 'start':
        parser.add_option('--debug', action='store_true', default=False, dest='debug')
        parser.add_option('--host', metavar='HOSTNAME')
        parser.add_option('--port', type=int, metavar='PORT')
        parser.add_option('--daemon', action='store_true', default=False, dest='daemonize')
        parser.add_option('--no-daemon', action='store_false', default=False, dest='daemonize')
        parser.add_option('--pidfile', dest='pidfile')
        parser.add_option('--logfile', dest='logfile')
    elif args[1] == 'stop':
        parser.add_option('--pidfile', dest='pidfile')
        parser.add_option('--logfile', dest='logfile')

    (options, args) = parser.parse_args()

    if options.config:
        # assumed to be a file
        app.config.from_file(options.config)
    else:
        config_path = os.path.expanduser(os.path.join('~', '.playa', 'playa.conf.py'))
        if os.path.exists(config_path):
            app.config.from_file(config_path)

    if args[0] == 'upgrade':
        upgrade()

    elif args[0] == 'start':
        web = PlayaServer(host=options.host, port=options.port,
                           pidfile=options.pidfile, logfile=options.logfile,
                           daemonize=options.daemonize, debug=options.debug)
        web.execute(args[0])

    elif args[0] == 'restart':
        web = PlayaServer()
        web.execute(args[0])
  
    elif args[0] == 'stop':
        web = PlayaServer(pidfile=options.pidfile, logfile=options.logfile)
        web.execute(args[0])

    sys.exit(0)

if __name__ == '__main__':
    main()