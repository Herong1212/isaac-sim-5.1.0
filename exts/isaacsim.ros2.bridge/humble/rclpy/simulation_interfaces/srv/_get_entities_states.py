# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/GetEntitiesStates.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GetEntitiesStates_Request(type):
    """Metaclass of message 'GetEntitiesStates_Request'."""

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
                'simulation_interfaces.srv.GetEntitiesStates_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_entities_states__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_entities_states__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_entities_states__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_entities_states__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_entities_states__request

            from simulation_interfaces.msg import EntityFilters
            if EntityFilters.__class__._TYPE_SUPPORT is None:
                EntityFilters.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GetEntitiesStates_Request(metaclass=Metaclass_GetEntitiesStates_Request):
    """Message class 'GetEntitiesStates_Request'."""

    __slots__ = [
        '_filters',
    ]

    _fields_and_field_types = {
        'filters': 'simulation_interfaces/EntityFilters',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'EntityFilters'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import EntityFilters
        self.filters = kwargs.get('filters', EntityFilters())

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
        if self.filters != other.filters:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def filters(self):
        """Message field 'filters'."""
        return self._filters

    @filters.setter
    def filters(self, value):
        if __debug__:
            from simulation_interfaces.msg import EntityFilters
            assert \
                isinstance(value, EntityFilters), \
                "The 'filters' field must be a sub message of type 'EntityFilters'"
        self._filters = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GetEntitiesStates_Response(type):
    """Metaclass of message 'GetEntitiesStates_Response'."""

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
                'simulation_interfaces.srv.GetEntitiesStates_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__get_entities_states__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__get_entities_states__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__get_entities_states__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__get_entities_states__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__get_entities_states__response

            from simulation_interfaces.msg import EntityState
            if EntityState.__class__._TYPE_SUPPORT is None:
                EntityState.__class__.__import_type_support__()

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


class GetEntitiesStates_Response(metaclass=Metaclass_GetEntitiesStates_Response):
    """Message class 'GetEntitiesStates_Response'."""

    __slots__ = [
        '_result',
        '_entities',
        '_states',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
        'entities': 'sequence<string>',
        'states': 'sequence<simulation_interfaces/EntityState>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'EntityState')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import Result
        self.result = kwargs.get('result', Result())
        self.entities = kwargs.get('entities', [])
        self.states = kwargs.get('states', [])

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
        if self.entities != other.entities:
            return False
        if self.states != other.states:
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
    def entities(self):
        """Message field 'entities'."""
        return self._entities

    @entities.setter
    def entities(self, value):
        if __debug__:
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
                "The 'entities' field must be a set or sequence and each value of type 'str'"
        self._entities = value

    @builtins.property
    def states(self):
        """Message field 'states'."""
        return self._states

    @states.setter
    def states(self, value):
        if __debug__:
            from simulation_interfaces.msg import EntityState
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
                 all(isinstance(v, EntityState) for v in value) and
                 True), \
                "The 'states' field must be a set or sequence and each value of type 'EntityState'"
        self._states = value


class Metaclass_GetEntitiesStates(type):
    """Metaclass of service 'GetEntitiesStates'."""

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
                'simulation_interfaces.srv.GetEntitiesStates')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__get_entities_states

            from simulation_interfaces.srv import _get_entities_states
            if _get_entities_states.Metaclass_GetEntitiesStates_Request._TYPE_SUPPORT is None:
                _get_entities_states.Metaclass_GetEntitiesStates_Request.__import_type_support__()
            if _get_entities_states.Metaclass_GetEntitiesStates_Response._TYPE_SUPPORT is None:
                _get_entities_states.Metaclass_GetEntitiesStates_Response.__import_type_support__()


class GetEntitiesStates(metaclass=Metaclass_GetEntitiesStates):
    from simulation_interfaces.srv._get_entities_states import GetEntitiesStates_Request as Request
    from simulation_interfaces.srv._get_entities_states import GetEntitiesStates_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
