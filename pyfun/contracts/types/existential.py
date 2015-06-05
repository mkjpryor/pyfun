"""
This module provides some existential types

@author: Matt Pryor <mkjpryor@gmail.com>
"""

from types import MappingProxyType
from collections import Mapping, OrderedDict

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
        uniontypes = []
        strict = True
        for t in types:
            if not strict:
                raise SyntaxError('If an ellipsis is used, it must be the last argument')
            if t is Ellipsis:
                strict = False
                continue
            if not isinstance(t, type):
                raise TypeError('Cannot parameterise tuple with non-type argument')
            uniontypes.append(t)
        if not uniontypes:
            raise TypeError('Cannot create an unparameterised tuple')
        cls = self.__class__(self.__name__, self.__bases__, dict(self.__dict__))
        cls.__tupletypes__ = tuple(uniontypes)
        cls.__strict__ = strict
        return cls
    
    def __eq__(self, other):
        if not isinstance(other, TupleMeta):
            return NotImplemented
        return self.__strict__ == other.__strict__ and self.__tupletypes__ == other.__tupletypes__
    
    def __hash__(self):
        return hash(self.__strict__) ^ hash(self.__tupletypes__)
    
    def __instancecheck__(self, instance):
        if not isinstance(instance, tuple):
            return False
        if not self.__tupletypes__:
            return True
        if self.__strict__ and len(instance) != len(self.__tupletypes__):
            return False
        return all(isinstance(v, t) for v, t in zip(instance, self.__tupletypes__))
    
    def __subclasscheck__(self, cls):
        # A subclass of tuple is only a subclass of an unparameterised Tuple
        if issubclass(cls, tuple):
            return not self.__tupletypes__
        # We only do further checks for other tuples
        if not isinstance(cls, TupleMeta):
            return super().__subclasscheck__(cls)
        # Check each position in cls is a subclass of the corresponding position in self
        if not self.__tupletypes__:
            return True
        if not cls.__tupletypes__:
            return False
        if self.__strict__:
            if not cls.__strict__ or len(self.__tupletypes__) != len(cls.__tupletypes__):
                return False
        return all(issubclass(t1, t2) for t1, t2 in zip(cls.__tupletypes__, self.__tupletypes__))
    
    def __repr__(self):
        def types():
            for t in (self.__tupletypes__ or ()):
                yield t.__name__
            if not self.__strict__:
                yield "..." 
        return 'Tuple[%s]' % ', '.join(types())


class Tuple(metaclass = TupleMeta):
    """
    Parameterisable type for tuples, e.g. Tuple[int, str] means a tuple whose first element is an
    int and whose second element is a string
    """
    __tupletypes__ = None
    __strict__     = True
    
    
class RecordMeta(TypeMeta):
    """
    Metaclass for the Record type
    """
    
    def __getitem__(self, types):
        if self.__recordtypes__:
            raise TypeError('Cannot re-parameterise an existing record')
        if not isinstance(types, tuple):
            types = (types, )
        # Change a tuple of slices into a mapping of keys to types
        recordtypes = OrderedDict()
        strict = True
        for s in types:
            if not strict:
                raise SyntaxError('If an ellipsis is used, it must be the last argument')
            if s is Ellipsis:
                strict = False
                continue
            if not isinstance(s, slice):
                raise SyntaxError('Error in record type specification')
            k = s.start
            t = s.stop
            if not isinstance(t, type):
                raise TypeError('Cannot parameterise record with non-type argument')
            recordtypes[k] = t
        if not recordtypes:
            raise TypeError('Cannot create an unparameterised record')
        cls = self.__class__(self.__name__, self.__bases__, dict(self.__dict__))
        cls.__recordtypes__ = MappingProxyType(recordtypes)
        cls.__strict__ = strict
        return cls
    
    def __eq__(self, other):
        if not isinstance(other, RecordMeta):
            return NotImplemented
        return self.__strict__ == other.__strict and self.__recordtypes__ == other.__recordtypes__
    
    def __hash__(self):
        return hash(self.__strict__) ^ hash(frozenset(self.__recordtypes__.items()))
    
    def __instancecheck__(self, instance):
        if not isinstance(instance, Mapping):
            return False
        if not self.__recordtypes__:
            return True
        if self.__strict__ and len(instance) != len(self.__recordtypes__):
            return False
        try:
            return all(isinstance(instance[k], t) for k, t in self.__recordtypes__.items())
        except LookupError:
            return False
    
    def __subclasscheck__(self, cls):
        # A Mapping is only a subclass of an unparameterised record
        if issubclass(cls, Mapping):
            return not self.__recordtypes__
        # We only do further checks for other record types
        if not isinstance(cls, RecordMeta):
            return super().__subclasscheck__(cls)
        # Check each key in cls is a subclass of the corresponding key in self
        if not self.__recordtypes__:
            return True
        if not cls.__recordtypes__:
            return False
        if self.__strict__:
            if not cls.__strict__ or len(self.__recordtypes__) != len(cls.__recordtypes__):
                return False
        try:
            return all(issubclass(cls.__recordtypes__[k], t) for k, t in self.__recordtypes__.items())
        except LookupError:
            return False
    
    def __repr__(self):
        def types():
            for k, t in (self.__recordtypes__ or {}).items():
                yield "%s: %s" % (k, t.__name__ )
            if not self.__strict__:
                yield "..." 
        return 'Record[%s]' % ', '.join(types())


class Record(metaclass = RecordMeta):
    """
    Parameterisable type for records, e.g. Record['x': int, 'y': str] means a mapping type where
    key 'x' is an int and key 'y' is a string
    
    If an ellipsis (...) is given as the last type argument, that means other keys can be present
    but are not type checked
    """
    __recordtypes__ = None
    __strict__      = True
    
    
class HasAttrsMeta(TypeMeta):
    """
    Metaclass for the HasAttr type
    """
    
    def __getitem__(self, types):
        if self.__attrtypes__:
            raise TypeError('Cannot re-parameterise an existing structural type')
        if not isinstance(types, tuple):
            types = (types, )
        # Change a tuple of slices into a mapping of keys to types
        attrtypes = OrderedDict()
        for s in types:
            if not isinstance(s, slice):
                raise SyntaxError('Error in record type specification')
            k = s.start
            t = s.stop
            if not isinstance(t, type):
                raise TypeError('Cannot parameterise structural type with non-type argument')
            attrtypes[k] = t
        if not attrtypes:
            raise TypeError('Cannot create an unparameterised structural type')
        cls = self.__class__(self.__name__, self.__bases__, dict(self.__dict__))
        cls.__attrtypes__ = MappingProxyType(attrtypes)
        return cls
    
    def __eq__(self, other):
        if not isinstance(other, HasAttrsMeta):
            return NotImplemented
        return self.__attrtypes__ == other.__attrtypes__
    
    def __hash__(self):
        return hash(frozenset(self.__attrtypes__.items()))
    
    def __instancecheck__(self, instance):
        if not self.__attrtypes__:
            return True
        try:
            return all(isinstance(getattr(instance, k), t) for k, t in self.__attrtypes__.items())
        except AttributeError:
            return False
    
    def __subclasscheck__(self, cls):
        # We only do checks for other structural types
        if not isinstance(cls, HasAttrsMeta):
            return super().__subclasscheck__(cls)
        # Check each key in cls is a subclass of the corresponding key in self
        if not self.__attrtypes__:
            return True
        if not cls.__attrtypes__:
            return False
        try:
            return all(issubclass(cls.__attrtypes__[k], t) for k, t in self.__attrtypes__.items())
        except LookupError:
            return False
    
    def __repr__(self):
        return 'HasAttrs[%s]' % ', '.join(
            "%s: %s" % (k, t.__name__ ) for k, t in (self.__attrtypes__ or {}).items()
        )


class HasAttrs(metaclass = HasAttrsMeta):
    """
    Parameterisable type for structural typing, e.g. HasAttrs['x': int, 'y': str] means an object
    that has an attribute x that is an int and an attribute y that is a string
    """
    __attrtypes__ = None
