#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Python-Module"""

print("\n############################## %s ##################################\n" %(__doc__))

from runoob import runoob1
from runoob import runoob2

runoob1.run1()
runoob2.run2()

print()

print("__doc__:", __doc__)
print("__file__:", __file__)
print("__name__:", __name__)
print("__package__:", __package__)

print()

print("dir():", dir())
print("globals():", globals())
print("locals():", locals())

print()

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

print()

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