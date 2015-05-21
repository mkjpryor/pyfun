"""
This module provides the monad and monad-plus types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc

from .funcutils import auto_bind, identity
from .applicative import Applicative, Alternative


class Monad(Applicative):
    """
    The monad type, best thought of as an abstract datatype of actions
    """

    @abc.abstractmethod
    def flatmap(self, f):
        """
        Sequentially compose two actions, using the result from the first as input
        to the second
        
        Signature:  `Monad M => M<a>.flatmap :: (a -> M<b>) -> M<b>`
        """
        pass
    
    def ap(self, other):
        return self >= (lambda f: other >= (lambda a: self.__class__.unit(f(a))))
        
    def __ge__(self, other):
        """
        Alternative syntax for `flatmap`: `Ma >= f == f <= Ma == Ma.flatmap(f)`
        """
        return self.flatmap(other)
    

# Monad operators

@auto_bind
def flatmap(Ma, f):
    """
    Sequentially compose two actions, using the result from the first as input
    to the second
        
    Signature: `Monad M => flatmap :: M<a> -> (a -> M<b>) -> M<b>`
    """
    return Ma >= f


def join(Ma):
    """
    Removes a layer of monadic structure
    
    Signature: `Monad M => join :: M<M<a>> -> M<a>`
    """
    return Ma >= identity


#########################################################################################
#########################################################################################


class MonadPlus(Monad, Alternative):
    """
    The monad-plus type, for a monad that supports success and failure
    """
    pass


# MonadPlus operators

def filter(p, Ma):
    """
    Generic MonadPlus equivalent of filter for lists
    
    Signature: `MonadPlus M => filter :: (a -> bool) -> M<a> -> M<a>`
    """
    unit = Ma.__class__.unit
    empty = Ma.__class__.empty
    return Ma >= (lambda a: unit(a) if p(a) else empty())
    