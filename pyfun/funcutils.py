"""
This module provides utilities for manipulating functions

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools

from pyfun.decorators import infix


@infix
def compose(*funcs):
    """
    Returns a new function that composes the given functions from right to left
    
    All functions except the last should be functions of a single argument
    
    E.g. the following are identical:
     
        h = compose(r, q, p)
        h = lambda *args, **kwargs: r(q(p(*args, **kwargs)))
    """
    return chain(*reversed(funcs))


@infix
def chain(*funcs):
    """
    Returns a new function that composes the given functions from left to right
    
    All functions except the first should be functions of a single argument
    
    E.g. the following are identical:
     
        h = chain(p, q, r)
        h = lambda *args, **kwargs: r(q(p(*args, **kwargs)))
    """
    if not funcs:
        raise ValueError('At least one function must be given')
    funcs = list(funcs)
    first = funcs.pop(0)
    def exec_chain(*args, **kwargs):
        return functools.reduce(lambda result, f: f(result), funcs, first(*args, **kwargs))
    return exec_chain


# Create an object of some anonymous type to serve as a placeholder
_ = type('', (object,), {})()
def partial(f, *bound, **kwbound):
    """
    Binds the first n arguments of f to the given arguments, returning a new function
    that accepts the rest of the arguments before calling f
    
    When binding arguments, the placeholder _ (underscore) can be given to indicate that
    the argument will be filled later
    
    E.g. to bind the first and third arguments of a function:
    
        def add(a, b, c):
            return a + b + c
            
        f = partial(add, 1, _, 3)
        
        print(f(2))  # Calls f(1, 2, 3) and prints 6
    """
    def func(*args, **kwargs):
        # We want the args as a mutable list
        args = list(args)
        
        # Start with the bound arguments
        args_use = list(bound)
        kwargs_use = dict(kwbound)
        
        # Merge in the positional args from the left, observing any placeholders
        for i, item in enumerate(args_use):
            if not args: break
            if item is _: args_use[i] = args.pop(0)
        args_use.extend(args)
        
        # Update the bound keyword args with the provided ones
        kwargs_use.update(kwargs)
        
        # Call the underlying function
        return f(*args_use, **kwargs_use)
    return func


class MatchError(RuntimeError):
    """
    Error representing a failure to match a case
    """
    pass

def match(*cases):
    """
    This function emulates the match statement from functional languages
    
    Each case is a tuple of (matcher, function) where:
        function is only called if the matcher passes
        matcher is one of:
          * A single type
              * In this case, the match will only succeed if exactly one argument of the
                correct type is given when the match expression is called
          * A tuple of types, one per argument
              * In this case, a tuple can be given as an element to represent a union over types
          * A predicate, which will receive all the arguments which the match expression
            is called with
          * None, indicating a default case that will always match
          
    Cases are evaluated in the order in which they are given, with the first match being
    executed
    """
    # Transform any types or tuples of types into predicates
    cases = list(cases)
    for i, c in enumerate(cases):
        if c[0] is None:
            cases[i] = (lambda *args, **kwargs: True, c[1])
            continue
        if isinstance(c[0], type):
            c = ((c[0],), c[1])
        if isinstance(c[0], tuple):
            cases[i] = (__to_predicate(*c[0]), c[1])
    # Return a function that selects the first matching case and executes it
    def select(*args, **kwargs):
        for p, f in cases:
            if p(*args, **kwargs):
                return f(*args, **kwargs)
        raise MatchError('Could not find suitable match')
    return select

def __to_predicate(*types):
    """
    Converts a set of types into a predicate that tests the given arguments against those types
    """
    def match_types(*args):
        return len(types) == len(args) and all(isinstance(a, t) for a, t in zip(args, types))
    return match_types
