"""
This module provides utilities for manipulating functions

@author: Matt Pryor <mkjpryor@gmail.com>
"""

import functools, inspect
from itertools import islice
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
    to be registered for a particular type
    
    The returned function cannot be invoked directly - the correct function should
    be obtained by using the resolve method and passing the required type
    
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
    >>> print(func.resolve(float))
    None
    """
    # If the function is called directly, we want to tell people to use resolve
    def raise_generic_error(*args, **kwargs):
        raise RuntimeError('Generic functions cannot be invoked directly')
    # We want to utilise all the effort that has gone into the dispatch algorithm
    # of functools.singledispatch, so use that as our dispatcher
    dispatcher = functools.singledispatch(raise_generic_error)
    raise_generic_error.register = dispatcher.register
    # We want to return None rather than raise_generic_error if no specific implementation
    # is found
    def _dispatch(t):
        impl = dispatcher.dispatch(t)
        return impl if impl is not raise_generic_error else None
    raise_generic_error.resolve = _dispatch
    # Make the wrapper function look like the wrapped function before returning it
    functools.update_wrapper(raise_generic_error, f)
    return raise_generic_error


@auto_bind
def singledispatch(n, f):
    """
    Returns a new function that dispatches to registered implementations based on the
    type of the n-th argument
    
    Implementations are registered using the register method of the returned callable,
    with the type being picked up from the annotation of the argument being dispatched on
    
    f is used as the default implementation if there are no other matches, regardless
    of annotations
    
    Can only be used to dispatch on positional arguments
    
    >>> from collections import Iterable
    >>> @singledispatch(1)
    ... def add(a, b, c): raise TypeError('No implementation for %s' % type(b).__name__)
    ...
    >>> @add.register(int)
    ... def add_int(a: int, b: int, c: int) -> int: return a + b + c
    ...
    >>> @add.register(Iterable)
    ... def add_iter(a: Iterable, b: Iterable, c: Iterable) -> Iterable: return a + b + c
    ...
    >>> add(1, 2, 3)
    6
    >>> add("1", "2", "3")
    '123'
    >>> add((1,), (2,), (3,))
    (1, 2, 3)
    >>> add(1.0, 2.0, 3.0)
    Traceback (most recent call last):
        ...
    TypeError: No implementation for float
    """
    # We want to utilise all the effort that has gone into the dispatch algorithm
    # of functools.singledispatch, so use that as our dispatcher
    dispatcher = functools.singledispatch(f)
    # Return a function that dispatches on the type of the n-th argument
    def dispatch_on_nth(*args, **kwargs):
        return dispatcher.dispatch(type(args[n]))(*args, **kwargs)
    # When registering, we want to use the annotations
    def register_by_annotation(impl):
        # We want to get the annotation of the n-th argument
        annotation = next(islice(inspect.signature(impl).parameters.values(), n, None)).annotation
        # If there is no annotation or the annotation is not a type, raise an error
        if annotation is P.empty:
            raise TypeError('Argument %d must have a type annotation for dispatching' % n)
        elif not isinstance(annotation, type):
            raise TypeError('Annotation for dispatching must be a type')
        # Otherwise, use the annotated type
        dispatcher.register(annotation)(impl)
    dispatch_on_nth.register = register_by_annotation
    dispatch_on_nth.resolve  = dispatcher.dispatch
    # Add a default property that returns f
    dispatch_on_nth.default = f
    # Make the returned function look like f
    functools.update_wrapper(dispatch_on_nth, f)
    return dispatch_on_nth


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
