# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import Tuple, final


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


@final
class Delegate:
    '''
    `Delegate` is immutable object.
    '''

    __slots__ = ('__funcs', '__raise_on_empty')

    def __init__(self, *funcs, raise_on_empty=True):
        self.__funcs = funcs
        self.__raise_on_empty = raise_on_empty

    def _with_funcs(self, *funcs):
        return Delegate(*funcs, raise_on_empty=self.__raise_on_empty)

    def _init_args(self):
        'get the init args of this delegate.'
        return self.__funcs, {'raise_on_empty': self.__raise_on_empty}

    def __repr__(self):
        return f'Delegate{self.__funcs!r}'

    def __bool__(self):
        return len(self.__funcs) > 0

    @staticmethod
    def combine(first: 'Delegate', second):
        assert isinstance(first, Delegate)

        f_funcs = first.__funcs
        s_kwargs = first._init_args()[1]

        if type(second) is Delegate and second._init_args()[1] == first._init_args()[1]:
            s_funcs = second.__funcs
        elif callable(second):
            s_funcs = (second, )
        else:
            raise TypeError('{other!r} is not callable')

        if not s_funcs:
            return first

        return first._with_funcs(*f_funcs, *s_funcs)

    def __radd__(self, other):
        # usage: other += Delegate()
        if other is None:
            # allow None += Delegate()
            return self
        return self.combine(other, self)

    def __add__(self, other):
        # usage: Delegate() += other
        return self.combine(self, other)

    def __sub__(self, other):
        if other is None:
            raise TypeError('other cannot be None')

        if other is self:
            return self._with_funcs(())

        if isinstance(other, Delegate):
            to_remove = other.__funcs
        else:
            to_remove = (other, )

        funcs = list(self.__funcs)
        funcs.reverse()
        for func in to_remove:
            try:
                funcs.remove(func)
            except ValueError:
                raise ValueError(f'{func!r} is not in {self!r}')
        funcs.reverse()

        return self._with_funcs(*funcs)

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
                ret = func(*args, **kwargs)
            except Exception as e:
                errors.append(e)

        if errors:
            raise InvokeAggregateError(errors)

        return ret

        

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
