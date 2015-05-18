"""
This module implements several type-classes for the built-in tuple type

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools

from pyfun import monad


@monad.flatmap.register(tuple, object)
def flatmap(xs, f):
    return functools.reduce(lambda xs, x: xs + f(x), xs, ())

@monad.unit.register(tuple)
def unit(a):
    return (a,)

@monad.empty.register(tuple)
def empty():
    return ()

@monad.append.register(tuple, tuple)
def append(xs, ys):
    return xs + ys
