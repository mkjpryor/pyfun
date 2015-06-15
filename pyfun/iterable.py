"""
This module implements several type-classes for iterables

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import itertools, collections

from .monad import MonadPlus


class IterableM(MonadPlus):
    """
    Monad-plus implementation for iterables
    """
    
    def __init__(self, iterable):
        self.__iter = iter(iterable)
        
    def __iter__(self):
        self.__iter, iter = itertools.tee(self.__iter)
        return iter

    def flatmap(self, f: collections.Callable) -> IterableM:
        return IterableM(itertools.chain.from_iterable(f(x) for x in self.__iter))
    
    @staticmethod
    def unit(a) -> IterableM:
        return IterableM((a,))
    
    def binop(self, Fother: collections.Iterable) -> IterableM:
        return IterableM(itertools.chain(self, Fother))
        
    @staticmethod
    def empty() -> IterableM:
        return IterableM(())
