# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:msg/EntityFilters.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_EntityFilters(type):
    """Metaclass of message 'EntityFilters'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('simulation_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'simulation_interfaces.msg.EntityFilters')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__entity_filters
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__entity_filters
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__entity_filters
            cls._TYPE_SUPPORT = module.type_support_msg__msg__entity_filters
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__entity_filters

            from simulation_interfaces.msg import Bounds
            if Bounds.__class__._TYPE_SUPPORT is None:
                Bounds.__class__.__import_type_support__()

            from simulation_interfaces.msg import EntityCategory
            if EntityCategory.__class__._TYPE_SUPPORT is None:
                EntityCategory.__class__.__import_type_support__()

            from simulation_interfaces.msg import TagsFilter
            if TagsFilter.__class__._TYPE_SUPPORT is None:
                TagsFilter.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class EntityFilters(metaclass=Metaclass_EntityFilters):
    """Message class 'EntityFilters'."""

    __slots__ = [
        '_filter',
        '_categories',
        '_tags',
        '_bounds',
    ]

    _fields_and_field_types = {
        'filter': 'string',
        'categories': 'sequence<simulation_interfaces/EntityCategory>',
        'tags': 'simulation_interfaces/TagsFilter',
        'bounds': 'simulation_interfaces/Bounds',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'EntityCategory')),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'TagsFilter'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Bounds'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.filter = kwargs.get('filter', str())
        self.categories = kwargs.get('categories', [])
        from simulation_interfaces.msg import TagsFilter
        self.tags = kwargs.get('tags', TagsFilter())
        from simulation_interfaces.msg import Bounds
        self.bounds = kwargs.get('bounds', Bounds())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.filter != other.filter:
            return False
        if self.categories != other.categories:
            return False
        if self.tags != other.tags:
            return False
        if self.bounds != other.bounds:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property  # noqa: A003
    def filter(self):  # noqa: A003
        """Message field 'filter'."""
        return self._filter

    @filter.setter  # noqa: A003
    def filter(self, value):  # noqa: A003
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'filter' field must be of type 'str'"
        self._filter = value

    @builtins.property
    def categories(self):
        """Message field 'categories'."""
        return self._categories

    @categories.setter
    def categories(self, value):
        if __debug__:
            from simulation_interfaces.msg import EntityCategory
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, EntityCategory) for v in value) and
                 True), \
                "The 'categories' field must be a set or sequence and each value of type 'EntityCategory'"
        self._categories = value

    @builtins.property
    def tags(self):
        """Message field 'tags'."""
        return self._tags

    @tags.setter
    def tags(self, value):
        if __debug__:
            from simulation_interfaces.msg import TagsFilter
            assert \
                isinstance(value, TagsFilter), \
                "The 'tags' field must be a sub message of type 'TagsFilter'"
        self._tags = value

    @builtins.property
    def bounds(self):
        """Message field 'bounds'."""
        return self._bounds

    @bounds.setter
    def bounds(self, value):
        if __debug__:
            from simulation_interfaces.msg import Bounds
            assert \
                isinstance(value, Bounds), \
                "The 'bounds' field must be a sub message of type 'Bounds'"
        self._bounds = value
