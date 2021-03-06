# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import List

class MultiInvokeError(Exception):
    def __init__(self, errors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._errors = tuple(errors)

    @property
    def errors(self) -> List[Exception]:
        return self._errors


class Delegate:
    '''
    `Delegate` is immutable object.
    '''

    __slots__ = ('_funcs')

    def __init__(self):
        self._funcs = ()

    def __repr__(self):
        return f'Delegate{self._funcs!r}'

    def __bool__(self):
        return len(self._funcs) > 0

    def __radd__(self, other):
        # usage: other += Delegate()
        s_funcs = self._funcs

        if isinstance(other, Delegate):
            if not s_funcs:
                return other
            o_funcs = other._funcs
        elif callable(other):
            o_funcs = (other, )
        elif other is None:
            # None + Delegate() -> Delegate()
            o_funcs = ()
        else:
            raise ValueError('other must be callable')

        if o_funcs:
            rv = Delegate()
            rv._funcs = s_funcs + o_funcs
            return rv
        else:
            return self

    def __add__(self, other):
        # usage: Delegate() += other
        # so other cannot be `None`

        if other is None:
            raise TypeError('other cannot be None')

        return self.__radd__(other)

    def __sub__(self, other):
        if other is self:
            if self._funcs:
                return Delegate()
            else:
                return self

        elif other is None:
            raise TypeError('other cannot be None')

        funcs = list(self._funcs)
        funcs.reverse()

        if isinstance(other, Delegate):
            if not other:
                return self

            for func in other._funcs:
                try:
                    funcs.remove(func)
                except ValueError:
                    raise ValueError(f'{func!r} is not in {self!r}')

        else:
            try:
                funcs.remove(other)
            except ValueError:
                raise ValueError(f'{other!r} is not in {self!r}')

        funcs.reverse()

        # funcs must changed.
        if funcs:
            rv = Delegate()
            rv._funcs = tuple(funcs)
            return rv
        else:
            return Delegate()

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def __hash__(self):
        return hash(Delegate) ^ hash(self._funcs)

    def __eq__(self, other):
        if isinstance(other, Delegate):
            return self._funcs == other._funcs

        elif len(self._funcs) == 1:
            return self._funcs[0] == other

        elif len(self._funcs) == 0:
            return other is None

        else:
            return False

    def __contains__(self, item):
        return item in self._funcs

    def invoke(self, *args, **kwargs):
        if not self:
            raise RuntimeError(f'{self!r} is empty')

        ret = None
        errors = []
        for func in self._funcs:
            try:
                ret = self._call_func(func, args, kwargs)
            except Exception as e:
                errors.append(e)

        if errors:
            raise MultiInvokeError(errors)

        return ret

    def _call_func(self, func, args, kwargs):
        return func(*args, **kwargs)

    def _bound(self, target):
        d = _BoundedDelegate(target)
        d._funcs = self._funcs
        return d


class _BoundedDelegate(Delegate):
    __slots__ = ('_target')

    def __init__(self, target):
        super().__init__()
        self._target = None

    def _call_func(self, func, args, kwargs):
        return func(self._target, *args, **kwargs)

    def __hash__(self):
        return hash(_BoundedDelegate) ^ hash(self._funcs) ^ hash(id(self._target))

    def __eq__(self, other):
        if isinstance(other, _BoundedDelegate):
            return self._target is other._target and self._funcs == other._funcs

        elif len(self._funcs) == 0:
            return other is None

        else:
            return False



class event:
    '''
    a data descriptor use for class.

    so when you want to get `Delegate` from the attr, we can bound the Delegate with `self` argument.
    '''

    def __init__(self, func_or_name):
        self._name = str(getattr(func_or_name, '__name__', func_or_name))

    def __get__(self, obj, cls):
        if obj is not None:
            d = vars(obj).get(self._name, Delegate())
            if d:
                return d._bound(obj)
            else:
                return d
        else:
            return None

    def __set__(self, obj, value):
        if not isinstance(value, Delegate):
            raise TypeError(f'{value!r} is not a Delegate')

        d = vars(obj)
        d[self._name] = value


def event_handler(func):
    '''
    decorate a function to a Delegate.

    usage:

    ``` py
    @event_handler
    def func(): 1

    a = None
    a += func
    assert a == 1
    ```
    '''
    return Delegate() + func
