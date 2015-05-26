"""
This module provides the monad and monad-plus types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, collections

from .funcutils import identity, auto_bind, multipledispatch
from .applicative import Alternative, ap, unit, binop, empty


class Monad(abc.ABC):
    """
    The monad type, best thought of as an abstract datatype of actions
    
    A type becomes a monad by providing implementions for flatmap and unit
    """

    @classmethod
    def __subclasshook__(cls, other):
        return flatmap.resolve(other, collections.Callable) is not flatmap.default \
               and unit.resolve(other) is not None


# Monad operators

@auto_bind
@multipledispatch
def flatmap(Ma: Monad, f: collections.Callable) -> Monad:
    """
    Sequentially compose two actions, using the result from the first as input
    to the second
        
    Signature: `Monad M => flatmap :: M<a> -> (a -> M<b>) -> M<b>`
    """
    raise TypeError('Not implemented for %s' % type(Ma).__name__)


@ap.register
def _ap(Mf: Monad, Ma: Monad) -> Monad:
    return flatmap(Mf, lambda f: flatmap(Ma, lambda a: unit.resolve(type(Ma))(f(a))))


@multipledispatch
def join(Ma: Monad) -> Monad:
    """
    Removes a layer of monadic structure
    
    Signature: `Monad M => join :: M<M<a>> -> M<a>`
    """
    return flatmap(Ma, identity)


#########################################################################################
#########################################################################################


class MonadPlus(abc.ABC):
    """
    The monad-plus type, for a monad that supports success and failure
    
    A type becomes a monad-plus by being a monad and an alternative
    """

    @classmethod
    def __subclasshook__(cls, other):
        return issubclass(other, Monad) and issubclass(other, Alternative)


# MonadPlus operators

@auto_bind
@multipledispatch
def filter(p: collections.Callable, Ma: MonadPlus) -> MonadPlus:
    """
    Generic MonadPlus equivalent of filter for lists
    
    Signature: `MonadPlus M => filter :: (a -> bool) -> M<a> -> M<a>`
    """
    return flatmap(Ma, lambda a: unit.resolve(type(Ma))(a) if p(a) else empty.resolve(type(Ma))())
    