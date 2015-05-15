"""
This module provides the monad and monad-plus types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from pyfun.decorators import singledispatch, auto_bind, infix
from pyfun import applicative


class Monad(applicative.Applicative):
    """
    The monad type
    """
    pass


@infix
@auto_bind
@singledispatch(0)
def flatmap(Ma, f):
    """
    Signature:  Monad M => flatmap :: M a -> (a -> M b) -> M b
    """
    raise TypeError('Unable to locate implementation for %s' % repr(Ma.__class__))

# monad.unit is applicative.unit
unit = applicative.unit


@applicative.ap.register(Monad, Monad)
def ap(Mf, Ma):
    return Mf |flatmap| ( lambda f: Ma |flatmap| ( lambda a: unit.resolve(Mf.__class__)(f(a))))


#########################################################################################
#########################################################################################


class MonadPlus(Monad, applicative.Alternative):
    """
    The monad-plus type
    """
    pass


# MonadPlus requires the same functions as Applicative
empty  = applicative.empty
append = applicative.append
