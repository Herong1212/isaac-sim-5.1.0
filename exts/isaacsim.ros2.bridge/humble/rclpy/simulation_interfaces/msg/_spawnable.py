# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:msg/Spawnable.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Spawnable(type):
    """Metaclass of message 'Spawnable'."""

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
                'simulation_interfaces.msg.Spawnable')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__spawnable
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__spawnable
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__spawnable
            cls._TYPE_SUPPORT = module.type_support_msg__msg__spawnable
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__spawnable

            from simulation_interfaces.msg import Bounds
            if Bounds.__class__._TYPE_SUPPORT is None:
                Bounds.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Spawnable(metaclass=Metaclass_Spawnable):
    """Message class 'Spawnable'."""

    __slots__ = [
        '_uri',
        '_description',
        '_spawn_bounds',
    ]

    _fields_and_field_types = {
        'uri': 'string',
        'description': 'string',
        'spawn_bounds': 'simulation_interfaces/Bounds',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Bounds'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.uri = kwargs.get('uri', str())
        self.description = kwargs.get('description', str())
        from simulation_interfaces.msg import Bounds
        self.spawn_bounds = kwargs.get('spawn_bounds', Bounds())

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
        if self.uri != other.uri:
            return False
        if self.description != other.description:
            return False
        if self.spawn_bounds != other.spawn_bounds:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def uri(self):
        """Message field 'uri'."""
        return self._uri

    @uri.setter
    def uri(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'uri' field must be of type 'str'"
        self._uri = value

    @builtins.property
    def description(self):
        """Message field 'description'."""
        return self._description

    @description.setter
    def description(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'description' field must be of type 'str'"
        self._description = value

    @builtins.property
    def spawn_bounds(self):
        """Message field 'spawn_bounds'."""
        return self._spawn_bounds

    @spawn_bounds.setter
    def spawn_bounds(self, value):
        if __debug__:
            from simulation_interfaces.msg import Bounds
            assert \
                isinstance(value, Bounds), \
                "The 'spawn_bounds' field must be a sub message of type 'Bounds'"
        self._spawn_bounds = value
