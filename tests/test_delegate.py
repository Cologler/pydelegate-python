#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import unittest

from pytest import raises

from pydelegate import Delegate, InvokeEmptyDelegateError

def test_delegate_raise_on_empty():
    with raises(InvokeEmptyDelegateError):
        Delegate()()

def test_delegate_raise_on_empty_is_false():
    assert None is Delegate(raise_on_empty=False)()

def test_delegate_testable():
    assert not Delegate(), 'test empty delegate should be false'
    assert Delegate(lambda: None)
    assert Delegate(lambda: None, lambda: None)

def test_delegate_equals_delegate():
    assert Delegate() is not Delegate()
    assert Delegate() == Delegate()
    assert Delegate(raise_on_empty=True)    != Delegate(raise_on_empty=False)
    assert Delegate(raise_on_empty=True)    == Delegate(raise_on_empty=True)
    assert Delegate(raise_on_empty=False)   == Delegate(raise_on_empty=False)

    assert Delegate(lambda: None) != Delegate(lambda: None)

    fn = lambda: None
    assert Delegate(fn) == Delegate(fn)
    assert Delegate(fn, raise_on_empty=True) != Delegate(fn, raise_on_empty=False)
    assert Delegate(fn) != Delegate(fn, fn)

def test_delegate_equals():
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

def test_delegate_invoke_order_by_added():
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

def test_delegate_invoke_return_last_value():
    def func1():
        return 1

    def func2():
        return 2

    d = Delegate()
    d += func1
    d += func2
    assert d() == 2, 'should be the last one'

def test_delegate_add_from_none():
    assert isinstance(None + Delegate(), Delegate)
    assert not (None + Delegate())

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

def test_delegate_as_class_member_with_class():
    class A:
        d = Delegate()

    def func():
        return 1

    assert not A.d
    A.d += func
    assert A.d
    assert A.d() == 1

def test_delegate_as_class_member_with_instance():
    class A:
        d = Delegate()

    def func():
        return 1

    a1 = A()
    assert not a1.d
    a1.d += func
    assert a1.d
    assert a1.d() == 1