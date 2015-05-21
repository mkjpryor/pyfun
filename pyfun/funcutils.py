"""
This module provides utilities for manipulating functions

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools, inspect
from inspect import Parameter as P


def identity(x):
    """
    The identity function
    """
    return x


def n_args(f):
    """
    Returns the number of **required positional** arguments of `f`
    """
    is_required_positional = lambda p: p.kind == P.POSITIONAL_OR_KEYWORD and p.default is P.empty
    return len([p for p in inspect.signature(f).parameters.values() if is_required_positional(p)])


def chain(*funcs):
    """
    Returns a new function that is the composition of the given functions from left
    to right, e.g. `chain(p, q, r) == lambda *args, **kwargs: r(q(p(*args, **kwargs)))`
    
    All functions except the first should be functions of a single argument
    """
    if not funcs:
        raise ValueError('At least one function must be given')
    funcs = list(funcs)
    first = funcs.pop(0)
    def exec_chain(*args, **kwargs):
        return functools.reduce(lambda result, f: f(result), funcs, first(*args, **kwargs))
    return exec_chain


def compose(*funcs):
    """
    Similar to chain except that the functions are composed from right to left
    """
    return chain(*reversed(funcs))


# Create an object of some anonymous type to serve as a placeholder
_ = type('', (object,), {})()
def partial(f, *bound, **kwbound):
    """
    Binds the first `n` positional arguments of `f` to the given arguments, returning a
    new function that accepts the rest of the arguments before calling `f`
    
    When binding arguments, the placeholder `_` (underscore) can be given to indicate that
    the argument will be filled later
    
    E.g. to bind the first and third arguments of a function:
    
        from pyfun.funcutils import partial, _
    
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


def auto_bind(f):
    """
    Allows for the automatic binding of **required positional arguments** to `f`,
    only calling `f` when all required positional arguments have a value
    
    The placeholder `_` can be given to indicate that the argument will be provided
    in a later call
    
    If binding of optional positional arguments, as well as required ones, is 
    needed, `auto_bind_n` should be used instead
    
    This function can be used as a decorator, e.g.:
    
        from pyfun.funcutils import auto_bind

        @auto_bind
        def add(a, b, c):
            return a + b + c
        
        print(add(1, 2, 3))     # Prints 6
        print(add(1, 2)(3))     # Prints 6
        print(add(1)(2, 3))     # Prints 6
        print(add(1)(2)(3))     # Prints 6
        print(add(_, 2)(1, 3))  # Prints 6
    """
    return auto_bind_n(n_args(f), f)    


def auto_bind_n(n, f = None, bound = ()):
    """
    Returns a decorator that automatically binds `n` **positional** arguments of `f`
    
    If `f` is not given, this function returns a function that can be used as a decorator
    """
    if not f:
        def decorator(g):
            return auto_bind_n(n, g, bound)
        return decorator

    def backfill_args(*args):
        args = list(args)
        args_use = list(bound)
        # Merge args with the already bound arguments, observing placeholders
        for i, item in enumerate(args_use):
            if not args: break
            if item is _: args_use[i] = args.pop(0)
        args_use.extend(args)
        # If we have enough arguments to call f and return a value, do it
        if len(args_use) >= n and not any(a is _ for a in args_use[:n]): return f(*args_use[:n])
        # If no arguments were given, just return f
        # NOTE: The case where n = 0 is dealt with above
        if not args_use: return f
        # Otherwise, we want to continue to bind arguments
        return auto_bind_n(n, f, tuple(args_use))
    # Set a flag we can use to test if the function is auto-bound
    backfill_args.__autobound__ = True
    # Before returning it, update the wrapper function to look like the
    # wrapped function
    functools.update_wrapper(backfill_args, f)
    return backfill_args
