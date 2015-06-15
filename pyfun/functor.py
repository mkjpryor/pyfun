"""
This module provides the functor type and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, collections


class Functor(abc.ABC):
    """
    The functor type for types that can be mapped over
    """

    @abc.abstractmethod
    @staticmethod
    def map(self, f: collections.Callable) -> Functor:
        """
        Returns a new functor 'containing' the result of applying `f` to the 'contents' of
        this functor
        
        Signature: `Functor F => F<a>.map :: (a -> b) -> F<b>`
        """
