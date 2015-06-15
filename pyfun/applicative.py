"""
This module provides the applicative and alternative types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, functools, collections

from .funcutils import n_args, auto_bind, auto_bind_n
from .functor import Functor


class Applicative(Functor):
    """
    The applicative type, a functor with application
    """

    @abc.abstractmethod
    def ap(self, Fa: Applicative) -> Applicative:
        """
        Perform computation inside the applicative structure
        
        `self` must be an applicative over functions
            
        Signature: `Applicative F => F<(a -> b)>.ap :: F<a> -> F<b>`
        """

    @abc.abstractmethod
    @staticmethod
    def unit(a) -> Applicative:
        """
        Lifts a value into the applicative structure
            
        Signature: `Applicative F => unit :: a -> F<a>`
        """

    def map(self, f: collections.Callable) -> Applicative:
        return self.__class__.unit(f).ap(self)
    

def lift(f):
    """
    Lifts `f` into a function over applicatives
    
    The returned function is auto-bound
    
    NOTE: This function only considers the **required positional** arguments of `f`
          For lifting functions with optional positional arguments, see `lift_n`
        
    This method can be used as a decorator
        
    Signature: `Applicative F => lift :: (a1 -> a2 -> ... -> r) -> F<a1> -> F<a2> -> ... -> F<r>`
    """
    return lift_n(n_args(f), f)


@auto_bind
def lift_n(n: int, f):
    """
    Lifts `n` arguments of the given function into a function over applicatives
        
    If only `n` is given, another function is returned that can be used as a decorator

    Signature: `Applicative F => lift_n :: int -> (a1 -> a2 -> ... aN -> r) -> F<a1> -> F<a2> -> ... F<aN> -> F<r>`
    """
    # Auto-bind f for n arguments, so we can call it with an argument and get a
    # function accepting the rest of the arguments back
    f = auto_bind_n(n, f)
    
    @functools.wraps(f)
    def lifted(*args):
        # If no arguments are given, just call f with no args
        # Otherwise, use the first argument to work out what applicative to lift the
        # function into before using ap to sequence the computation
        return functools.reduce(lambda a, x: a.ap(x), args[1:], args[0].map(f)) if args else f()
    # Auto-bind the lifted function for n arguments
    return auto_bind_n(n, lifted)


#########################################################################################
#########################################################################################


class Alternative(Applicative):
    """
    The alternative type, a monoid on applicatives
    """
    
    @abc.abstractmethod
    def binop(self, Fother: Alternative) -> Alternative:
        """
        An associative binary operation
           
        Signature: `Alternative F => F<a>.binop :: F<a> -> F<a>`
        """
    
    @abc.abstractmethod
    @staticmethod
    def empty() -> Alternative:
        """
        The identity of `binop`
            
        Signature: `Alternative F => empty :: F<a>`
        """
