"""
This module provides the monad and monad-plus types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, collections

from .funcutils import identity, auto_bind
from .applicative import Applicative, Alternative


class Monad(Applicative):
    """
    The monad type, best thought of as an abstract datatype of actions
    """

    def flatmap(self, f: collections.Callable) -> Monad:
        """
        Sequentially compose two actions, using the result from the first as input
        to the second
            
        Signature: `Monad M => M<a>.flatmap :: (a -> M<b>) -> M<b>`
        """

    def ap(self, Ma: Monad) -> Monad:
        return self.flatmap(lambda f: Ma.flatmap(lambda a: self.__class__.unit(f(a))))

    def join(self) -> Monad:
        """
        Removes a layer of monadic structure
        
        Signature: `Monad M => M<M<a>>.join :: M<a>`
        """
        return self.flatmap(identity)


#########################################################################################
#########################################################################################


class MonadPlus(Monad, Alternative):
    """
    The monad-plus type, for a monad that supports success and failure
    """

    def filter(self, p: collections.Callable) -> MonadPlus:
        """
        Generic MonadPlus equivalent of filter for lists
        
        Signature: `MonadPlus M => M<a>.filter :: (a -> bool) -> M<a>`
        """
        return self.flatmap(lambda a: self.__class__.unit(a) if p(a) else self.__class__.empty())
