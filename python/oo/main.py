#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Python-Object-oriented"""

print("\n############################## %s ##################################\n" %(__doc__))

class Base:
    "Base class"

    def __init__(self, attr):
        print("%s.__init__: attr = %d" %(Base.__name__, attr))
        self.attr = attr
       
    def __del__(self):
        print("%s.__del__" %(Base.__name__))

    def __str__(self):
        return("%s [attr = %d]" %(Base.__name__, self.attr))

    def __eq__(self, obj):
        return self.attr == obj.attr

    def __gt__(self, obj):
        if self.attr > obj.attr:
            return True
        else:
            return False
        
    def __add__(self, obj):
        return Base(self.attr + obj.attr)

    def func(self):
        print("%s.func" %(Base.__name__))

    def set_attr(self, attr):
        self.attr = attr

    def get_attr(self):
        return self.attr

class Derive(Base):
    "Derive class"

    def __init__(self, attr):
        #super(Derive, self).__init__(attr)
        Base.__init__(self, attr)
        print("%s.__init__: attr = %d" %(Derive.__name__, self.attr))

    def __del__(self):
        print("%s.__del__" %(Derive.__name__))
        Base.__del__(self)
        
    def __add__(self, obj):
        return Derive(self.attr + obj.attr) 

    def func(self):
        print("%s.func" %(Derive.__name__))

print("Derive.__doc__:", Derive.__doc__)
print("Derive.__name__:", Derive.__name__)
print("Derive.__module__:", Derive.__module__)
print("Derive.__bases__:", Derive.__bases__)
print("Derive.__dict__:", Derive.__dict__)

print()

b1 = Derive(200)
b2 = Derive(100)

print()

b1.func()
b2.func()

print()

print(b1)
print(b2)

print()

print("repr(b1):", repr(b1))
print("repr(b2):", repr(b2))
print("b1 == b2:", (b1 == b2))
print("b1 > b2:", (b1 > b2))
print("b1 + b2:", (b1 + b2))

print()

print("isinstance(b1, Base):", isinstance(b1, Base))
print("isinstance(b1, Derive):", isinstance(b1, Derive))
print("issubclass(Derive, Base):", issubclass(Derive, Base))

print()

del b1
del b2
