"""
This module implements several type-classes for the built-in sequence types

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import collections

from pyfun import monad

# Automatically import the list and tuple implementations
import pyfun.iterable.list
import pyfun.iterable.tuple


# Register all iterables as being monad-plus
monad.MonadPlus.register(collections.Iterable)

# Register generic iterable implementations
@monad.flatmap.register(collections.Iterable)
def flatmap(xs, f):
    for x in xs:
        yield from f(x)

@monad.unit.register(collections.Iterable)
def unit(a):
    yield a

@monad.empty.register(collections.Iterable)
def empty():
    yield from ()

@monad.append.register(collections.Iterable, collections.Iterable)
def append(xs, ys):
    yield from xs
    yield from ys
