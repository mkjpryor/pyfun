"""
This module provides the functor type and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc

from .funcutils import auto_bind


class Functor(abc.ABC):
    """
    The functor type for types that can be mapped over
    """

    @abc.abstractmethod
    def map(self, f):
        """
        Returns a functor 'containing' the result of applying `f` to the 'contents' of `self`
    
        Signature: `Functor F => F<a>.map :: (a -> b) -> F<b>`
        """
        pass

    def __rshift__(self, other):
        """
        Alternative syntax for `map`: `Fa >> f == Fa.map(f)`
        """
        return self.map(other)
        
    def __rlshift__(self, other):
        """
        Alternative syntax for `map`: `f << Fa == Fa.map(f)`
        """
        return self.map(other)


## Functor operators

@auto_bind
def map(f, Fa):
    """
    Returns a functor 'containing' the result of applying `f` to the 'contents' of `Fa`
    
    Signature: `Functor F => map :: (a -> b) -> F<a> -> F<b>`
    """
    return Fa >> f
