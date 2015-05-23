"""
This module implements several type-classes for iterables

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from collections import Iterable, Callable

from .monad import flatmap, unit, binop, empty


# Monad-plus implementation for generic iterables

@flatmap.register
def _flatmap(xs: Iterable, f: Callable) -> Iterable:
    for x in xs:
        yield from f(x)

@unit.register(Iterable)
def _unit(a) -> Iterable:
    yield a

@binop.register
def _binop(xs: Iterable, ys: Iterable) -> Iterable:
    yield from xs
    yield from ys
    
@empty.register(Iterable)
def _empty() -> Iterable:
    yield from ()
