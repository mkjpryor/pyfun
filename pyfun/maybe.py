"""
This module defines the Maybe type for cleanly representing the absence of a value

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from collections import Callable, Iterable

from .monad import flatmap, unit, binop, empty


class Maybe:
    """
    A Maybe represents a value that may or may not be present
    """
    pass

class Just(Maybe):
    """
    A Just represents a value that is present
    """
    def __init__(self, value):
        self.value = value
        
    def __bool__(self):
        return True
    
    def __eq__(self, other):
        return isinstance(other, Just) and other.value == self.value
        
    def __hash__(self):
        return hash(self.value)
        
    def __repr__(self):
        return "Just(%s)" % repr(self.value)
    
class Nothing(Maybe):
    """
    A Nothing represents the absence of a value
    """
    def __bool__(self):
        return False
    
    def __eq__(self, other):
        return isinstance(other, Nothing)
        
    def __hash__(self):
        return 0
    
    def __repr__(self):
        return "Nothing"


#########################################################################################
#########################################################################################


def unwrap(x: Maybe):
    """
    Returns the wrapped value if x is a Just, or raises an exception if x is Nothing
    """
    if x:
        return x.value
    else:
        raise TypeError('Cannot unwrap Nothing')
    

def unwrap_or(default, x: Maybe):
    """
    If x is a Just, returns the wrapped value
    If x is Nothing, returns default
    """
    return unwrap(x) if x else default

    
def unwrap_or_else(f: Callable, x: Maybe):
    """
    If x is a Just, returns the wrapped value
    If x is Nothing, returns f()
    """
    return unwrap(x) if x else f()


def to_iter(x: Maybe) -> Iterable:
    """
    Returns an empty iterable if x is Nothing, otherwise an iterable of length 1 containing
    the wrapped value
    """
    if x:
        yield x.value
        

def from_iter(xs: Iterable) -> Maybe:
    """
    Returns Nothing if xs is an empty iterable, otherwise returns a Just containing the
    first element of xs
    """
    try:
        return Just(next(iter(xs)))
    except StopIteration:
        return Nothing()


#########################################################################################
#########################################################################################

# MonadPlus definition

@flatmap.register
def _flatmap(x: Maybe, f: Callable) -> Maybe:
    return f(unwrap(x)) if x else x

@unit.register(Maybe)
def _unit(a) -> Maybe:
    return Just(a)

@binop.register
def _binop(x: Maybe, y: Maybe) -> Maybe:
    return x or y
    
@empty.register(Maybe)
def _empty() -> Maybe:
    return Nothing()
