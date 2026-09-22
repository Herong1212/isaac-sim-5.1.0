# generated from rosidl_generator_py/resource/_idl.py.em
# with input from simulation_interfaces:msg/SimulatorFeatures.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'features'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SimulatorFeatures(type):
    """Metaclass of message 'SimulatorFeatures'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'SPAWNING': 0,
        'DELETING': 1,
        'NAMED_POSES': 2,
        'POSE_BOUNDS': 3,
        'ENTITY_TAGS': 4,
        'ENTITY_BOUNDS': 5,
        'ENTITY_BOUNDS_BOX': 6,
        'ENTITY_BOUNDS_CONVEX': 7,
        'ENTITY_CATEGORIES': 8,
        'SPAWNING_RESOURCE_STRING': 9,
        'ENTITY_STATE_GETTING': 10,
        'ENTITY_STATE_SETTING': 11,
        'ENTITY_INFO_GETTING': 12,
        'ENTITY_INFO_SETTING': 13,
        'SPAWNABLES': 14,
        'SIMULATION_RESET': 20,
        'SIMULATION_RESET_TIME': 21,
        'SIMULATION_RESET_STATE': 22,
        'SIMULATION_RESET_SPAWNED': 23,
        'SIMULATION_STATE_GETTING': 24,
        'SIMULATION_STATE_SETTING': 25,
        'SIMULATION_STATE_PAUSE': 26,
        'STEP_SIMULATION_SINGLE': 31,
        'STEP_SIMULATION_MULTIPLE': 32,
        'STEP_SIMULATION_ACTION': 33,
        'WORLD_LOADING': 40,
        'WORLD_RESOURCE_STRING': 41,
        'WORLD_TAGS': 42,
        'WORLD_UNLOADING': 43,
        'WORLD_INFO_GETTING': 44,
        'AVAILABLE_WORLDS': 45,
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
                'simulation_interfaces.msg.SimulatorFeatures')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__simulator_features
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__simulator_features
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__simulator_features
            cls._TYPE_SUPPORT = module.type_support_msg__msg__simulator_features
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__simulator_features

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'SPAWNING': cls.__constants['SPAWNING'],
            'DELETING': cls.__constants['DELETING'],
            'NAMED_POSES': cls.__constants['NAMED_POSES'],
            'POSE_BOUNDS': cls.__constants['POSE_BOUNDS'],
            'ENTITY_TAGS': cls.__constants['ENTITY_TAGS'],
            'ENTITY_BOUNDS': cls.__constants['ENTITY_BOUNDS'],
            'ENTITY_BOUNDS_BOX': cls.__constants['ENTITY_BOUNDS_BOX'],
            'ENTITY_BOUNDS_CONVEX': cls.__constants['ENTITY_BOUNDS_CONVEX'],
            'ENTITY_CATEGORIES': cls.__constants['ENTITY_CATEGORIES'],
            'SPAWNING_RESOURCE_STRING': cls.__constants['SPAWNING_RESOURCE_STRING'],
            'ENTITY_STATE_GETTING': cls.__constants['ENTITY_STATE_GETTING'],
            'ENTITY_STATE_SETTING': cls.__constants['ENTITY_STATE_SETTING'],
            'ENTITY_INFO_GETTING': cls.__constants['ENTITY_INFO_GETTING'],
            'ENTITY_INFO_SETTING': cls.__constants['ENTITY_INFO_SETTING'],
            'SPAWNABLES': cls.__constants['SPAWNABLES'],
            'SIMULATION_RESET': cls.__constants['SIMULATION_RESET'],
            'SIMULATION_RESET_TIME': cls.__constants['SIMULATION_RESET_TIME'],
            'SIMULATION_RESET_STATE': cls.__constants['SIMULATION_RESET_STATE'],
            'SIMULATION_RESET_SPAWNED': cls.__constants['SIMULATION_RESET_SPAWNED'],
            'SIMULATION_STATE_GETTING': cls.__constants['SIMULATION_STATE_GETTING'],
            'SIMULATION_STATE_SETTING': cls.__constants['SIMULATION_STATE_SETTING'],
            'SIMULATION_STATE_PAUSE': cls.__constants['SIMULATION_STATE_PAUSE'],
            'STEP_SIMULATION_SINGLE': cls.__constants['STEP_SIMULATION_SINGLE'],
            'STEP_SIMULATION_MULTIPLE': cls.__constants['STEP_SIMULATION_MULTIPLE'],
            'STEP_SIMULATION_ACTION': cls.__constants['STEP_SIMULATION_ACTION'],
            'WORLD_LOADING': cls.__constants['WORLD_LOADING'],
            'WORLD_RESOURCE_STRING': cls.__constants['WORLD_RESOURCE_STRING'],
            'WORLD_TAGS': cls.__constants['WORLD_TAGS'],
            'WORLD_UNLOADING': cls.__constants['WORLD_UNLOADING'],
            'WORLD_INFO_GETTING': cls.__constants['WORLD_INFO_GETTING'],
            'AVAILABLE_WORLDS': cls.__constants['AVAILABLE_WORLDS'],
        }

    @property
    def SPAWNING(self):
        """Message constant 'SPAWNING'."""
        return Metaclass_SimulatorFeatures.__constants['SPAWNING']

    @property
    def DELETING(self):
        """Message constant 'DELETING'."""
        return Metaclass_SimulatorFeatures.__constants['DELETING']

    @property
    def NAMED_POSES(self):
        """Message constant 'NAMED_POSES'."""
        return Metaclass_SimulatorFeatures.__constants['NAMED_POSES']

    @property
    def POSE_BOUNDS(self):
        """Message constant 'POSE_BOUNDS'."""
        return Metaclass_SimulatorFeatures.__constants['POSE_BOUNDS']

    @property
    def ENTITY_TAGS(self):
        """Message constant 'ENTITY_TAGS'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_TAGS']

    @property
    def ENTITY_BOUNDS(self):
        """Message constant 'ENTITY_BOUNDS'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_BOUNDS']

    @property
    def ENTITY_BOUNDS_BOX(self):
        """Message constant 'ENTITY_BOUNDS_BOX'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_BOUNDS_BOX']

    @property
    def ENTITY_BOUNDS_CONVEX(self):
        """Message constant 'ENTITY_BOUNDS_CONVEX'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_BOUNDS_CONVEX']

    @property
    def ENTITY_CATEGORIES(self):
        """Message constant 'ENTITY_CATEGORIES'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_CATEGORIES']

    @property
    def SPAWNING_RESOURCE_STRING(self):
        """Message constant 'SPAWNING_RESOURCE_STRING'."""
        return Metaclass_SimulatorFeatures.__constants['SPAWNING_RESOURCE_STRING']

    @property
    def ENTITY_STATE_GETTING(self):
        """Message constant 'ENTITY_STATE_GETTING'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_STATE_GETTING']

    @property
    def ENTITY_STATE_SETTING(self):
        """Message constant 'ENTITY_STATE_SETTING'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_STATE_SETTING']

    @property
    def ENTITY_INFO_GETTING(self):
        """Message constant 'ENTITY_INFO_GETTING'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_INFO_GETTING']

    @property
    def ENTITY_INFO_SETTING(self):
        """Message constant 'ENTITY_INFO_SETTING'."""
        return Metaclass_SimulatorFeatures.__constants['ENTITY_INFO_SETTING']

    @property
    def SPAWNABLES(self):
        """Message constant 'SPAWNABLES'."""
        return Metaclass_SimulatorFeatures.__constants['SPAWNABLES']

    @property
    def SIMULATION_RESET(self):
        """Message constant 'SIMULATION_RESET'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_RESET']

    @property
    def SIMULATION_RESET_TIME(self):
        """Message constant 'SIMULATION_RESET_TIME'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_RESET_TIME']

    @property
    def SIMULATION_RESET_STATE(self):
        """Message constant 'SIMULATION_RESET_STATE'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_RESET_STATE']

    @property
    def SIMULATION_RESET_SPAWNED(self):
        """Message constant 'SIMULATION_RESET_SPAWNED'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_RESET_SPAWNED']

    @property
    def SIMULATION_STATE_GETTING(self):
        """Message constant 'SIMULATION_STATE_GETTING'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_STATE_GETTING']

    @property
    def SIMULATION_STATE_SETTING(self):
        """Message constant 'SIMULATION_STATE_SETTING'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_STATE_SETTING']

    @property
    def SIMULATION_STATE_PAUSE(self):
        """Message constant 'SIMULATION_STATE_PAUSE'."""
        return Metaclass_SimulatorFeatures.__constants['SIMULATION_STATE_PAUSE']

    @property
    def STEP_SIMULATION_SINGLE(self):
        """Message constant 'STEP_SIMULATION_SINGLE'."""
        return Metaclass_SimulatorFeatures.__constants['STEP_SIMULATION_SINGLE']

    @property
    def STEP_SIMULATION_MULTIPLE(self):
        """Message constant 'STEP_SIMULATION_MULTIPLE'."""
        return Metaclass_SimulatorFeatures.__constants['STEP_SIMULATION_MULTIPLE']

    @property
    def STEP_SIMULATION_ACTION(self):
        """Message constant 'STEP_SIMULATION_ACTION'."""
        return Metaclass_SimulatorFeatures.__constants['STEP_SIMULATION_ACTION']

    @property
    def WORLD_LOADING(self):
        """Message constant 'WORLD_LOADING'."""
        return Metaclass_SimulatorFeatures.__constants['WORLD_LOADING']

    @property
    def WORLD_RESOURCE_STRING(self):
        """Message constant 'WORLD_RESOURCE_STRING'."""
        return Metaclass_SimulatorFeatures.__constants['WORLD_RESOURCE_STRING']

    @property
    def WORLD_TAGS(self):
        """Message constant 'WORLD_TAGS'."""
        return Metaclass_SimulatorFeatures.__constants['WORLD_TAGS']

    @property
    def WORLD_UNLOADING(self):
        """Message constant 'WORLD_UNLOADING'."""
        return Metaclass_SimulatorFeatures.__constants['WORLD_UNLOADING']

    @property
    def WORLD_INFO_GETTING(self):
        """Message constant 'WORLD_INFO_GETTING'."""
        return Metaclass_SimulatorFeatures.__constants['WORLD_INFO_GETTING']

    @property
    def AVAILABLE_WORLDS(self):
        """Message constant 'AVAILABLE_WORLDS'."""
        return Metaclass_SimulatorFeatures.__constants['AVAILABLE_WORLDS']


class SimulatorFeatures(metaclass=Metaclass_SimulatorFeatures):
    """
    Message class 'SimulatorFeatures'.

    Constants:
      SPAWNING
      DELETING
      NAMED_POSES
      POSE_BOUNDS
      ENTITY_TAGS
      ENTITY_BOUNDS
      ENTITY_BOUNDS_BOX
      ENTITY_BOUNDS_CONVEX
      ENTITY_CATEGORIES
      SPAWNING_RESOURCE_STRING
      ENTITY_STATE_GETTING
      ENTITY_STATE_SETTING
      ENTITY_INFO_GETTING
      ENTITY_INFO_SETTING
      SPAWNABLES
      SIMULATION_RESET
      SIMULATION_RESET_TIME
      SIMULATION_RESET_STATE
      SIMULATION_RESET_SPAWNED
      SIMULATION_STATE_GETTING
      SIMULATION_STATE_SETTING
      SIMULATION_STATE_PAUSE
      STEP_SIMULATION_SINGLE
      STEP_SIMULATION_MULTIPLE
      STEP_SIMULATION_ACTION
      WORLD_LOADING
      WORLD_RESOURCE_STRING
      WORLD_TAGS
      WORLD_UNLOADING
      WORLD_INFO_GETTING
      AVAILABLE_WORLDS
    """

    __slots__ = [
        '_features',
        '_spawn_formats',
        '_custom_info',
    ]

    _fields_and_field_types = {
        'features': 'sequence<uint16>',
        'spawn_formats': 'sequence<string>',
        'custom_info': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint16')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.features = array.array('H', kwargs.get('features', []))
        self.spawn_formats = kwargs.get('spawn_formats', [])
        self.custom_info = kwargs.get('custom_info', str())

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
        if self.features != other.features:
            return False
        if self.spawn_formats != other.spawn_formats:
            return False
        if self.custom_info != other.custom_info:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def features(self):
        """Message field 'features'."""
        return self._features

    @features.setter
    def features(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'H', \
                "The 'features' array.array() must have the type code of 'H'"
            self._features = value
            return
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
                 all(isinstance(v, int) for v in value) and
                 all(val >= 0 and val < 65536 for val in value)), \
                "The 'features' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 65535]"
        self._features = array.array('H', value)

    @builtins.property
    def spawn_formats(self):
        """Message field 'spawn_formats'."""
        return self._spawn_formats

    @spawn_formats.setter
    def spawn_formats(self, value):
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
                "The 'spawn_formats' field must be a set or sequence and each value of type 'str'"
        self._spawn_formats = value

    @builtins.property
    def custom_info(self):
        """Message field 'custom_info'."""
        return self._custom_info

    @custom_info.setter
    def custom_info(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'custom_info' field must be of type 'str'"
        self._custom_info = value
