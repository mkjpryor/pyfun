"""
This module provides the functor type and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, collections

from .funcutils import auto_bind, singledispatch


# We derive from ABC purely for the convenience of __subclasshook__ (as opposed to defining
# our own metaclasses to use __(subclass|instance)check__
class Functor(abc.ABC):
    """
    The functor type for types that can be mapped over
    
    A type becomes a functor by providing an implementation for map
    """

    @classmethod
    def __subclasshook__(cls, other):
        return map.resolve(other) is not map.default


## Functor operators

@auto_bind
@singledispatch(1)
def map(f: collections.Callable, Fa: Functor) -> Functor:
    """
    Returns a functor 'containing' the result of applying `f` to the 'contents' of `Fa`
    
    Signature: `Functor F => map :: (a -> b) -> F<a> -> F<b>`
    """
    raise TypeError('Not implemented for %s' % type(Fa).__name__)
