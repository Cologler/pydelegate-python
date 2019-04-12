#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import unittest

from pytest import raises

from pydelegate import Delegate

def test_delegate_init():
    assert not Delegate(), 'delegate should be empty'

def test_delegate_equals():
    assert Delegate() == Delegate(), 'empty should equals'

    def func():
        pass

    d1 = Delegate()
    d1 += func
    d2 = Delegate()
    d2 += func
    assert d1 == d2, 'delegates should equals if they has same callback'

def test_delegate_invoke_empty():
    with raises(RuntimeError):
        Delegate()()

def test_delegate_should_call_one_by_one():
    def func1(ls: list):
        ls.append(1)

    def func2(ls: list):
        ls.append(2)

    d = Delegate()
    d += func1
    d += func2
    src = []
    d(src)
    assert src == [1, 2], 'delegate should call one by one'

def test_delegate_retval():
    def func():
        return 1

    d = Delegate()
    d += func
    assert d() == 1, 'delegate should has return value'

def test_delegate_retval_should_be_the_last():
    def func1():
        return 1

    def func2():
        return 2

    d = Delegate()
    d += func1
    d += func2
    assert d() == 2, 'delegate return value should be the last callback'
