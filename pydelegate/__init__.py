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

    def __get_opts(self):
        'get the init options of this delegate, use to compare.'
        return self.__raise_on_empty

    def __repr__(self):
        return f'Delegate{self.__funcs!r}'

    def __bool__(self):
        return len(self.__funcs) > 0

    @staticmethod
    def combine(first: 'Delegate', second):
        assert isinstance(first, Delegate)

        if type(second) is Delegate and second.__get_opts() == first.__get_opts():
            s_funcs = second.__funcs
        elif callable(second):
            s_funcs = (second, )
        else:
            raise TypeError('{other!r} is not callable')

        if not s_funcs:
            return first

        return first._with_funcs(*first.__funcs, *s_funcs)

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

    def __get_cmpval(self):
        return (Delegate, self.__funcs, self.__get_opts())

    def __hash__(self):
        return hash(self.__get_cmpval())

    def __eq__(self, other):
        return type(other) is Delegate and self.__get_cmpval() == other.__get_cmpval()

    def __contains__(self, item):
        return item in self.__funcs

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        '''
        invoke this delegate.
        '''

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

    @property
    def funcs_list(self):
        '''
        get the list of funcs.
        '''
        return self.__funcs


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
