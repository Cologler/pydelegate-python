#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import unittest

from pytest import raises

from pydelegate import Delegate, event, InvokeEmptyDelegateError

def test_empty_delegate_invoke_raise_error():
    with raises(InvokeEmptyDelegateError):
        Delegate()()

def test_delegate_testable():
    assert not Delegate(), 'test empty delegate should be false'
    assert Delegate(lambda: None)
    assert Delegate(lambda: None, lambda: None)

def test_delegate_equals():
    assert Delegate() is not Delegate()
    assert Delegate() == Delegate()
    assert Delegate(lambda: None) != Delegate(lambda: None)
    fn = lambda: None
    assert Delegate(fn) == Delegate(fn)
    assert Delegate(fn) != Delegate(fn, fn)

def test_delegate_eq_items():
    def func1(): pass
    def func2(): pass
    def func3(): pass

    d1 = Delegate()
    d1 += func1
    d2 = Delegate()
    d2 += func1
    assert d1 == d2

    d1 += func2
    d2 += func2
    assert d1 == d2

    d1 += func3
    d2 += func3
    assert d1 == d2

    d1 += func1
    d2 += func2
    assert d1 != d2

def test_delegate_invoke_order():
    def func1(ls: list):
        ls.append(1)

    def func2(ls: list):
        ls.append(2)

    d = Delegate()
    d += func1
    d += func2
    dest = []
    d(dest)
    assert dest == [1, 2], 'should first in first run'

def test_delegate_invoke_return_value():
    def func1():
        return 1

    def func2():
        return 2

    d = Delegate()
    d += func1
    d += func2
    assert d() == 2, 'should be the last one'

def test_delegate_add_from_none():
    d = None
    d += Delegate()
    assert isinstance(d, Delegate)
    assert not d

    def func():
        return 1
    d += func
    assert d() == 1

def test_delegate_add_none():
    d = Delegate()
    with raises(TypeError):
        d += None

def test_delegate_remove_order():
    def func1(ls: list):
        ls.append(1)

    def func2(ls: list):
        ls.append(2)

    d = Delegate()
    d += func1
    d += func2
    d += func1
    d -= func1
    src = []
    d(src)
    assert src == [1, 2], 'should remove the last match'

def test_delegate_as_class_member():
    class A:
        d = Delegate()

    def func():
        return 1

    A = A()
    A.d += func
    assert A.d
    assert A.d() == 1, 'call without self argument'

def test_delegate_as_instance_member():
    class A:
        d = Delegate()

    def func():
        return 1

    a1 = A()
    a1.d += func
    assert not A.d
    assert a1.d
    assert a1.d() == 1, 'call with self argument'


def test_event_as_instance_member():
    class A:
        @event
        def d(self):
            pass

        e = event('e')

    def func1(self, ls: list):
        ls.append(1)

    def func2(self, ls: list):
        ls.append(2)

    a1 = A()
    assert not a1.d
    a1.d += func1
    a1.d += func2
    assert not A.d
    src = []
    a1.d(src)
    assert src == [1, 2]

    def func3(self, ls: list):
        ls.append(3)

    def func4(self, ls: list):
        ls.append(4)

    a2 = A()
    assert not a2.e
    a2.e += func3
    a2.e += func4
    assert not A.e
    src = []
    a2.e(src)
    assert src == [3, 4]

def test_event_as_class_member():
    class A:
        @event
        def d(self):
            pass

    assert A.d is None
    # should not use `A.d += ?`, this will overwrite the `event`
