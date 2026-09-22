# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/GetEntityBounds.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GetEntityBounds_Request(type):
    """Metaclass of message 'GetEntityBounds_Request'."""

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
                'simulation_interfaces.srv.GetEntityBounds_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_entity_bounds__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_entity_bounds__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_entity_bounds__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_entity_bounds__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_entity_bounds__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GetEntityBounds_Request(metaclass=Metaclass_GetEntityBounds_Request):
    """Message class 'GetEntityBounds_Request'."""

    __slots__ = [
        '_entity',
    ]

    _fields_and_field_types = {
        'entity': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.entity = kwargs.get('entity', str())

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
        if self.entity != other.entity:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def entity(self):
        """Message field 'entity'."""
        return self._entity

    @entity.setter
    def entity(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'entity' field must be of type 'str'"
        self._entity = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GetEntityBounds_Response(type):
    """Metaclass of message 'GetEntityBounds_Response'."""

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
                'simulation_interfaces.srv.GetEntityBounds_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_entity_bounds__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_entity_bounds__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_entity_bounds__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_entity_bounds__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_entity_bounds__response

            from simulation_interfaces.msg import Bounds
            if Bounds.__class__._TYPE_SUPPORT is None:
                Bounds.__class__.__import_type_support__()

            from simulation_interfaces.msg import Result
            if Result.__class__._TYPE_SUPPORT is None:
                Result.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GetEntityBounds_Response(metaclass=Metaclass_GetEntityBounds_Response):
    """Message class 'GetEntityBounds_Response'."""

    __slots__ = [
        '_result',
        '_bounds',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
        'bounds': 'simulation_interfaces/Bounds',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Bounds'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import Result
        self.result = kwargs.get('result', Result())
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
        if self.result != other.result:
            return False
        if self.bounds != other.bounds:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def result(self):
        """Message field 'result'."""
        return self._result

    @result.setter
    def result(self, value):
        if __debug__:
            from simulation_interfaces.msg import Result
            assert \
                isinstance(value, Result), \
                "The 'result' field must be a sub message of type 'Result'"
        self._result = value

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


class Metaclass_GetEntityBounds(type):
    """Metaclass of service 'GetEntityBounds'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('simulation_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'simulation_interfaces.srv.GetEntityBounds')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__get_entity_bounds

            from simulation_interfaces.srv import _get_entity_bounds
            if _get_entity_bounds.Metaclass_GetEntityBounds_Request._TYPE_SUPPORT is None:
                _get_entity_bounds.Metaclass_GetEntityBounds_Request.__import_type_support__()
            if _get_entity_bounds.Metaclass_GetEntityBounds_Response._TYPE_SUPPORT is None:
                _get_entity_bounds.Metaclass_GetEntityBounds_Response.__import_type_support__()


class GetEntityBounds(metaclass=Metaclass_GetEntityBounds):
    from simulation_interfaces.srv._get_entity_bounds import GetEntityBounds_Request as Request
    from simulation_interfaces.srv._get_entity_bounds import GetEntityBounds_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
