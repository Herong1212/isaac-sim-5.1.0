# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/GetAvailableWorlds.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GetAvailableWorlds_Request(type):
    """Metaclass of message 'GetAvailableWorlds_Request'."""

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
                'simulation_interfaces.srv.GetAvailableWorlds_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_available_worlds__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_available_worlds__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_available_worlds__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_available_worlds__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_available_worlds__request

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


class GetAvailableWorlds_Request(metaclass=Metaclass_GetAvailableWorlds_Request):
    """Message class 'GetAvailableWorlds_Request'."""

    __slots__ = [
        '_additional_sources',
        '_filter',
        '_offline_only',
        '_continue_on_error',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'additional_sources': 'sequence<string>',
        'filter': 'simulation_interfaces/TagsFilter',
        'offline_only': 'boolean',
        'continue_on_error': 'boolean',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'TagsFilter'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
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
        self.additional_sources = kwargs.get('additional_sources', [])
        from simulation_interfaces.msg import TagsFilter
        self.filter = kwargs.get('filter', TagsFilter())
        self.offline_only = kwargs.get('offline_only', bool())
        self.continue_on_error = kwargs.get('continue_on_error', bool())

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
        if self.additional_sources != other.additional_sources:
            return False
        if self.filter != other.filter:
            return False
        if self.offline_only != other.offline_only:
            return False
        if self.continue_on_error != other.continue_on_error:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def additional_sources(self):
        """Message field 'additional_sources'."""
        return self._additional_sources

    @additional_sources.setter
    def additional_sources(self, value):
        if self._check_fields:
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
                 all(isinstance(v, str) for v in value) and
                 True), \
                "The 'additional_sources' field must be a set or sequence and each value of type 'str'"
        self._additional_sources = value

    @builtins.property  # noqa: A003
    def filter(self):  # noqa: A003
        """Message field 'filter'."""
        return self._filter

    @filter.setter  # noqa: A003
    def filter(self, value):  # noqa: A003
        if self._check_fields:
            from simulation_interfaces.msg import TagsFilter
            assert \
                isinstance(value, TagsFilter), \
                "The 'filter' field must be a sub message of type 'TagsFilter'"
        self._filter = value

    @builtins.property
    def offline_only(self):
        """Message field 'offline_only'."""
        return self._offline_only

    @offline_only.setter
    def offline_only(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'offline_only' field must be of type 'bool'"
        self._offline_only = value

    @builtins.property
    def continue_on_error(self):
        """Message field 'continue_on_error'."""
        return self._continue_on_error

    @continue_on_error.setter
    def continue_on_error(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'continue_on_error' field must be of type 'bool'"
        self._continue_on_error = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GetAvailableWorlds_Response(type):
    """Metaclass of message 'GetAvailableWorlds_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'DEFAULT_SOURCES_FAILED': 101,
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
                'simulation_interfaces.srv.GetAvailableWorlds_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_available_worlds__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_available_worlds__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_available_worlds__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_available_worlds__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_available_worlds__response

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
            'DEFAULT_SOURCES_FAILED': cls.__constants['DEFAULT_SOURCES_FAILED'],
        }

    @property
    def DEFAULT_SOURCES_FAILED(self):
        """Message constant 'DEFAULT_SOURCES_FAILED'."""
        return Metaclass_GetAvailableWorlds_Response.__constants['DEFAULT_SOURCES_FAILED']


class GetAvailableWorlds_Response(metaclass=Metaclass_GetAvailableWorlds_Response):
    """
    Message class 'GetAvailableWorlds_Response'.

    Constants:
      DEFAULT_SOURCES_FAILED
    """

    __slots__ = [
        '_result',
        '_worlds',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
        'worlds': 'sequence<simulation_interfaces/WorldResource>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'WorldResource')),  # noqa: E501
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
        self.worlds = kwargs.get('worlds', [])

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
        if self.worlds != other.worlds:
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

    @builtins.property
    def worlds(self):
        """Message field 'worlds'."""
        return self._worlds

    @worlds.setter
    def worlds(self, value):
        if self._check_fields:
            from simulation_interfaces.msg import WorldResource
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
                 all(isinstance(v, WorldResource) for v in value) and
                 True), \
                "The 'worlds' field must be a set or sequence and each value of type 'WorldResource'"
        self._worlds = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GetAvailableWorlds_Event(type):
    """Metaclass of message 'GetAvailableWorlds_Event'."""

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
                'simulation_interfaces.srv.GetAvailableWorlds_Event')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_available_worlds__event
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_available_worlds__event
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_available_worlds__event
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_available_worlds__event
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_available_worlds__event

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


class GetAvailableWorlds_Event(metaclass=Metaclass_GetAvailableWorlds_Event):
    """Message class 'GetAvailableWorlds_Event'."""

    __slots__ = [
        '_info',
        '_request',
        '_response',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'info': 'service_msgs/ServiceEventInfo',
        'request': 'sequence<simulation_interfaces/GetAvailableWorlds_Request, 1>',
        'response': 'sequence<simulation_interfaces/GetAvailableWorlds_Response, 1>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['service_msgs', 'msg'], 'ServiceEventInfo'),  # noqa: E501
        rosidl_parser.definition.BoundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'srv'], 'GetAvailableWorlds_Request'), 1),  # noqa: E501
        rosidl_parser.definition.BoundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'srv'], 'GetAvailableWorlds_Response'), 1),  # noqa: E501
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
            from simulation_interfaces.srv import GetAvailableWorlds_Request
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
                 all(isinstance(v, GetAvailableWorlds_Request) for v in value) and
                 True), \
                "The 'request' field must be a set or sequence with length <= 1 and each value of type 'GetAvailableWorlds_Request'"
        self._request = value

    @builtins.property
    def response(self):
        """Message field 'response'."""
        return self._response

    @response.setter
    def response(self, value):
        if self._check_fields:
            from simulation_interfaces.srv import GetAvailableWorlds_Response
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
                 all(isinstance(v, GetAvailableWorlds_Response) for v in value) and
                 True), \
                "The 'response' field must be a set or sequence with length <= 1 and each value of type 'GetAvailableWorlds_Response'"
        self._response = value


class Metaclass_GetAvailableWorlds(type):
    """Metaclass of service 'GetAvailableWorlds'."""

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
                'simulation_interfaces.srv.GetAvailableWorlds')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__get_available_worlds

            from simulation_interfaces.srv import _get_available_worlds
            if _get_available_worlds.Metaclass_GetAvailableWorlds_Request._TYPE_SUPPORT is None:
                _get_available_worlds.Metaclass_GetAvailableWorlds_Request.__import_type_support__()
            if _get_available_worlds.Metaclass_GetAvailableWorlds_Response._TYPE_SUPPORT is None:
                _get_available_worlds.Metaclass_GetAvailableWorlds_Response.__import_type_support__()
            if _get_available_worlds.Metaclass_GetAvailableWorlds_Event._TYPE_SUPPORT is None:
                _get_available_worlds.Metaclass_GetAvailableWorlds_Event.__import_type_support__()


class GetAvailableWorlds(metaclass=Metaclass_GetAvailableWorlds):
    from simulation_interfaces.srv._get_available_worlds import GetAvailableWorlds_Request as Request
    from simulation_interfaces.srv._get_available_worlds import GetAvailableWorlds_Response as Response
    from simulation_interfaces.srv._get_available_worlds import GetAvailableWorlds_Event as Event

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
