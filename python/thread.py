"""Python-Thread"""

print("\n############################## %s ##################################\n" %(__doc__))

import signal
import threading
import queue
import time
import random


def sig_handler(signum, frame):
    global exit
    exit = True


class RecvThread(threading.Thread):
    def __init__(self, id, name):
        threading.Thread.__init__(self)
        print("RecvThread.__init__: id = %d, name = %s" %(id, name))

        self.id = id
        self.name = name
    
    def run(self):
        print("RecvThread.run: running")

        while not exit:
            lock.acquire()

            if not queue.empty():
                data = queue.get()
                print("RecvThread.run: get %s" %(data))
            
            lock.release()
            time.sleep(1)

        print("RecvThread.run: exit")


class SendThread(threading.Thread):
    def __init__(self, id, name):
        threading.Thread.__init__(self)

        print("SendThread.__init__: id = %d, name = %s" %(id, name))
        self.id = id
        self.name = name

    def run(self):
        print("SendThread.run: running")

        while not exit:
            lock.acquire()

            if not queue.full():
                data = random.randrange(1, 100, 1)
                queue.put(data)
                print("SendThread.run: put %s" %(data))
            
            lock.release()
            time.sleep(1)

        print("SendThread.run: exit")


signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGHUP, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

exit = False
lock = threading.Lock()
queue = queue.Queue(100)

rthread = RecvThread(1, "Receive Thread")
rthread.start()
sthread = SendThread(2, "Send Thread")
sthread.start()

while True:
    try:
        if exit:
            rthread.join()
            sthread.join()
            break
    except Exception as e:
        print(e)
        break

print("Main thread exit")


# function decorator
def args_wrapper(pre = ""):
    def wrapper(f):
        def inner(*args, **kwargs):
            print("inner:", pre, args, kwargs)
            return f(*args, **kwargs)
        return inner
    return wrapper


@args_wrapper("test")
def test(x, y):
    print("test:", x, y)
    return x + y


print("test() return", test(100, 200))


# class decorator
class Wrapper(object):
    def __init__(self, f):
        print("%s.__init__:" %(Wrapper.__name__), f.__name__)
        self.__f = f

    def __call__(self, *args, **kwargs):
        print("%s.__call__:" %(Wrapper.__name__), self.__f.__name__, args, kwargs)
        return self.__f(*args, **kwargs)


@Wrapper
def call(x, y):
    print("call:", x, y)
    return x + y


print("call() return", call(100, 200))
