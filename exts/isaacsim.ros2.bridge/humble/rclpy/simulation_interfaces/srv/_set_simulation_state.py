# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:srv/SetSimulationState.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SetSimulationState_Request(type):
    """Metaclass of message 'SetSimulationState_Request'."""

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
                'simulation_interfaces.srv.SetSimulationState_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_simulation_state__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_simulation_state__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_simulation_state__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_simulation_state__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_simulation_state__request

            from simulation_interfaces.msg import SimulationState
            if SimulationState.__class__._TYPE_SUPPORT is None:
                SimulationState.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetSimulationState_Request(metaclass=Metaclass_SetSimulationState_Request):
    """Message class 'SetSimulationState_Request'."""

    __slots__ = [
        '_state',
    ]

    _fields_and_field_types = {
        'state': 'simulation_interfaces/SimulationState',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'SimulationState'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from simulation_interfaces.msg import SimulationState
        self.state = kwargs.get('state', SimulationState())

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
        if self.state != other.state:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def state(self):
        """Message field 'state'."""
        return self._state

    @state.setter
    def state(self, value):
        if __debug__:
            from simulation_interfaces.msg import SimulationState
            assert \
                isinstance(value, SimulationState), \
                "The 'state' field must be a sub message of type 'SimulationState'"
        self._state = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_SetSimulationState_Response(type):
    """Metaclass of message 'SetSimulationState_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'ALREADY_IN_TARGET_STATE': 101,
        'STATE_TRANSITION_ERROR': 102,
        'INCORRECT_TRANSITION': 103,
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
                'simulation_interfaces.srv.SetSimulationState_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_simulation_state__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_simulation_state__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_simulation_state__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_simulation_state__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_simulation_state__response

            from simulation_interfaces.msg import Result
            if Result.__class__._TYPE_SUPPORT is None:
                Result.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'ALREADY_IN_TARGET_STATE': cls.__constants['ALREADY_IN_TARGET_STATE'],
            'STATE_TRANSITION_ERROR': cls.__constants['STATE_TRANSITION_ERROR'],
            'INCORRECT_TRANSITION': cls.__constants['INCORRECT_TRANSITION'],
        }

    @property
    def ALREADY_IN_TARGET_STATE(self):
        """Message constant 'ALREADY_IN_TARGET_STATE'."""
        return Metaclass_SetSimulationState_Response.__constants['ALREADY_IN_TARGET_STATE']

    @property
    def STATE_TRANSITION_ERROR(self):
        """Message constant 'STATE_TRANSITION_ERROR'."""
        return Metaclass_SetSimulationState_Response.__constants['STATE_TRANSITION_ERROR']

    @property
    def INCORRECT_TRANSITION(self):
        """Message constant 'INCORRECT_TRANSITION'."""
        return Metaclass_SetSimulationState_Response.__constants['INCORRECT_TRANSITION']


class SetSimulationState_Response(metaclass=Metaclass_SetSimulationState_Response):
    """
    Message class 'SetSimulationState_Response'.

    Constants:
      ALREADY_IN_TARGET_STATE
      STATE_TRANSITION_ERROR
      INCORRECT_TRANSITION
    """

    __slots__ = [
        '_result',
    ]

    _fields_and_field_types = {
        'result': 'simulation_interfaces/Result',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['simulation_interfaces', 'msg'], 'Result'),  # noqa: E501
    )

    def __init__(self, **kwargs):
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


class Metaclass_SetSimulationState(type):
    """Metaclass of service 'SetSimulationState'."""

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
                'simulation_interfaces.srv.SetSimulationState')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__set_simulation_state

            from simulation_interfaces.srv import _set_simulation_state
            if _set_simulation_state.Metaclass_SetSimulationState_Request._TYPE_SUPPORT is None:
                _set_simulation_state.Metaclass_SetSimulationState_Request.__import_type_support__()
            if _set_simulation_state.Metaclass_SetSimulationState_Response._TYPE_SUPPORT is None:
                _set_simulation_state.Metaclass_SetSimulationState_Response.__import_type_support__()


class SetSimulationState(metaclass=Metaclass_SetSimulationState):
    from simulation_interfaces.srv._set_simulation_state import SetSimulationState_Request as Request
    from simulation_interfaces.srv._set_simulation_state import SetSimulationState_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
