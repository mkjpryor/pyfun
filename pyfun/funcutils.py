"""
This module provides utilities for manipulating functions

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools, inspect
from inspect import Parameter as P

from multipledispatch.core import ismethod
from multipledispatch.dispatcher import Dispatcher, MethodDispatcher


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


def auto_bind(f):
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
    return auto_bind_n(n_args(f), f)    


def auto_bind_n(n, f = None, bound = ()):
    """
    Returns a decorator that automatically binds `n` **positional** arguments of `f`
    
    If `f` is not given, this function returns a function that can be used as a decorator
    
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


def generic(f):
    """
    Decorator that marks the decorated function as generic, and allows implementations
    to be registered for particular types
    
    The returned function cannot be invoked directly - the correct function should
    be obtained by using the resolve method and passing the required type
    
    The decorated function is used as the implementation for object, i.e. the implementation
    that will be used if no specific implementations are registered for a type
    
    >>> from collections import Iterable
    >>> @generic
    ... def func(): pass
    ...
    >>> @func.register(int)
    ... def func_int(): return "INT"
    ...
    >>> @func.register(Iterable)
    ... def func_iter(): return "ITERABLE"
    ...
    >>> @func.register(list)
    ... def func_list(): return "LIST"
    >>> func()
    Traceback (most recent call last):
        ...
    RuntimeError: Generic functions cannot be invoked directly
    >>> func.resolve(int)()
    'INT'
    >>> func.resolve(tuple)()
    'ITERABLE'
    >>> func.resolve(str)()
    'ITERABLE'
    >>> func.resolve(list)()
    'LIST'
    >>> func.resolve(float)
    Traceback (most recent call last):
        ...
    RuntimeError: No implementation registered for (float)
    """
    # If the function is called directly, we want to tell people to use resolve
    def raise_generic_error(*args, **kwargs):
        raise RuntimeError('Generic functions cannot be invoked directly')
    # We want to utilise all the effort that has gone into the dispatch algorithm
    # of the multipledispatch package
    dispatcher = MethodDispatcher(f.__name__) if ismethod(f) else Dispatcher(f.__name__)
    # Use the register implementation directly and rename dispatch to resolve
    raise_generic_error.register = dispatcher.register
    # We want to issue our own error on failed resolve, rather than talking about signature
    def resolve_for_types(*types):
        impl = dispatcher.dispatch(*types)
        if not impl:
            raise RuntimeError(
                'No implementation registered for (%s)' % ', '.join(t.__name__ for t in types))
        return impl
    raise_generic_error.resolve  = resolve_for_types
    # Make the wrapper function look like the wrapped function before returning it
    functools.update_wrapper(raise_generic_error, f)
    return raise_generic_error


def multipledispatch(f):
    """
    Returns a new function that performs multiple dispatch based on the types given in the
    parameter annotations
    
    Implementations are registered using the register method of the returned callable
    
    The decorated function is used as the default implementation if there are no other
    matches, regardless of annotations
    
    Multiple dispatch can only be used on functions with *no optional or keyword arguments*
    
    >>> @multipledispatch
    ... def add(a, b, *others): pass
    ...
    Traceback (most recent call last):
        ...
    ValueError: Multiple dispatch not allowed with optional or keyword arguments
    >>> @multipledispatch
    ... def add(a, b, c): raise TypeError('No implementation for %s' % type(a).__name__)
    ...
    >>> @add.register
    ... def add_int(a: int, b: int, c: int) -> int: return a + b + c
    ...
    >>> @add.register
    ... def add_str(a: str, b: str, c: str) -> str: return a + b + c
    ...
    >>> add(1, 2, 3)
    6
    >>> add("1", "2", "3")
    '123'
    >>> add(1.0, 2.0, 3.0)
    Traceback (most recent call last):
        ...
    TypeError: No implementation for float
    """
    # If f has any optional or keyword arguments, raise an error
    for p in inspect.signature(f).parameters.values():
        if p.kind == P.POSITIONAL_OR_KEYWORD and p.default is P.empty:
            continue
        raise ValueError('Multiple dispatch not allowed with optional or keyword arguments')
    # Get an appropriate dispatcher
    dispatcher = MethodDispatcher(f.__name__) if ismethod(f) else Dispatcher(f.__name__)
    # Return a function that attempts to use the dispatcher, falling back on f
    def dispatch_with_fallback(*args, **kwargs):
        try:
            return dispatcher(*args, **kwargs)
        except NotImplementedError:
            return f(*args, **kwargs)
    # When registering, we want to use the annotations
    def register_with_annotations(impl):
        # Construct the types array by inspecting the annotations
        types = []
        for p in inspect.signature(impl).parameters.values():
            # Just like f, if impl has any optional or keyword arguments, raise an error
            if not __is_required_positional(p):
                raise ValueError('Multiple dispatch not allowed with optional or keyword arguments')
            # If there is no annotation, use object as the type
            if p.annotation is P.empty:
                types.append(object)
            # If the annotation is not a type, raise an error
            elif not isinstance(p.annotation, type):
                raise TypeError('Multiple dispatch expects annotations to be types')
            # Otherwise, use the annotated type
            else:
                types.append(p.annotation)
        dispatcher.register(*types)(impl)
    dispatch_with_fallback.register = register_with_annotations
    # When resolving, we want to use f as a fallback case
    def resolve_with_fallback(*types):
        return dispatcher.dispatch(*types) or f
    dispatch_with_fallback.resolve  = resolve_with_fallback
    # Add a default property that returns f
    dispatch_with_fallback.default = f
    # Make the returned function look like f
    functools.update_wrapper(dispatch_with_fallback, f)
    return dispatch_with_fallback


def infix(f):
    """
    Allows a function of two arguments to be used as an infix function
    
    For example:
    
    >>> @infix
    ... def add(a, b): return a + b
    ...
    >>> add(1, 2)
    3
    >>> 1 %add% 2
    3
    """
    def start_infix(_, other):
        # When the infix expression is started, return a new object that
        # knows how to finish the expression
        g = functools.partial(f, other)
        return type('', (object,), { '__mod__' : lambda _, x: g(x) })()
    # Return an object that knows how to start the infix expression
    # It can also be called directly
    ifix = type('', (object,), {
        '__rmod__' : start_infix,
        '__call__' : lambda _, *args, **kwargs: f(*args, **kwargs)
    })()
    # Make it look like f for any future decorators
    functools.update_wrapper(ifix, f)
    return ifix
