#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""python-模块"""

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
