"""
This module provides the applicative and alternative types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc, functools

from .funcutils import n_args, auto_bind, auto_bind_n, generic, multipledispatch
from .functor import map


class Applicative(abc.ABC):
    """
    The applicative type, a functor with application
    
    A type becomes an applicative by providing implementations for ap and unit
    """

    @classmethod
    def __subclasshook__(cls, other):
        return ap.resolve(other, other) is not ap.default and unit.resolve(other) is not None
    
        
## Applicative operators

@auto_bind
@multipledispatch
def ap(Ff: Applicative, Fa: Applicative) -> Applicative:
    """
    Perform computation inside the applicative structure
        
    Signature: `Applicative F => ap :: F<(a -> b)> -> F<a> -> F<b>`
    """
    raise TypeError('Not implemented for %s' % type(Ff).__name__)


@generic
def unit(a) -> Applicative:
    """
    Lifts a value into the applicative structure
        
    Signature: `Applicative F => unit :: F -> a -> F<a>`
    """
    pass


@map.register
def _map(f, Fa: Applicative) -> Applicative:
    return ap(unit.resolve(type(Fa))(f), Fa)
    

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
    
    def lifted(*args):
        # If no arguments are given, just call f with no args
        # Otherwise, use the first argument to work out what applicative to lift the
        # function into before using ap to sequence the computation
        return functools.reduce(ap, args[1:], map(f, args[0])) if args else f()
    # Update argspec, etc. to look like f
    functools.update_wrapper(lifted, f)
    # Auto-bind the lifted function for n arguments
    return auto_bind_n(n, lifted)


#########################################################################################
#########################################################################################


class Alternative(abc.ABC):
    """
    The alternative type, a monoid on applicatives
    
    A type becomes an alternative by providing implementations for binop and empty in
    addition to being an applicative
    """

    @classmethod
    def __subclasshook__(cls, other):
        return issubclass(other, Applicative) and \
               binop.resolve(other, other) is not binop.default and \
               empty.resolve(other) is not None    
    

## Alternative operators

@auto_bind
@multipledispatch
def binop(Fa: Alternative, Fother: Alternative) -> Alternative:
    """
    An associative binary operation
       
    Signature: `Alternative F => binop :: F<a> -> F<a> -> F<a>`
    """
    raise TypeError('Not implemented for %s' % type(Fa).__name__)


@generic
def empty() -> Alternative:
    """
    The identity of `binop`
        
    Signature: `Alternative F => empty :: F -> F<a>`
    """
    pass
