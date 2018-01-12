#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import sys
import traceback
import unittest

from pydelegate import event, InvokeError

def callback_add_one(val):
    return val + 1

def callback_add_two(val):
    return val + 2

class Test(unittest.TestCase):
    def test_modes(self):
        class A:
            e0 = event()

            @event
            def e1(self):
                pass

            @event
            @staticmethod
            def e2(self):
                pass

            @event
            @classmethod
            def e3(cls):
                pass

        a = A()
        a.e0 += callback_add_one
        a.e1 += callback_add_one
        A.e2 += callback_add_one
        A.e3 += callback_add_one
        self.assertEqual(a.e0(0), 1)
        self.assertEqual(a.e1(0), 1)
        self.assertEqual(A.e2(0), 1)
        self.assertEqual(A.e3(0), 1)

    def test_result_should_be_tail(self):
        class A:
            e0 = event()

        a = A()
        a.e0 += callback_add_one
        a.e0 += callback_add_two
        self.assertEqual(a.e0(0), 2)

    def test_remove_node(self):
        class A:
            e0 = event()

            def f(self):
                pass

            def o(self):
                pass

        a = A()
        self.assertIsNot(a.f, a.f)
        a.e0 += a.f
        self.assertEqual(len(a.e0.get_invocation_list()), 1)
        a.e0 -= a.o
        self.assertEqual(len(a.e0.get_invocation_list()), 1)
        a.e0 -= a.f
        self.assertEqual(len(a.e0.get_invocation_list()), 0)

    def test_empty_invoke(self):
        class A:
            e0 = event()

        a = A()
        with self.assertRaises(InvokeError):
            a.e0()


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        unittest.main()
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()
