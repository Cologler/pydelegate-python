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
    __slots__ = ('_funcs')

    def __init__(self, *funcs):
        self._funcs = funcs

    def __bool__(self):
        return len(self._funcs) > 0

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        if not self:
            raise RuntimeError('Cannot invoke empty delegate.')

        rets = tuple(f(*args, **kwargs) for f in self._funcs)
        return rets[-1]

    def __eq__(self, other):
        if not isinstance(other, Delegate):
            return False
        return self._funcs == other._funcs

    def __add__(self, other):
        funcs = self._funcs

        if isinstance(other, Delegate):
            funcs += other._funcs
        elif callable(other):
            funcs += (other, )
        else:
            raise ValueError

        return Delegate(*funcs) if funcs else EMPTY

    def __sub__(self, other):
        if other is self:
            return EMPTY

        funcs = list(self._funcs)

        if isinstance(other, Delegate):
            for func in other._funcs:
                try:
                    funcs.remove(func)
                except ValueError:
                    pass
        elif callable(other):
            try:
                funcs.remove(other)
            except ValueError:
                pass
        else:
            raise ValueError

        if len(funcs) == len(self._funcs):
            return self
        if len(funcs) == 0:
            return EMPTY
        return Delegate(*funcs)

    def get_invocation_list(self):
        return self._funcs

EMPTY = Delegate() # the cached empty delegate
