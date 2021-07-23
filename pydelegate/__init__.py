# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import Tuple


class InvokeEmptyDelegateError(RuntimeError):
    'raised when invoke a empty delegate.'


class MultiInvokeError(Exception):
    def __init__(self, errors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._errors = tuple(errors)

    @property
    def errors(self) -> Tuple[Exception, ...]:
        return self._errors

    def __repr__(self):
        return f'MultiInvokeError({self.errors!r})'


class Delegate:
    '''
    `Delegate` is immutable object.
    '''

    __slots__ = ('__funcs', )

    def __init__(self, *funcs):
        self.__funcs = funcs

    def __repr__(self):
        return f'Delegate{self.__funcs!r}'

    def __bool__(self):
        return len(self.__funcs) > 0

    def __radd__(self, other):
        # usage: other += Delegate()
        s_funcs = self.__funcs

        if isinstance(other, Delegate):
            if not s_funcs:
                return other
            o_funcs = other.__funcs
        elif callable(other):
            o_funcs = (other, )
        elif other is None:
            # None + Delegate() -> Delegate()
            o_funcs = ()
        else:
            raise TypeError('other must be callable')

        if o_funcs:
            return Delegate(*s_funcs, *o_funcs)
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
            if self.__funcs:
                return Delegate()
            else:
                return self

        elif other is None:
            raise TypeError('other cannot be None')

        funcs = list(self.__funcs)
        funcs.reverse()

        if isinstance(other, Delegate):
            if not other:
                return self

            for func in other.__funcs:
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
            rv = Delegate(*funcs)
            return rv
        else:
            return Delegate()

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def __hash__(self):
        return hash(Delegate) ^ hash(self.__funcs)

    def __eq__(self, other):
        if isinstance(other, Delegate):
            return self.__funcs == other.__funcs

        elif len(self.__funcs) == 1:
            return self.__funcs[0] == other

        elif len(self.__funcs) == 0:
            return other is None

        else:
            return False

    def __contains__(self, item):
        return item in self.__funcs

    def invoke(self, *args, **kwargs):
        if not self:
            raise InvokeEmptyDelegateError(f'{self!r} is empty')

        ret = None
        errors = []
        for func in self.__funcs:
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
        d = _BoundedDelegate(target, *self.__funcs)
        return d


class _BoundedDelegate(Delegate):
    __slots__ = ('__target', )

    def __init__(self, target, *funcs):
        super().__init__(*funcs)
        self.__target = target

    def _call_func(self, func, args, kwargs):
        return func(self.__target, *args, **kwargs)

    def __hash__(self):
        return hash(_BoundedDelegate) ^ hash(self.__funcs) ^ hash(id(self.__target))

    def __eq__(self, other):
        if isinstance(other, _BoundedDelegate):
            return self.__target is other.__target and self.__funcs == other.__funcs

        elif len(self.__funcs) == 0:
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

# alias
delegate = Delegate

# deprecated, but kept compatible
event_handler = Delegate

__all__ = [
    # public api
    'Delegate', 'event',

    # errors
    'InvokeEmptyDelegateError',

    # alias
    'delegate', 'event_handler',
]
