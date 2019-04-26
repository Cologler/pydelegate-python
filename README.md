# pydelegate

![GitHub](https://img.shields.io/github/license/Cologler/pydelegate-python.svg)
[![Build Status](https://travis-ci.com/Cologler/pydelegate-python.svg?branch=master)](https://travis-ci.com/Cologler/pydelegate-python)
[![PyPI](https://img.shields.io/pypi/v/pydelegate.svg)](https://pypi.org/project/pydelegate/)

a python version delegate like C#.

## Usage

``` py
from pydelegate import Delegate

def func():
    return 1

d = Delegate()
d += func
assert d() == 1
```

or you can set init `Delegate` lazy:

``` py
from pydelegate import event_handler

def func():
    return 1

d = None
d += event_handler(func) # event_handler() return a `Delegate`
assert d() == 1
```

or if you want inject `self` var in your instance method, use `event` data descriptor:

``` py
from pydelegate import event

class A:
    @event
    def d(self):
        pass
    # or
    e = event('e')

def func(self):
    return 1

a = A()
a.d += func
assert a.d() == 1
```

read unittests for more usages.
