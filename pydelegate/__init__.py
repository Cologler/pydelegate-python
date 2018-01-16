#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from collections import deque
from typing import List

class InvokeError(Exception):
    pass

class Delegate:
    def __init__(self, *delegates):
        self._delegates = delegates

    def __bool__(self):
        return len(self._delegates) > 0

    def __call__(self, *args, **kwargs):
        if not self:
            # case has return value, so cannot be empty.
            # same with csharp.
            raise InvokeError('Cannot invoke empty delegate.')

        for delegate in self._delegates:
            ret = delegate(*args, **kwargs)
        return ret

    def __eq__(self, other):
        if not isinstance(other, Delegate):
            return False
        if len(self._delegates) != len(other._delegates):
            return False
        return all(l == r for l, r in zip(self._delegates, other._delegates))

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
        if other is self:
            return EMPTY

        if isinstance(other, Delegate):
            delegates = list(self._delegates)
            for delegate in other._delegates:
                if delegate in delegates:
                    delegates.remove(delegate)
            if len(delegates) == len(self._delegates):
                return self
        elif callable(other):
            if other not in self._delegates:
                return self
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
    '''
    if `static` is `None` and do not decorate on `classmethod` or `staticmethod`, return instance event.
    '''
    if static is True:
        return EMPTY

    if static is None and len(args) == 1:
        if isinstance(args[0], (classmethod, staticmethod)):
            return EMPTY

    return EventDescriptor()
