"""
This module provides some existential types

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from ..types import TypeMeta


class TupleMeta(TypeMeta):
    """
    Metaclass for the Tuple type
    """
    
    def __getitem__(self, types):
        if self.__tupletypes__:
            raise TypeError('Cannot re-parameterise an existing tuple')
        if not isinstance(types, tuple):
            types = (types, )
        if len(types) < 2:
            raise TypeError('Cannot create a tuple of less than 2 types')
        cls = self.__class__(self.__name__, self.__bases__, dict(self.__dict__))
        cls.__tupletypes__ = types
        return cls
    
    def __eq__(self, other):
        if not isinstance(other, TupleMeta):
            return NotImplemented
        return self.__tupletypes__ == other.__tupletypes__
    
    def __hash__(self):
        return hash(self.__tupletypes__)
    
    def __instancecheck__(self, instance):
        if not isinstance(instance, tuple):
            return False
        if not self.__tupletypes__:
            return True
        if len(instance) != len(self.__tupletypes__):
            return False
        return all(isinstance(v, t) for v, t in zip(instance, self.__tupletypes__))
    
    def __subclasscheck__(self, cls):
        # A subclass of tuple is only a subclass of an unparameterised Tuple
        if issubclass(cls, tuple):
            return not self.__tupletypes__
        # We only do further checks for other tuples
        if not isinstance(cls, TupleMeta):
            return super().__subclasscheck(cls)
        # Check each position in cls is a subclass of the corresponding position in self
        if not self.__tupletypes__:
            return True
        if not cls.__tupletypes__:
            return False
        if len(self.__tupletypes__) != len(cls.__tupletypes__):
            return False
        return all(issubclass(t1, t2) for t1, t2 in zip(cls.__tupletypes__, self.__tupletypes__))
    
    def __repr__(self):
        return 'Tuple[%s]' % ', '.join(t.__name__ for t in (self.__tupletypes__ or ()))


class Tuple(metaclass = TupleMeta):
    """
    Parameterisable type for tuples, e.g. Tuple[int, str] means a tuple whose first element is an
    int and whose second element is a string
    """
    __tupletypes__ = None
    