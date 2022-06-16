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

or you can add `Delegate` to `None`:

``` py
from pydelegate import Delegate

def func():
    return 1

d = None
d += Delegate(func)
assert d() == 1
```
