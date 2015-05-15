"""
This module provides function decorators

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools
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
    """
    # If the function is called directly, we want to tell people to use resolve
    def raise_generic_error(*args, **kwargs):
        raise RuntimeError('Generic functions cannot be invoked directly - ' +
                           'use resolve to find a type-specific implementation')
    # Use a dummy function as the implementation for object
    # We can then check to see if a better implementation has been provided for object
    # by comparing the resolved value to this function
    def dummy(*args, **kwargs): pass
    # We want to utilise all the effort that has gone into the dispatch algorithm
    # of functools.singledispatch
    dispatcher = functools.singledispatch(dummy)
    # We can just use the register implementation directly
    raise_generic_error.register = dispatcher.register
    # For resolve, we want to raise an error if we can't find an implementation
    def resolve(the_type):
        impl = dispatcher.dispatch(the_type)
        if impl is dummy:
            raise TypeError('Unable to locate implementation of %s for %s' % (f.__name__, repr(the_type)))
        return impl
    raise_generic_error.resolve = resolve
    # Make the wrapper function look like the wrapped function before returning it
    functools.update_wrapper(raise_generic_error, f)
    return raise_generic_error


def singledispatch(n):
    """
    Returns a decorator that allows the decorated function to do single dispatch
    on the type of the n-th *positional* argument (0-indexed)
    
    The decorated function will never be invoked directly - if no implementation can
    be found for the type of the n-th argument, an error will be raised
    """
    def decorator(f):
        # Use a generic under the hood for dispatching
        dispatcher = generic(f)
        # We want to return a function that uses the dispatcher to dispatch on the n-th arg
        def dispatch_on_nth_arg(*args, **kwargs):
            return dispatcher.resolve(args[n].__class__)(*args, **kwargs)
        # Attach the register method from the dispatcher as a method on the function to
        # allow the registering of specific implementations
        dispatch_on_nth_arg.register = dispatcher.register
        # Make the wrapper function look like the wrapped function before returning it
        functools.update_wrapper(dispatch_on_nth_arg, f)
        return dispatch_on_nth_arg
    return decorator


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
