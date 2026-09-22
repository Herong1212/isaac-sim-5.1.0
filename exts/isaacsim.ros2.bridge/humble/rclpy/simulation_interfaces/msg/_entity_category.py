# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:msg/EntityCategory.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_EntityCategory(type):
    """Metaclass of message 'EntityCategory'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'CATEGORY_OBJECT': 0,
        'CATEGORY_ROBOT': 1,
        'CATEGORY_HUMAN': 2,
        'CATEGORY_DYNAMIC_OBJECT': 4,
        'CATEGORY_STATIC_OBJECT': 5,
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
                'simulation_interfaces.msg.EntityCategory')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__entity_category
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__entity_category
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__entity_category
            cls._TYPE_SUPPORT = module.type_support_msg__msg__entity_category
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__entity_category

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'CATEGORY_OBJECT': cls.__constants['CATEGORY_OBJECT'],
            'CATEGORY_ROBOT': cls.__constants['CATEGORY_ROBOT'],
            'CATEGORY_HUMAN': cls.__constants['CATEGORY_HUMAN'],
            'CATEGORY_DYNAMIC_OBJECT': cls.__constants['CATEGORY_DYNAMIC_OBJECT'],
            'CATEGORY_STATIC_OBJECT': cls.__constants['CATEGORY_STATIC_OBJECT'],
        }

    @property
    def CATEGORY_OBJECT(self):
        """Message constant 'CATEGORY_OBJECT'."""
        return Metaclass_EntityCategory.__constants['CATEGORY_OBJECT']

    @property
    def CATEGORY_ROBOT(self):
        """Message constant 'CATEGORY_ROBOT'."""
        return Metaclass_EntityCategory.__constants['CATEGORY_ROBOT']

    @property
    def CATEGORY_HUMAN(self):
        """Message constant 'CATEGORY_HUMAN'."""
        return Metaclass_EntityCategory.__constants['CATEGORY_HUMAN']

    @property
    def CATEGORY_DYNAMIC_OBJECT(self):
        """Message constant 'CATEGORY_DYNAMIC_OBJECT'."""
        return Metaclass_EntityCategory.__constants['CATEGORY_DYNAMIC_OBJECT']

    @property
    def CATEGORY_STATIC_OBJECT(self):
        """Message constant 'CATEGORY_STATIC_OBJECT'."""
        return Metaclass_EntityCategory.__constants['CATEGORY_STATIC_OBJECT']


class EntityCategory(metaclass=Metaclass_EntityCategory):
    """
    Message class 'EntityCategory'.

    Constants:
      CATEGORY_OBJECT
      CATEGORY_ROBOT
      CATEGORY_HUMAN
      CATEGORY_DYNAMIC_OBJECT
      CATEGORY_STATIC_OBJECT
    """

    __slots__ = [
        '_category',
    ]

    _fields_and_field_types = {
        'category': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.category = kwargs.get('category', int())

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
        if self.category != other.category:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def category(self):
        """Message field 'category'."""
        return self._category

    @category.setter
    def category(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'category' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'category' field must be an unsigned integer in [0, 255]"
        self._category = value
