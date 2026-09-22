# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/ResetSimulation.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ResetSimulation_Request(type):
    """Metaclass of message 'ResetSimulation_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'SCOPE_DEFAULT': 0,
        'SCOPE_TIME': 1,
        'SCOPE_STATE': 2,
        'SCOPE_SPAWNED': 4,
        'SCOPE_ALL': 255,
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
                'simulation_interfaces.srv.ResetSimulation_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__reset_simulation__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__reset_simulation__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__reset_simulation__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__reset_simulation__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__reset_simulation__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'SCOPE_DEFAULT': cls.__constants['SCOPE_DEFAULT'],
            'SCOPE_TIME': cls.__constants['SCOPE_TIME'],
            'SCOPE_STATE': cls.__constants['SCOPE_STATE'],
            'SCOPE_SPAWNED': cls.__constants['SCOPE_SPAWNED'],
            'SCOPE_ALL': cls.__constants['SCOPE_ALL'],
        }

    @property
    def SCOPE_DEFAULT(self):
        """Message constant 'SCOPE_DEFAULT'."""
        return Metaclass_ResetSimulation_Request.__constants['SCOPE_DEFAULT']

    @property
    def SCOPE_TIME(self):
        """Message constant 'SCOPE_TIME'."""
        return Metaclass_ResetSimulation_Request.__constants['SCOPE_TIME']

    @property
    def SCOPE_STATE(self):
        """Message constant 'SCOPE_STATE'."""
        return Metaclass_ResetSimulation_Request.__constants['SCOPE_STATE']

    @property
    def SCOPE_SPAWNED(self):
        """Message constant 'SCOPE_SPAWNED'."""
        return Metaclass_ResetSimulation_Request.__constants['SCOPE_SPAWNED']

    @property
    def SCOPE_ALL(self):
        """Message constant 'SCOPE_ALL'."""
        return Metaclass_ResetSimulation_Request.__constants['SCOPE_ALL']


class ResetSimulation_Request(metaclass=Metaclass_ResetSimulation_Request):
    """
    Message class 'ResetSimulation_Request'.

    Constants:
      SCOPE_DEFAULT
      SCOPE_TIME
      SCOPE_STATE
      SCOPE_SPAWNED
      SCOPE_ALL
    """

    __slots__ = [
        '_scope',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'scope': 'uint8',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.scope = kwargs.get('scope', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
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
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.scope != other.scope:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def scope(self):
        """Message field 'scope'."""
        return self._scope

    @scope.setter
    def scope(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'scope' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'scope' field must be an unsigned integer in [0, 255]"
        self._scope = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ResetSimulation_Response(type):
    """Metaclass of message 'ResetSimulation_Response'."""

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
                'simulation_interfaces.srv.ResetSimulation_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__reset_simulation__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__reset_simulation__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__reset_simulation__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__reset_simulation__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__reset_simulation__response

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


class ResetSimulation_Response(metaclass=Metaclass_ResetSimulation_Response):
    """Message class 'ResetSimulation_Response'."""

    __slots__ = [
        '_result',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import Result
        self.result = kwargs.get('result', Result())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
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
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.result != other.result:
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
        if self._check_fields:
            from simulation_interfaces.msg import Result
            assert \
                isinstance(value, Result), \
                "The 'result' field must be a sub message of type 'Result'"
        self._result = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ResetSimulation_Event(type):
    """Metaclass of message 'ResetSimulation_Event'."""

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
                'simulation_interfaces.srv.ResetSimulation_Event')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__reset_simulation__event
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__reset_simulation__event
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__reset_simulation__event
            cls._TYPE_SUPPORT = module.type_support_msg__srv__reset_simulation__event
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__reset_simulation__event

            from service_msgs.msg import ServiceEventInfo
            if ServiceEventInfo.__class__._TYPE_SUPPORT is None:
                ServiceEventInfo.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ResetSimulation_Event(metaclass=Metaclass_ResetSimulation_Event):
    """Message class 'ResetSimulation_Event'."""

    __slots__ = [
        '_info',
        '_request',
        '_response',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'info': 'service_msgs/ServiceEventInfo',
        'request': 'sequence<simulation_interfaces/ResetSimulation_Request, 1>',
        'response': 'sequence<simulation_interfaces/ResetSimulation_Response, 1>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['service_msgs', 'msg'], 'ServiceEventInfo'),  # noqa: E501
        rosidl_parser.definition.BoundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'srv'], 'ResetSimulation_Request'), 1),  # noqa: E501
        rosidl_parser.definition.BoundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'srv'], 'ResetSimulation_Response'), 1),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from service_msgs.msg import ServiceEventInfo
        self.info = kwargs.get('info', ServiceEventInfo())
        self.request = kwargs.get('request', [])
        self.response = kwargs.get('response', [])

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
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
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.info != other.info:
            return False
        if self.request != other.request:
            return False
        if self.response != other.response:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def info(self):
        """Message field 'info'."""
        return self._info

    @info.setter
    def info(self, value):
        if self._check_fields:
            from service_msgs.msg import ServiceEventInfo
            assert \
                isinstance(value, ServiceEventInfo), \
                "The 'info' field must be a sub message of type 'ServiceEventInfo'"
        self._info = value

    @builtins.property
    def request(self):
        """Message field 'request'."""
        return self._request

    @request.setter
    def request(self, value):
        if self._check_fields:
            from simulation_interfaces.srv import ResetSimulation_Request
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
                 len(value) <= 1 and
                 all(isinstance(v, ResetSimulation_Request) for v in value) and
                 True), \
                "The 'request' field must be a set or sequence with length <= 1 and each value of type 'ResetSimulation_Request'"
        self._request = value

    @builtins.property
    def response(self):
        """Message field 'response'."""
        return self._response

    @response.setter
    def response(self, value):
        if self._check_fields:
            from simulation_interfaces.srv import ResetSimulation_Response
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
                 len(value) <= 1 and
                 all(isinstance(v, ResetSimulation_Response) for v in value) and
                 True), \
                "The 'response' field must be a set or sequence with length <= 1 and each value of type 'ResetSimulation_Response'"
        self._response = value


class Metaclass_ResetSimulation(type):
    """Metaclass of service 'ResetSimulation'."""

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
                'simulation_interfaces.srv.ResetSimulation')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__reset_simulation

            from simulation_interfaces.srv import _reset_simulation
            if _reset_simulation.Metaclass_ResetSimulation_Request._TYPE_SUPPORT is None:
                _reset_simulation.Metaclass_ResetSimulation_Request.__import_type_support__()
            if _reset_simulation.Metaclass_ResetSimulation_Response._TYPE_SUPPORT is None:
                _reset_simulation.Metaclass_ResetSimulation_Response.__import_type_support__()
            if _reset_simulation.Metaclass_ResetSimulation_Event._TYPE_SUPPORT is None:
                _reset_simulation.Metaclass_ResetSimulation_Event.__import_type_support__()


class ResetSimulation(metaclass=Metaclass_ResetSimulation):
    from simulation_interfaces.srv._reset_simulation import ResetSimulation_Request as Request
    from simulation_interfaces.srv._reset_simulation import ResetSimulation_Response as Response
    from simulation_interfaces.srv._reset_simulation import ResetSimulation_Event as Event

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
