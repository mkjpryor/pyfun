"""
This module implements several type-classes for the built-in list type

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools

from pyfun import monad


@monad.flatmap.register(list)
def flatmap(xs, f):
    return functools.reduce(lambda xs, x: xs + f(x), xs, [])

@monad.unit.register(list)
def unit(a):
    return [a]

@monad.empty.register(list)
def empty():
    return []

@monad.append.register(list, list)
def append(xs, ys):
    return xs + ys
