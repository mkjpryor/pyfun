"""
This module provides function decorators

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools, types
from inspect import signature, Parameter as P


def auto_bind(f):
    """
    Allows for the automatic binding of **required positional arguments** to the
    decorated function, only calling the decorated function when all required
    positional arguments have a value.
    
    If binding of optional positional arguments, as well as required ones, is 
    needed, `auto_bind_n` should be used instead.
    
    Example:
    
        from pyfun.decorators import auto_bind

        @auto_bind
        def add(a, b, c):
            return a + b + c
        
        print(add(1, 2, 3))  # Prints 6
        print(add(1, 2)(3))  # Prints 6
        print(add(1)(2, 3))  # Prints 6
        print(add(1)(2)(3))  # Prints 6
    """
    # Try to detect the number of required, positional arguments for f
    n = len([p for p in signature(f).parameters.values() if (p.kind == P.POSITIONAL_OR_KEYWORD or
                                                             p.kind == P.POSITIONAL_ONLY)
                                                            and p.default is P.empty])
    return auto_bind_n(n)(f)


def auto_bind_n(n):
    """
    Returns a decorator that automatically binds n *positional* arguments of
    the the decorated function
    """
    def decorator(f):
        def bind_args(*args):
            # If we have enough arguments to call f and return a value, do it
            if len(args) >= n:
                return f(*args[0:n])
            # Otherwise, bind the arguments we have
            return auto_bind_n(n - len(args))(functools.partial(f, *args))
        # Before returning it, update the wrapper function to look like the
        # wrapped function
        functools.update_wrapper(bind_args, f)
        return bind_args
    return decorator


def singledispatch(n):
    """
    Returns a decorator that allows the decorated function to do single dispatch
    on the type of the n-th *positional* argument (0-indexed)
    """
    def decorator(f):
        # We want to utilise all the effort that has gone into the dispatch algorithm
        # of functools.singledispatch - the best way to do this is just use it as our
        # dispatcher with a dummy function
        dispatcher = functools.singledispatch(lambda *args, **kwargs: None)
        # Assign f as the function for object
        dispatcher.register(object, f)
        # We want to return a function that uses the dispatcher to dispatch on the n-th arg
        def dispatch_on_nth_arg(*args, **kwargs):
            return dispatcher.dispatch(args[n].__class__)(*args, **kwargs)
        # Attach the methods from the dispatcher as methods on the function, to allow
        # it to behave in a similar way to functools.singledispatch
        dispatch_on_nth_arg.register = dispatcher.register
        dispatch_on_nth_arg.dispatch = dispatcher.dispatch
        dispatch_on_nth_arg.registry = types.MappingProxyType(dispatcher.registry)
        dispatch_on_nth_arg._clear_cache = dispatcher._clear_cache
        # Make the wrapper function look like the wrapped function before returning it
        functools.update_wrapper(dispatch_on_nth_arg, f)
        return dispatch_on_nth_arg
    return decorator
