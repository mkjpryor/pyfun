"""
This module provides the applicative and alternative types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from pyfun.decorators import singledispatch, generic, auto_bind, infix, multipledispatch
from pyfun import functor


class Applicative(functor.Functor):
    """
    The applicative type
    """
    pass


@infix
@auto_bind
@multipledispatch
def ap(Ff, Fa):
    """
    Signature:  Applicative F => ap :: F (a -> b) -> F a -> F b
    """
    raise TypeError('Unable to locate implementation for (%s, %s)' % (Ff.__class__.__name__,
                                                                      Fa.__class__.__name__))

@generic
def unit(a):
    """
    Signature: Applicative F => unit :: a -> F a
    """
    raise TypeError('Unable to locate type-specific implementation')


@functor.fmap.register(Applicative)
def fmap(f, Fa):
    return unit.resolve(Fa.__class__)(f) |ap| Fa


#########################################################################################
#########################################################################################


class Alternative(Applicative):
    """
    The alternative type
    """
    pass


@generic
def empty():
    """
    Signature: Alternative F => empty :: F a
    """
    raise TypeError('Unable to locate type-specific implementation')

@infix
@auto_bind
@multipledispatch
def append(Fa, Fa2):
    """
    Signature:  Alternative F => append :: F a -> F a -> F a
    """
    raise TypeError('Unable to locate implementation for (%s, %s)' % (Fa.__class__.__name__,
                                                                      Fa2.__class__.__name__))
