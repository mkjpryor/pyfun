"""
This module provides the applicative and alternative types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, functools

from .funcutils import auto_bind, auto_bind_n, n_args
from .functor import Functor


class Applicative(Functor):
    """
    The applicative type, a functor with application
    """
    
    @abc.abstractmethod
    def ap(self, other):
        """
        Perform computation inside the applicative structure
        
        Signature:  `Applicative F => F<(a -> b)>.ap :: F<a> -> F<b>`
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def unit(a):
        """
        Lifts a value into the applicative structure
        
        Signature: `Applicative F => unit :: a -> F<a>`
        """
        pass

    def __xor__(self, other):
        """
        Alternative syntax for `ap`: `Ff ^ Fa == Ff.ap(Fa)`
        """
        return self.ap(other)
    
    def map(self, f):
        return self.__class__.unit(f) ^ self
    
    
## Applicative operators

@auto_bind
def ap(Ff, Fa):
    """
    Perform computation inside the applicative structure
        
    Signature: `Applicative F => ap :: F<(a -> b)> -> F<a> -> F<b>`
    """
    return Ff ^ Fa


@auto_bind
def unit(cls, a):
    """
    Lifts a value into the applicative structure for `cls`
        
    Signature: `Applicative F => unit :: F -> a -> F<a>`
    """
    return cls.unit(a)


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
def lift_n(n, f):
    """
    Lifts `n` arguments of the given function into a function over applicatives
        
    If only `n` is given, another function is returned that can be used as a decorator

    Signature: `Applicative F => lift_n :: int -> (a1 -> a2 -> ... aN -> r) -> F<a1> -> F<a2> -> ... F<aN> -> F<r>`
    """
    # Auto-bind f for n arguments, so we can call it with an argument and get a
    # function accepting the rest of the arguments back
    f = auto_bind_n(n, f)
    
    def lifted(*args):
        # If no arguments are given, just call f with no args
        # Otherwise, use the first argument to work out what applicative to lift the
        # function into before using ap to sequence the computation
        return functools.reduce(ap, args, args[0].__class__.unit(f)) if args else f()
    # Update argspec, etc. to look like f
    functools.update_wrapper(lifted, f)
    # Auto-bind the lifted function for n arguments
    return auto_bind_n(n, lifted)


#########################################################################################
#########################################################################################


class Alternative(Applicative):
    """
    The alternative type, a monoid on applicatives
    """

    @abc.abstractmethod
    def binop(self, other):
        """
        An associative binary operation
        
        Signature: `Alternative F => F<a>.binop :: F<a> -> F<a>`
        """
        pass
    
    @staticmethod
    @abc.abstractmethod
    def empty():
        """
        The identity of `binop`
        
        Signature: `Alternative F => empty :: F<a>`
        """
        pass
    
    def __or__(self, other):
        """
        Alternative syntax for `binop`: `Fa | Fb == Fa.binop(Fb)`
        """
        return self.binop(other)
    
    
## Alternative operators

@auto_bind
def binop(Fa, Fother):
    """
    An associative binary operation
       
    Signature: `Alternative F => binop :: F<a> -> F<a> -> F<a>`
    """
    return Fa | Fother

def empty(cls):
    """
    The identity of `binop`
        
    Signature: `Alternative F => empty :: F -> F<a>`
    """
    return cls.empty()
