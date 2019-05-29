#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from images_preprocessor.skeleton import fib

__author__ = "haouzij"
__copyright__ = "haouzij"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
