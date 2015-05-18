"""
This module provides function decorators

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools
from inspect import signature, Parameter as P

from multipledispatch.core import ismethod
from multipledispatch.dispatcher import Dispatcher, MethodDispatcher


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
    n = len([p for p in signature(f).parameters.values() if p.kind == P.POSITIONAL_OR_KEYWORD and
                                                            p.default is P.empty])
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


def generic(f):
    """
    Decorator that marks the decorated function as generic, and allows implementations
    to be registered for particular types
    
    The returned function cannot be invoked directly - the correct function should
    be obtained by using the resolve method and passing the required type
    
    The decorated function is used as the implementation for object, i.e. the implementation
    that will be used if no specific implementations are registered for a type
    """
    # If the function is called directly, we want to tell people to use resolve
    def raise_generic_error(*args, **kwargs):
        raise RuntimeError('Generic functions cannot be invoked directly - ' +
                           'use resolve to find a type-specific implementation')
    # We want to utilise all the effort that has gone into the dispatch algorithm
    # of the multipledispatch package
    dispatcher = MethodDispatcher(f.__name__) if ismethod(f) else Dispatcher(f.__name__)
    # Use the register implementation directly and rename dispatch to resolve
    raise_generic_error.register = dispatcher.register
    raise_generic_error.resolve  = dispatcher.dispatch
    # Make the wrapper function look like the wrapped function before returning it
    functools.update_wrapper(raise_generic_error, f)
    return raise_generic_error


def multipledispatch(f):
    """
    Decorator that allows multiple dispatch to be done on the given function with
    registration similar to functools.singledispatch
    
    The decorated function is used as the default implementation if there are no
    other matches
    """
    # Get an appropriate dispatcher
    dispatcher = MethodDispatcher(f.__name__) if ismethod(f) else Dispatcher(f.__name__)
    # The function we return a function attempts to use the dispatcher, falling back on f
    def dispatch_with_fallback(*args, **kwargs):
        try:
            return dispatcher(*args, **kwargs)
        except NotImplementedError:
            return f(*args, **kwargs)
    # When resolving, we want to use f as a fallback case as well
    def resolve_with_fallback(*types):
        return dispatcher.dispatch(*types) or f
    # Attach functions to register and resolve implementations for particular types
    dispatch_with_fallback.register = dispatcher.register
    dispatch_with_fallback.resolve  = resolve_with_fallback
    # Add a default property that returns f
    dispatch_with_fallback.default = property(lambda _: f)
    # Make the returned function look like f
    functools.update_wrapper(dispatch_with_fallback, f)
    return dispatch_with_fallback


def infix(f):
    """
    Allows a function of two arguments to be used as an infix function
    
    For example:
    
        @infix
        def add(a, b):
            return a + b
            
        print(add(1, 2))  # Prints 3
        print(1 |add| 2)  # Prints 3
    """
    def start_infix(_, other):
        # When the infix expression is started, return a new object that
        # knows how to finish the expression
        g = functools.partial(f, other)
        return type('', (object,), { '__or__' : lambda _, x: g(x) })()
    # Return an object that knows how to start the infix expression
    # It can also be called directly
    ifix = type('', (object,), {
        '__ror__' : start_infix,
        '__call__' : lambda _, *args, **kwargs: f(*args, **kwargs)
    })()
    # Make it look like f for any future decorators
    functools.update_wrapper(ifix, f)
    return ifix
