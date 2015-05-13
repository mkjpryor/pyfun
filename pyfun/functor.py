"""
This module provides the functor type and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from pyfun.decorators import singledispatch, auto_bind_n


#########################################################################################
## The Functor class exists purely for instance and subclass checking
##
## A class is considered a functor if there is an fmap implementation available for it
#########################################################################################

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
        return fmap.dispatch(subclass) is not fmap.dispatch(object)
    

class Functor(metaclass = FunctorMeta):
    """
    The actual functor type
    
    The type itself provides no functionality, but can be used to check if an object
    or class is a functor using isinstance or issubclass
    """
    pass


#########################################################################################
## Functions that must be defined to be a functor
#########################################################################################

@auto_bind_n(2)     # Because @singledispatch returns an argument that has
                    # no required positional args, we must use auto_bind_n
@singledispatch(1)  # Dispatch based on the type of the 2nd argument
def fmap(f, Fa):
    """
    Signature:  Functor F => (a -> b) -> F a -> F b
    """
    raise NotImplementedError("Not implemented for %s" % type(Fa))
