"""
This module provides the functor type and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc

from pyfun.decorators import singledispatch, auto_bind, infix


class Functor(metaclass = abc.ABCMeta):
    """
    The functor type
    """
    pass


@infix
@auto_bind
@singledispatch(1)
def fmap(f, Fa):
    """
    Signature:  Functor F => fmap :: (a -> b) -> F a -> F b
    """
    raise TypeError('Unable to locate implementation for %s' % repr(Fa.__class__))
