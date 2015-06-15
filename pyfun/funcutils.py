"""
This module provides utilities for manipulating functions

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools, inspect
from inspect import Parameter as P


def identity(x):
    """
    The identity function
    
    >>> identity(10)
    10
    >>> identity("10")
    '10'
    >>> identity([1,2,3,4,5])
    [1, 2, 3, 4, 5]
    """
    return x


def __is_required_positional(param):
    """
    Utility function for use in this module - is the given parameter a required positional
    parameter?
    """
    return param.kind == P.POSITIONAL_OR_KEYWORD and param.default is P.empty


def n_args(f):
    """
    Returns the number of **required positional** arguments of `f`
    
    >>> def func1(a, b, c): pass
    ...
    >>> n_args(func1)
    3
    >>> def func2(a, b, c = 0): pass
    ...
    >>> n_args(func2)
    2
    >>> def func3(a, b = 0, *args): pass
    ...
    >>> n_args(func3)
    1
    """
    return len([p for p in inspect.signature(f).parameters.values() if __is_required_positional(p)])


def chain(*funcs):
    """
    Returns a new function that is the composition of the given functions from left
    to right, e.g. `chain(p, q, r) == lambda *args, **kwargs: r(q(p(*args, **kwargs)))`
    
    All functions except the first should be functions of a single argument
    
    >>> def double(x): return x * 2
    ...
    >>> def third(x): return x // 3
    ...
    >>> def add(x, y): return x + y
    ...
    >>> f = chain(add, third, double)
    >>> f(2, 4)
    4
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
    
    >>> def double(x): return x * 2
    ...
    >>> def third(x): return x // 3
    ...
    >>> def add(x, y): return x + y
    ...
    >>> f = compose(double, third, add)
    >>> f(2, 4)
    4
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
    
    >>> def add(a, b, c): return a + b + c
    ...
    >>> f = partial(add, 1, _, 3)
    >>> f(2)
    6
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


def auto_bind(f, *bound):
    """
    Allows for the automatic binding of **required positional arguments** to `f`,
    only calling `f` when all required positional arguments have a value
    
    The placeholder `_` can be given to indicate that the argument will be provided
    in a later call
    
    If binding of optional positional arguments, as well as required ones, is 
    needed, `auto_bind_n` should be used instead
    
    This function can be used as a decorator, e.g.:
    
    >>> @auto_bind
    ... def add(a, b, c, d = 0): return a + b + c + d
    ...
    >>> add(1, 2, 3)
    6
    >>> add(1, 2)(3)
    6
    >>> add(1)(2, 3)
    6
    >>> add(1)(2)(3)
    6
    >>> add(_, 2)(1, 3)
    6
    """
    return auto_bind_n(n_args(f), f, *bound)


def auto_bind_n(n, f = None, *bound):
    """
    Returns a new function that allows for the binding of exactly `n` **positional arguments**
    to `f`, only calling `f` when there are `n` real values (i.e. all placeholders have been
    filled)
    
    If `f` is not given, the resulting function can be used as a decorator, e.g.:
    
    >>> @auto_bind_n(3)
    ... def add(a, b, c = 0): return a + b + c
    ...
    >>> add(1, 2, 3)
    6
    >>> add(1, 2)(3)
    6
    >>> add(1)(2, 3)
    6
    >>> add(1)(2)(3)
    6
    >>> add(_, 2)(1, 3)
    6
    """
    if f is None:
        def wrapper(g):
            return auto_bind_n(n, g, *bound)
        return wrapper
    
    @functools.wraps(f)
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
        # If no arguments were given, just return the wrapper
        # NOTE: The case where n = 0 is dealt with above
        if not args_use: return backfill_args
        # Otherwise, we want to continue to bind arguments
        return auto_bind_n(n, f, *args_use)
    backfill_args.__autobound__ = True
    return backfill_args
