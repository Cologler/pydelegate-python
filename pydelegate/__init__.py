# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import Tuple


class InvokeEmptyDelegateError(Exception):
    'raised when invoke a empty delegate.'


class InvokeAggregateError(Exception):
    def __init__(self, errors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__errors = tuple(errors)

    @property
    def errors(self) -> Tuple[Exception, ...]:
        return self.__errors

    def __repr__(self):
        return f'InvokeAggregateError({self.errors!r})'


class Delegate:
    '''
    `Delegate` is immutable object.
    '''

    __slots__ = ('__funcs', '__raise_on_empty')

    def __init__(self, *funcs, raise_on_empty=True):
        self.__funcs = funcs
        self.__raise_on_empty = raise_on_empty

    def _init_args(self):
        'get the init args of this delegate.'
        return self.__funcs, {'raise_on_empty': self.__raise_on_empty}

    def __repr__(self):
        return f'Delegate{self.__funcs!r}'

    def __bool__(self):
        return len(self.__funcs) > 0

    def __radd__(self, other):
        # usage: other += Delegate()

        if other is None:
            return self

        s_funcs = self.__funcs
        s_kwargs = self._init_args()[1]

        if type(other) is Delegate and other._init_args()[1] == self._init_args()[1]:
            o_funcs = other.__funcs
        elif callable(other):
            o_funcs = (other, )
        else:
            raise TypeError('other must be callable')

        if not o_funcs:
            return self

        return Delegate(*s_funcs, *o_funcs, **s_kwargs)

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

    def __hash__(self):
        if not self.__funcs:
            return hash(None)
        return hash((Delegate, self.__funcs, self.__raise_on_empty))

    def __eq__(self, other):
        if isinstance(other, Delegate):
            return self._init_args() == other._init_args()

        elif len(self.__funcs) == 1:
            return self.__funcs[0] == other

        elif len(self.__funcs) == 0:
            return other is None

        else:
            return False

    def __contains__(self, item):
        return item in self.__funcs

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        if not self:
            if self.__raise_on_empty:
                raise InvokeEmptyDelegateError(f'{self!r} is empty')
            return None

        ret = None
        errors = []
        for func in self.__funcs:
            try:
                ret = self._call_func(func, args, kwargs)
            except Exception as e:
                errors.append(e)

        if errors:
            raise InvokeAggregateError(errors)

        return ret

    def _call_func(self, func, args, kwargs):
        return func(*args, **kwargs)

# alias
delegate = Delegate

__all__ = [
    # public api
    'Delegate',

    # errors
    'InvokeEmptyDelegateError', 'InvokeAggregateError',

    # alias
    'delegate',
]
