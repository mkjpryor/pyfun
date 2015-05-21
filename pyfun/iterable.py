"""
This module implements several type-classes for iterables

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import collections, itertools

from .monad import MonadPlus


class Iterable(collections.Iterable, MonadPlus):
    def __init__(self, iterable):
        self.__iter = iter(iterable)
        
    def __iter__(self):
        # In order to be repeatedly iterable, we must tee our iterator every
        # time a new iterator is requested 
        self.__iter, iter = itertools.tee(self.__iter)
        return iter
        
    def binop(self, other):
        return Iterable(itertools.chain(self, other))
    
    @staticmethod
    def empty():
        return Iterable(())
        
    def flatmap(self, f):
        return Iterable(x for xs in self for x in f(xs))
    
    @staticmethod
    def unit(a):
        return Iterable((a,))
