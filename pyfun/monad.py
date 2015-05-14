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
def bind(Ma, f):
    """
    Signature:  Monad M => bind :: M a -> (a -> M b) -> M b
    """
    pass

# monad.unit is applicative.unit
unit = applicative.unit


@applicative.apply.register(Monad)
def apply(Mf, Ma):
    return bind(Mf, lambda f: bind(Ma, lambda a: applicative.unit.resolve(Mf.__class__)(f(a))))


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
