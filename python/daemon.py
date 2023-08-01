#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import atexit
import time
import signal


class Daemon:
    # signal handler for termination (required)
    @staticmethod
    def __signal_handler(signum, frame):
        print("Daemon::__signal_handler: signum = {} \n".format(signum))

        if signal.SIGTERM == signum:
            raise SystemExit(1)

    def __init__(self,
                 pidfile='/tmp/daemon.pid',
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null'):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def daemonize(self):
        if os.path.exists(self.pidfile):
            raise RuntimeError('Already running!')

        # first fork (detaches from parent)
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError(
                'fork #1 faild: {0} ({1}) \n'.format(e.errno, e.strerror))

        os.chdir('/')
        os.setsid()
        os.umask(0o22)
        # os.umask(0)

        # second fork (relinquish session leadership)
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError(
                'fork #2 faild: {0} ({1}) \n'.format(e.errno, e.strerror))

        # flush I/O buffers
        sys.stdout.flush()
        sys.stderr.flush()

        # replace file descriptors for stdin, stdout, and stderr
        with open(self.stdin, 'rb', 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(self.stdout, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(self.stderr, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        # write the PID file
        with open(self.pidfile, 'w') as f:
            f.write(str(os.getpid()))

        # arrange to have the PID file removed on exit/signal
        atexit.register(lambda: os.remove(self.pidfile))
        # atexit.register(os.remove, pid_file)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def start(self):
        try:
            self.daemonize()
        except RuntimeError as e:
            print(e)
            raise SystemExit(1)

        self.run()

    def stop(self):
        try:
            if os.path.exists(self.pidfile):
                with open(self.pidfile) as f:
                    os.kill(int(f.read()), signal.SIGTERM)
            else:
                print('Not running!')
                raise SystemExit(1)
        except OSError as e:
            if 'No such process' in str(e) and os.path.exists(self.pidfile):
                os.remove(self.pidfile)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        pass


class MyDaemon(Daemon):
    def __init__(self,
                 pidfile='/tmp/mydaemon.pid',
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null'):
        super().__init__(pidfile, stdin, stdout, stderr)

    def run(self):
        print('MyDaemon started with pid {} \n'.format(os.getpid()))

        while True:
            print('MyDaemon Alive! {} \n'.format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            # TODO: do something
            time.sleep(5)


if "__main__" == __name__:
    PIDFILE = '/tmp/mydaemon.pid'
    LOG = '/tmp/mydaemon.log'

    daemon = MyDaemon(pidfile=PIDFILE, stdout=LOG, stderr=LOG)

    if len(sys.argv) != 2:
        print('Usage: {} [start|stop|restart]'.format(sys.argv[0]))
        raise SystemExit(1)

    if 'start' == sys.argv[1]:
        daemon.start()
    elif 'stop' == sys.argv[1]:
        daemon.stop()
    elif 'restart' == sys.argv[1]:
        daemon.restart()
    else:
        print('Unknown command {!r}'.format(sys.argv[1]))
        raise SystemExit(1)
