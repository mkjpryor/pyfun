"""
This module provides the functor type and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

__all__ = ["FunctorMeta", "Functor", "fmap"]

from pyfun.decorators import singledispatch, auto_bind


class FunctorMeta(type):
    """
    Meta-class implementing checks for membership of the functor type
    """
    
    def __instancecheck__(self, instance):
        """
        Implements isinstance for checking if something is a functor
        """
        # An instance is a functor is its class is a functor type
        return issubclass(instance.__class__, self)
    
    def __subclasscheck__(self, subclass):
        """
        Implements issubclass for checking if something is a functor
        """
        # A class is a functor if there is a specific fmap implementation for it
        return fmap.resolve(subclass) is not fmap.resolve(object)
    

class Functor(metaclass = FunctorMeta):
    """
    The actual functor type
    
    The type itself provides no functionality, but can be used to check if an object
    or class is a functor using isinstance or issubclass
    """
    pass


@auto_bind
@singledispatch(1)
def fmap(f, Fa):
    """
    Signature:  Functor F => fmap :: (a -> b) -> F a -> F b
    """
    pass
