# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:msg/Result.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Result(type):
    """Metaclass of message 'Result'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'RESULT_FEATURE_UNSUPPORTED': 0,
        'RESULT_OK': 1,
        'RESULT_NOT_FOUND': 2,
        'RESULT_INCORRECT_STATE': 3,
        'RESULT_OPERATION_FAILED': 4,
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
                'simulation_interfaces.msg.Result')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__result
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__result
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__result
            cls._TYPE_SUPPORT = module.type_support_msg__msg__result
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__result

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'RESULT_FEATURE_UNSUPPORTED': cls.__constants['RESULT_FEATURE_UNSUPPORTED'],
            'RESULT_OK': cls.__constants['RESULT_OK'],
            'RESULT_NOT_FOUND': cls.__constants['RESULT_NOT_FOUND'],
            'RESULT_INCORRECT_STATE': cls.__constants['RESULT_INCORRECT_STATE'],
            'RESULT_OPERATION_FAILED': cls.__constants['RESULT_OPERATION_FAILED'],
        }

    @property
    def RESULT_FEATURE_UNSUPPORTED(self):
        """Message constant 'RESULT_FEATURE_UNSUPPORTED'."""
        return Metaclass_Result.__constants['RESULT_FEATURE_UNSUPPORTED']

    @property
    def RESULT_OK(self):
        """Message constant 'RESULT_OK'."""
        return Metaclass_Result.__constants['RESULT_OK']

    @property
    def RESULT_NOT_FOUND(self):
        """Message constant 'RESULT_NOT_FOUND'."""
        return Metaclass_Result.__constants['RESULT_NOT_FOUND']

    @property
    def RESULT_INCORRECT_STATE(self):
        """Message constant 'RESULT_INCORRECT_STATE'."""
        return Metaclass_Result.__constants['RESULT_INCORRECT_STATE']

    @property
    def RESULT_OPERATION_FAILED(self):
        """Message constant 'RESULT_OPERATION_FAILED'."""
        return Metaclass_Result.__constants['RESULT_OPERATION_FAILED']


class Result(metaclass=Metaclass_Result):
    """
    Message class 'Result'.

    Constants:
      RESULT_FEATURE_UNSUPPORTED
      RESULT_OK
      RESULT_NOT_FOUND
      RESULT_INCORRECT_STATE
      RESULT_OPERATION_FAILED
    """

    __slots__ = [
        '_result',
        '_error_message',
    ]

    _fields_and_field_types = {
        'result': 'uint8',
        'error_message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.result = kwargs.get('result', int())
        self.error_message = kwargs.get('error_message', str())

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
        if self.error_message != other.error_message:
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
            assert \
                isinstance(value, int), \
                "The 'result' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'result' field must be an unsigned integer in [0, 255]"
        self._result = value

    @builtins.property
    def error_message(self):
        """Message field 'error_message'."""
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'error_message' field must be of type 'str'"
        self._error_message = value
