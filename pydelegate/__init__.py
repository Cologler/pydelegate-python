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


class EventDescriptor:
    ''' the `event` descriptor use for instance event. '''

    def __get__(self, obj, objtype):
        return vars(obj).get(self, EMPTY)

    def __set__(self, obj, value):
        if not isinstance(value, Delegate):
            raise TypeError

        vars(obj)[self] = value


def event(*args, static=None):
    if static is True:
        return EMPTY

    if static is None and len(args) == 1:
        if isinstance(args[0], (classmethod, staticmethod)):
            return EMPTY

    return EventDescriptor()
