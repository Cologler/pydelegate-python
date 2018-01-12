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

from pydelegate import event, static_event

class Test(unittest.TestCase):
    def test_(self):
        def callback_1(s):
            return s + 1

        def callback_2(s):
            return s + 2

        class A:
            e0 = event()

            @event
            def e1(self):
                pass

            @static_event
            def e2(self):
                pass


        a = A()
        a.e0 += callback_1
        a.e1 += callback_1
        A.e2 += callback_1
        A.e2 += callback_2
        self.assertEqual(a.e0(0), 1)
        self.assertEqual(a.e1(0), 1)
        self.assertEqual(a.e2(0), 2)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        unittest.main()
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()
