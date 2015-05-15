"""
This module provides utilities for manipulating functions

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from pyfun.decorators import infix


@infix
def compose(g, f):
    """
    Returns a new function h which is such that h(...) = g(f(...))
    """
    return lambda *args, **kwargs: g(f(*args, **kwargs))


class MatchError(RuntimeError):
    """
    Error representing a failure to match a case
    """
    pass

def match(*cases):
    """
    This function emulates the match statement from functional languages
    
    Each case is a tuple of (predicate, function)
    The function is only called if the predicate passes
    The predicate and the function receive all of the arguments passed
    """
    def select(*args, **kwargs):
        for p, f in cases:
            if p(*args, **kwargs):
                return f(*args, **kwargs)
        raise MatchError('Could not find suitable match')
    return select

def match_types(*cases):
    """
    Similar to match except that instead of a predicate, a tuple of expected types
    is given
    """
    # Transform the tuples into predicates
    def to_pred(*types):
        def match_types(*args):
            return len(types) == len(args) and all(isinstance(a, t) for a, t in zip(args, types))
        return match_types
    return match(*[(to_pred(*ts), f) for ts, f in cases])
