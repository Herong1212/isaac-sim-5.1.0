# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/LoadWorld.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_LoadWorld_Request(type):
    """Metaclass of message 'LoadWorld_Request'."""

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
                'simulation_interfaces.srv.LoadWorld_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__load_world__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__load_world__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__load_world__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__load_world__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__load_world__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class LoadWorld_Request(metaclass=Metaclass_LoadWorld_Request):
    """Message class 'LoadWorld_Request'."""

    __slots__ = [
        '_uri',
        '_resource_string',
        '_fail_on_unsupported_element',
        '_ignore_missing_or_unsupported_assets',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'uri': 'string',
        'resource_string': 'string',
        'fail_on_unsupported_element': 'boolean',
        'ignore_missing_or_unsupported_assets': 'boolean',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
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
        self.uri = kwargs.get('uri', str())
        self.resource_string = kwargs.get('resource_string', str())
        self.fail_on_unsupported_element = kwargs.get('fail_on_unsupported_element', bool())
        self.ignore_missing_or_unsupported_assets = kwargs.get('ignore_missing_or_unsupported_assets', bool())

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
        if self.uri != other.uri:
            return False
        if self.resource_string != other.resource_string:
            return False
        if self.fail_on_unsupported_element != other.fail_on_unsupported_element:
            return False
        if self.ignore_missing_or_unsupported_assets != other.ignore_missing_or_unsupported_assets:
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
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'uri' field must be of type 'str'"
        self._uri = value

    @builtins.property
    def resource_string(self):
        """Message field 'resource_string'."""
        return self._resource_string

    @resource_string.setter
    def resource_string(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'resource_string' field must be of type 'str'"
        self._resource_string = value

    @builtins.property
    def fail_on_unsupported_element(self):
        """Message field 'fail_on_unsupported_element'."""
        return self._fail_on_unsupported_element

    @fail_on_unsupported_element.setter
    def fail_on_unsupported_element(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'fail_on_unsupported_element' field must be of type 'bool'"
        self._fail_on_unsupported_element = value

    @builtins.property
    def ignore_missing_or_unsupported_assets(self):
        """Message field 'ignore_missing_or_unsupported_assets'."""
        return self._ignore_missing_or_unsupported_assets

    @ignore_missing_or_unsupported_assets.setter
    def ignore_missing_or_unsupported_assets(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'ignore_missing_or_unsupported_assets' field must be of type 'bool'"
        self._ignore_missing_or_unsupported_assets = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_LoadWorld_Response(type):
    """Metaclass of message 'LoadWorld_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'UNSUPPORTED_FORMAT': 101,
        'NO_RESOURCE': 102,
        'RESOURCE_PARSE_ERROR': 103,
        'MISSING_ASSETS': 104,
        'UNSUPPORTED_ASSETS': 105,
        'UNSUPPORTED_ELEMENTS': 106,
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
                'simulation_interfaces.srv.LoadWorld_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__load_world__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__load_world__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__load_world__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__load_world__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__load_world__response

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
            'UNSUPPORTED_FORMAT': cls.__constants['UNSUPPORTED_FORMAT'],
            'NO_RESOURCE': cls.__constants['NO_RESOURCE'],
            'RESOURCE_PARSE_ERROR': cls.__constants['RESOURCE_PARSE_ERROR'],
            'MISSING_ASSETS': cls.__constants['MISSING_ASSETS'],
            'UNSUPPORTED_ASSETS': cls.__constants['UNSUPPORTED_ASSETS'],
            'UNSUPPORTED_ELEMENTS': cls.__constants['UNSUPPORTED_ELEMENTS'],
        }

    @property
    def UNSUPPORTED_FORMAT(self):
        """Message constant 'UNSUPPORTED_FORMAT'."""
        return Metaclass_LoadWorld_Response.__constants['UNSUPPORTED_FORMAT']

    @property
    def NO_RESOURCE(self):
        """Message constant 'NO_RESOURCE'."""
        return Metaclass_LoadWorld_Response.__constants['NO_RESOURCE']

    @property
    def RESOURCE_PARSE_ERROR(self):
        """Message constant 'RESOURCE_PARSE_ERROR'."""
        return Metaclass_LoadWorld_Response.__constants['RESOURCE_PARSE_ERROR']

    @property
    def MISSING_ASSETS(self):
        """Message constant 'MISSING_ASSETS'."""
        return Metaclass_LoadWorld_Response.__constants['MISSING_ASSETS']

    @property
    def UNSUPPORTED_ASSETS(self):
        """Message constant 'UNSUPPORTED_ASSETS'."""
        return Metaclass_LoadWorld_Response.__constants['UNSUPPORTED_ASSETS']

    @property
    def UNSUPPORTED_ELEMENTS(self):
        """Message constant 'UNSUPPORTED_ELEMENTS'."""
        return Metaclass_LoadWorld_Response.__constants['UNSUPPORTED_ELEMENTS']


class LoadWorld_Response(metaclass=Metaclass_LoadWorld_Response):
    """
    Message class 'LoadWorld_Response'.

    Constants:
      UNSUPPORTED_FORMAT
      NO_RESOURCE
      RESOURCE_PARSE_ERROR
      MISSING_ASSETS
      UNSUPPORTED_ASSETS
      UNSUPPORTED_ELEMENTS
    """

    __slots__ = [
        '_result',
        '_world',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
        'world': 'simulation_interfaces/WorldResource',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'WorldResource'),  # noqa: E501
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
        from simulation_interfaces.msg import WorldResource
        self.world = kwargs.get('world', WorldResource())

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
        if self._check_fields:
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
        if self._check_fields:
            from simulation_interfaces.msg import WorldResource
            assert \
                isinstance(value, WorldResource), \
                "The 'world' field must be a sub message of type 'WorldResource'"
        self._world = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_LoadWorld_Event(type):
    """Metaclass of message 'LoadWorld_Event'."""

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
                'simulation_interfaces.srv.LoadWorld_Event')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__load_world__event
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__load_world__event
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__load_world__event
            cls._TYPE_SUPPORT = module.type_support_msg__srv__load_world__event
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__load_world__event

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


class LoadWorld_Event(metaclass=Metaclass_LoadWorld_Event):
    """Message class 'LoadWorld_Event'."""

    __slots__ = [
        '_info',
        '_request',
        '_response',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'info': 'service_msgs/ServiceEventInfo',
        'request': 'sequence<simulation_interfaces/LoadWorld_Request, 1>',
        'response': 'sequence<simulation_interfaces/LoadWorld_Response, 1>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['service_msgs', 'msg'], 'ServiceEventInfo'),  # noqa: E501
        rosidl_parser.definition.BoundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'srv'], 'LoadWorld_Request'), 1),  # noqa: E501
        rosidl_parser.definition.BoundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'srv'], 'LoadWorld_Response'), 1),  # noqa: E501
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
            from simulation_interfaces.srv import LoadWorld_Request
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
                 all(isinstance(v, LoadWorld_Request) for v in value) and
                 True), \
                "The 'request' field must be a set or sequence with length <= 1 and each value of type 'LoadWorld_Request'"
        self._request = value

    @builtins.property
    def response(self):
        """Message field 'response'."""
        return self._response

    @response.setter
    def response(self, value):
        if self._check_fields:
            from simulation_interfaces.srv import LoadWorld_Response
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
                 all(isinstance(v, LoadWorld_Response) for v in value) and
                 True), \
                "The 'response' field must be a set or sequence with length <= 1 and each value of type 'LoadWorld_Response'"
        self._response = value


class Metaclass_LoadWorld(type):
    """Metaclass of service 'LoadWorld'."""

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
                'simulation_interfaces.srv.LoadWorld')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__load_world

            from simulation_interfaces.srv import _load_world
            if _load_world.Metaclass_LoadWorld_Request._TYPE_SUPPORT is None:
                _load_world.Metaclass_LoadWorld_Request.__import_type_support__()
            if _load_world.Metaclass_LoadWorld_Response._TYPE_SUPPORT is None:
                _load_world.Metaclass_LoadWorld_Response.__import_type_support__()
            if _load_world.Metaclass_LoadWorld_Event._TYPE_SUPPORT is None:
                _load_world.Metaclass_LoadWorld_Event.__import_type_support__()


class LoadWorld(metaclass=Metaclass_LoadWorld):
    from simulation_interfaces.srv._load_world import LoadWorld_Request as Request
    from simulation_interfaces.srv._load_world import LoadWorld_Response as Response
    from simulation_interfaces.srv._load_world import LoadWorld_Event as Event

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
