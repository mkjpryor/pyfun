"""
This module turns the built-in list type into a monad-plus

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from functools import reduce

from pyfun import monad


# Register the built-in list as a MonadPlus
monad.MonadPlus.register(list)

# Provide the required implementations
@monad.bind.register(list)
def bind(xs, f):
    return reduce(lambda xs, x: xs + f(x), xs, [])

@monad.unit.register(list)
def unit(a):
    return [a]

@monad.empty.register(list)
def empty():
    return []

@monad.append.register(list)
def append(xs, ys):
    return xs.extend(ys)
