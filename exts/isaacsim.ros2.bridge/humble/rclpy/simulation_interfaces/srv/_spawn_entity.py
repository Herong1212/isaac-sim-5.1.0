# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/SpawnEntity.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SpawnEntity_Request(type):
    """Metaclass of message 'SpawnEntity_Request'."""

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
                'simulation_interfaces.srv.SpawnEntity_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__spawn_entity__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__spawn_entity__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__spawn_entity__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__spawn_entity__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__spawn_entity__request

            from geometry_msgs.msg import PoseStamped
            if PoseStamped.__class__._TYPE_SUPPORT is None:
                PoseStamped.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SpawnEntity_Request(metaclass=Metaclass_SpawnEntity_Request):
    """Message class 'SpawnEntity_Request'."""

    __slots__ = [
        '_name',
        '_allow_renaming',
        '_uri',
        '_resource_string',
        '_entity_namespace',
        '_initial_pose',
    ]

    _fields_and_field_types = {
        'name': 'string',
        'allow_renaming': 'boolean',
        'uri': 'string',
        'resource_string': 'string',
        'entity_namespace': 'string',
        'initial_pose': 'geometry_msgs/PoseStamped',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'PoseStamped'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.name = kwargs.get('name', str())
        self.allow_renaming = kwargs.get('allow_renaming', bool())
        self.uri = kwargs.get('uri', str())
        self.resource_string = kwargs.get('resource_string', str())
        self.entity_namespace = kwargs.get('entity_namespace', str())
        from geometry_msgs.msg import PoseStamped
        self.initial_pose = kwargs.get('initial_pose', PoseStamped())

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
        if self.name != other.name:
            return False
        if self.allow_renaming != other.allow_renaming:
            return False
        if self.uri != other.uri:
            return False
        if self.resource_string != other.resource_string:
            return False
        if self.entity_namespace != other.entity_namespace:
            return False
        if self.initial_pose != other.initial_pose:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def name(self):
        """Message field 'name'."""
        return self._name

    @name.setter
    def name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'name' field must be of type 'str'"
        self._name = value

    @builtins.property
    def allow_renaming(self):
        """Message field 'allow_renaming'."""
        return self._allow_renaming

    @allow_renaming.setter
    def allow_renaming(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'allow_renaming' field must be of type 'bool'"
        self._allow_renaming = value

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
    def resource_string(self):
        """Message field 'resource_string'."""
        return self._resource_string

    @resource_string.setter
    def resource_string(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'resource_string' field must be of type 'str'"
        self._resource_string = value

    @builtins.property
    def entity_namespace(self):
        """Message field 'entity_namespace'."""
        return self._entity_namespace

    @entity_namespace.setter
    def entity_namespace(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'entity_namespace' field must be of type 'str'"
        self._entity_namespace = value

    @builtins.property
    def initial_pose(self):
        """Message field 'initial_pose'."""
        return self._initial_pose

    @initial_pose.setter
    def initial_pose(self, value):
        if __debug__:
            from geometry_msgs.msg import PoseStamped
            assert \
                isinstance(value, PoseStamped), \
                "The 'initial_pose' field must be a sub message of type 'PoseStamped'"
        self._initial_pose = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_SpawnEntity_Response(type):
    """Metaclass of message 'SpawnEntity_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'NAME_NOT_UNIQUE': 101,
        'NAME_INVALID': 102,
        'UNSUPPORTED_FORMAT': 103,
        'NO_RESOURCE': 104,
        'NAMESPACE_INVALID': 105,
        'RESOURCE_PARSE_ERROR': 106,
        'MISSING_ASSETS': 107,
        'UNSUPPORTED_ASSETS': 108,
        'INVALID_POSE': 109,
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
                'simulation_interfaces.srv.SpawnEntity_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__spawn_entity__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__spawn_entity__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__spawn_entity__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__spawn_entity__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__spawn_entity__response

            from simulation_interfaces.msg import Result
            if Result.__class__._TYPE_SUPPORT is None:
                Result.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'NAME_NOT_UNIQUE': cls.__constants['NAME_NOT_UNIQUE'],
            'NAME_INVALID': cls.__constants['NAME_INVALID'],
            'UNSUPPORTED_FORMAT': cls.__constants['UNSUPPORTED_FORMAT'],
            'NO_RESOURCE': cls.__constants['NO_RESOURCE'],
            'NAMESPACE_INVALID': cls.__constants['NAMESPACE_INVALID'],
            'RESOURCE_PARSE_ERROR': cls.__constants['RESOURCE_PARSE_ERROR'],
            'MISSING_ASSETS': cls.__constants['MISSING_ASSETS'],
            'UNSUPPORTED_ASSETS': cls.__constants['UNSUPPORTED_ASSETS'],
            'INVALID_POSE': cls.__constants['INVALID_POSE'],
        }

    @property
    def NAME_NOT_UNIQUE(self):
        """Message constant 'NAME_NOT_UNIQUE'."""
        return Metaclass_SpawnEntity_Response.__constants['NAME_NOT_UNIQUE']

    @property
    def NAME_INVALID(self):
        """Message constant 'NAME_INVALID'."""
        return Metaclass_SpawnEntity_Response.__constants['NAME_INVALID']

    @property
    def UNSUPPORTED_FORMAT(self):
        """Message constant 'UNSUPPORTED_FORMAT'."""
        return Metaclass_SpawnEntity_Response.__constants['UNSUPPORTED_FORMAT']

    @property
    def NO_RESOURCE(self):
        """Message constant 'NO_RESOURCE'."""
        return Metaclass_SpawnEntity_Response.__constants['NO_RESOURCE']

    @property
    def NAMESPACE_INVALID(self):
        """Message constant 'NAMESPACE_INVALID'."""
        return Metaclass_SpawnEntity_Response.__constants['NAMESPACE_INVALID']

    @property
    def RESOURCE_PARSE_ERROR(self):
        """Message constant 'RESOURCE_PARSE_ERROR'."""
        return Metaclass_SpawnEntity_Response.__constants['RESOURCE_PARSE_ERROR']

    @property
    def MISSING_ASSETS(self):
        """Message constant 'MISSING_ASSETS'."""
        return Metaclass_SpawnEntity_Response.__constants['MISSING_ASSETS']

    @property
    def UNSUPPORTED_ASSETS(self):
        """Message constant 'UNSUPPORTED_ASSETS'."""
        return Metaclass_SpawnEntity_Response.__constants['UNSUPPORTED_ASSETS']

    @property
    def INVALID_POSE(self):
        """Message constant 'INVALID_POSE'."""
        return Metaclass_SpawnEntity_Response.__constants['INVALID_POSE']


class SpawnEntity_Response(metaclass=Metaclass_SpawnEntity_Response):
    """
    Message class 'SpawnEntity_Response'.

    Constants:
      NAME_NOT_UNIQUE
      NAME_INVALID
      UNSUPPORTED_FORMAT
      NO_RESOURCE
      NAMESPACE_INVALID
      RESOURCE_PARSE_ERROR
      MISSING_ASSETS
      UNSUPPORTED_ASSETS
      INVALID_POSE
    """

    __slots__ = [
        '_result',
        '_entity_name',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
        'entity_name': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import Result
        self.result = kwargs.get('result', Result())
        self.entity_name = kwargs.get('entity_name', str())

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
        if self.entity_name != other.entity_name:
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
    def entity_name(self):
        """Message field 'entity_name'."""
        return self._entity_name

    @entity_name.setter
    def entity_name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'entity_name' field must be of type 'str'"
        self._entity_name = value


class Metaclass_SpawnEntity(type):
    """Metaclass of service 'SpawnEntity'."""

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
                'simulation_interfaces.srv.SpawnEntity')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__spawn_entity

            from simulation_interfaces.srv import _spawn_entity
            if _spawn_entity.Metaclass_SpawnEntity_Request._TYPE_SUPPORT is None:
                _spawn_entity.Metaclass_SpawnEntity_Request.__import_type_support__()
            if _spawn_entity.Metaclass_SpawnEntity_Response._TYPE_SUPPORT is None:
                _spawn_entity.Metaclass_SpawnEntity_Response.__import_type_support__()


class SpawnEntity(metaclass=Metaclass_SpawnEntity):
    from simulation_interfaces.srv._spawn_entity import SpawnEntity_Request as Request
    from simulation_interfaces.srv._spawn_entity import SpawnEntity_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
