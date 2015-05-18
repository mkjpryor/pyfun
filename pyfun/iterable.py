"""
This module implements several type-classes for the built-in sequence types

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import collections, functools

from pyfun import monad


# Register generic iterable implementations
@monad.flatmap.register(collections.Iterable, object)
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


# Register list-specific implementations
monad.flatmap.register(list, object)(
    lambda xs, f: functools.reduce(lambda xs, x: xs + f(x), xs, [])
)
monad.unit.register(list)(lambda a: [a])
monad.empty.register(list)(list)
monad.append.register(list, list)(lambda xs, ys: xs + ys)


# Register tuple-specific implementations
monad.flatmap.register(tuple, object)(
    lambda xs, f: functools.reduce(lambda xs, x: xs + f(x), xs, ())
)
monad.unit.register(tuple)(lambda a: (a,))
monad.empty.register(tuple)(tuple)
monad.append.register(tuple, tuple)(lambda xs, ys: xs + ys)

