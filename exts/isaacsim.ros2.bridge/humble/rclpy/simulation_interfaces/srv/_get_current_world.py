# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/GetCurrentWorld.idl
# generated code does not contain a copyright notice


# Import statements for member types

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GetCurrentWorld_Request(type):
    """Metaclass of message 'GetCurrentWorld_Request'."""

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
                'simulation_interfaces.srv.GetCurrentWorld_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_current_world__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_current_world__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_current_world__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_current_world__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_current_world__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GetCurrentWorld_Request(metaclass=Metaclass_GetCurrentWorld_Request):
    """Message class 'GetCurrentWorld_Request'."""

    __slots__ = [
    ]

    _fields_and_field_types = {
    }

    SLOT_TYPES = (
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))

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
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)


# Import statements for member types

import builtins  # noqa: E402, I100

# already imported above
# import rosidl_parser.definition


class Metaclass_GetCurrentWorld_Response(type):
    """Metaclass of message 'GetCurrentWorld_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'NO_WORLD_LOADED': 101,
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
                'simulation_interfaces.srv.GetCurrentWorld_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_current_world__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_current_world__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_current_world__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_current_world__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_current_world__response

            from simulation_interfaces.msg import Result
            if Result.__class__._TYPE_SUPPORT is None:
                Result.__class__.__import_type_support__()

            from simulation_interfaces.msg import WorldResource
            if WorldResource.__class__._TYPE_SUPPORT is None:
                WorldResource.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'NO_WORLD_LOADED': cls.__constants['NO_WORLD_LOADED'],
        }

    @property
    def NO_WORLD_LOADED(self):
        """Message constant 'NO_WORLD_LOADED'."""
        return Metaclass_GetCurrentWorld_Response.__constants['NO_WORLD_LOADED']


class GetCurrentWorld_Response(metaclass=Metaclass_GetCurrentWorld_Response):
    """
    Message class 'GetCurrentWorld_Response'.

    Constants:
      NO_WORLD_LOADED
    """

    __slots__ = [
        '_result',
        '_world',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
        'world': 'simulation_interfaces/WorldResource',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'WorldResource'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import Result
        self.result = kwargs.get('result', Result())
        from simulation_interfaces.msg import WorldResource
        self.world = kwargs.get('world', WorldResource())

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
        if self.world != other.world:
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
    def world(self):
        """Message field 'world'."""
        return self._world

    @world.setter
    def world(self, value):
        if __debug__:
            from simulation_interfaces.msg import WorldResource
            assert \
                isinstance(value, WorldResource), \
                "The 'world' field must be a sub message of type 'WorldResource'"
        self._world = value


class Metaclass_GetCurrentWorld(type):
    """Metaclass of service 'GetCurrentWorld'."""

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
                'simulation_interfaces.srv.GetCurrentWorld')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__get_current_world

            from simulation_interfaces.srv import _get_current_world
            if _get_current_world.Metaclass_GetCurrentWorld_Request._TYPE_SUPPORT is None:
                _get_current_world.Metaclass_GetCurrentWorld_Request.__import_type_support__()
            if _get_current_world.Metaclass_GetCurrentWorld_Response._TYPE_SUPPORT is None:
                _get_current_world.Metaclass_GetCurrentWorld_Response.__import_type_support__()


class GetCurrentWorld(metaclass=Metaclass_GetCurrentWorld):
    from simulation_interfaces.srv._get_current_world import GetCurrentWorld_Request as Request
    from simulation_interfaces.srv._get_current_world import GetCurrentWorld_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
