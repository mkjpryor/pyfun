"""
This module provides the monad and monad-plus types and associated operations

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from pyfun.decorators import multipledispatch, auto_bind, infix
from pyfun import applicative


class Monad(applicative.Applicative):
    """
    The monad type
    """
    
    @classmethod
    def __subclasshook__(cls, other):
        """
        Determines whether other is an applicative when using isinstance/issubclass
        """
        return ( flatmap.resolve(other, object) is not flatmap.default() and
                 unit.resolve(other) is not None )


@infix
@auto_bind
@multipledispatch
def flatmap(Ma, f):
    """
    Signature:  Monad M => flatmap :: M a -> (a -> M b) -> M b
    """
    raise TypeError('Unable to locate implementation for %s' % repr(Ma.__class__))

# monad.unit is applicative.unit
unit = applicative.unit


@applicative.ap.register(Monad, Monad)
def ap(Mf, Ma):
    return Mf <<flatmap>> ( lambda f: Ma <<flatmap>> ( lambda a: unit.resolve(Mf.__class__)(f(a))))


#########################################################################################
#########################################################################################


class MonadPlus(Monad, applicative.Alternative):
    """
    The monad-plus type
    """
    
    @classmethod
    def __subclasshook__(cls, other):
        """
        Determines whether other is an applicative when using isinstance/issubclass
        """
        return ( Monad.__subclasshook__(other) and
                 applicative.Alternative.__subclasshook__(other) )


# MonadPlus requires the same functions as Applicative
empty  = applicative.empty
append = applicative.append
