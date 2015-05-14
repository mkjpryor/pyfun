"""
This module provides the applicative and alternative types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from pyfun.decorators import singledispatch, generic, auto_bind, infix
from pyfun import functor


class Applicative(functor.Functor):
    """
    The applicative type
    """
    pass


@infix
@auto_bind
@singledispatch(1)
def apply(Ff, Fa):
    """
    Signature:  Applicative F => ap :: F (a -> b) -> F a -> F b
    """
    pass

@generic
def unit(a):
    """
    Signature: Applicative F => unit :: a -> F a
    """
    pass


@functor.fmap.register(Applicative)
def fmap(f, Fa):
    return apply(unit.resolve(Fa.__class__)(f), Fa)


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
    pass

@infix
@auto_bind
@singledispatch(0)
def append(Fa, Fa2):
    """
    Signature:  Alternative F => append :: F a -> F a -> F a
    """
    pass
