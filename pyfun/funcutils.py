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
