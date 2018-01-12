#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from collections import deque
from typing import List

class Delegate:
    def __init__(self, *delegates):
        self._delegates = delegates

    def __bool__(self):
        return len(self._delegates) > 0

    def __call__(self, *args, **kwargs):
        ret = None
        for node in self._delegates:
            ret = node(*args, **kwargs)
        return ret

    def __add__(self, other):
        if isinstance(other, Delegate):
            if len(self._delegates) + len(other._delegates) == 0:
                return EMPTY
            return Delegate(*self._delegates, *other._delegates)
        elif callable(other):
            return Delegate(*self._delegates, other)
        else:
            raise ValueError

    def __sub__(self, other):
        if isinstance(other, Delegate):
            delegates = list(self._delegates)
            for delegate in other._delegates:
                delegates.remove(delegate)
        elif callable(other):
            delegates = list(self._delegates)
            delegates.remove(other)
        else:
            raise ValueError

        if delegates:
            return Delegate(*delegates)
        else:
            return EMPTY

    def get_invocation_list(self):
        return self._delegates


EMPTY = Delegate()


def static_event(*args):

    return EMPTY


def event(*args):

    prop = None

    def getter(self):
        return vars(self).get(prop, EMPTY)

    def setter(self, value):
        if not isinstance(value, Delegate):
            raise TypeError
        if value is EMPTY:
            del vars(self)[prop]
        else:
            vars(self)[prop] = value

    prop = property(fget=getter, fset=setter)
    return prop
