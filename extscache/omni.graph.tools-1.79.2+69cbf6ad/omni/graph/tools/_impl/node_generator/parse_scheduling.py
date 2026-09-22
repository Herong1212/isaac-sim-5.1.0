"""Support for the parsing and interpretation of scheduling hints in the .ogn file"""

from __future__ import annotations  # For the forward class reference type in compare()

import re
from enum import Enum
from typing import List, Optional, Union

from .utils import IndentedOutput, ParseError


# ======================================================================
class _AccessType(Enum):
    """Access type for a given scheduling flag
    ALL = The data will be both read and written to
    READ = The data will only be read
    WRITE = The data will only be written
    """

    ALL = "ReadWrite"
    READ = "ReadOnly"
    WRITE = "WriteOnly"

    @classmethod
    def flag_access_type(cls, flag_name: str):
        """Returns the type of access the flag name implies"""
        if flag_name.endswith("-read"):
            return cls.READ
        if flag_name.endswith("-write"):
            return cls.WRITE
        return cls.ALL

    @classmethod
    def as_cpp_enum(cls, access_type: _AccessType) -> str:
        """Returns the C++ enum value corresponding to the access type string taken from the class data values"""
        if access_type == cls.READ:
            return "eAccessType::eRead"
        if access_type == cls.WRITE:
            return "eAccessType::eWrite"
        return "eAccessType::eReadWrite"

    @classmethod
    def as_python_enum(cls, access_type: _AccessType) -> str:
        """Returns the Python enum value corresponding to the access type string taken from the class data values"""
        if access_type == cls.READ:
            return "og.eAccessType.E_READ"
        if access_type == cls.WRITE:
            return "og.eAccessType.E_WRITE"
        return "og.eAccessType.E_READ_WRITE"


# ======================================================================
class _ComputeRule(Enum):
    """Compute Rule for the scheduling flag
    DEFAULT = Evaluator default rule
    ON_REQUEST = Compute skipped until INode::onRequest
    """

    DEFAULT = "compute-default"
    ON_REQUEST = "compute-on-request"

    @classmethod
    def flag_compute_rule(cls, flag_name: str):
        """Returns the type of compute-rule the flag name implies"""
        if flag_name == cls.ON_REQUEST.value:
            return cls.ON_REQUEST
        return cls.DEFAULT

    @classmethod
    def as_cpp_enum(cls, compute_rule: _ComputeRule) -> str:
        """Returns the C++ enum value corresponding to the string taken from the class data values"""
        if compute_rule == cls.ON_REQUEST:
            return "eComputeRule::eOnRequest"
        return "eComputeRule::eDefault"

    @classmethod
    def as_python_enum(cls, compute_rule: _ComputeRule) -> str:
        """Returns the Python enum value corresponding to the access type string taken from the class data values"""
        if compute_rule == cls.ON_REQUEST:
            return "og.eComputeRule.E_ON_REQUEST"
        return "og.eComputeRule.E_DEFAULT"


# ======================================================================
# begin-scheduling-hints
class SchedulingHints:
    """Class managing the scheduling hints.
    The keywords are case-independent during parsing, specified in lower case here for easy checking.

    When there is a -read and -write variant only one of them should be specified at a time:
        no suffix: The item in question is accessed for both read and write
        -read suffix: The item in question is accessed only for reading
        -write suffix: The item in question is accessed only for writing

    These class static values list the possible values for the "scheduling" lists in the .ogn file.

    # Set when the node accesses other global data, i.e. data stored outside of the node, including the data
    # on other nodes.
    GLOBAL_DATA = "global"
    GLOBAL_DATA_READ = "global-read"
    GLOBAL_DATA_WRITE = "global-write"

    # Set when a node accesses static data, i.e. data shared among all nodes of the same type
    STATIC_DATA = "static"
    STATIC_DATA_READ = "static-read"
    STATIC_DATA_WRITE = "static-write"

    # Set when the node is a threadsafe function, i.e. it can be scheduled in parallel with any other nodes, including
    # nodes of the same type. This flag is not compatible with the topology hints that aren't read-only.
    THREADSAFE = "threadsafe"

    # Set when the node accesses the graph topology, e.g. connections, attributes, or nodes
    TOPOLOGY = "topology"
    TOPOLOGY_READ = "topology-read"
    TOPOLOGY_WRITE = "topology-write"

    # Set when the node accesses the USD stage data (for read-only, write-only, or both read and write)
    USD = "usd"
    USD_READ = "usd-read"
    USD_WRITE = "usd-write"

    # Set when the scheduling of the node compute may be modified from the evaluator default.
    COMPUTERULE_DEFAULT = "compute-default"
    COMPUTERULE_ON_REQUEST = "compute-on-request"

    # Set when the node author wishes to specify the purity of the computations that a node does.
    # A "pure" node is one that has no side effects in its initialize, compute, and/or release
    # methods (no mutation of data that is shared/can be accessed outside of the node scope, no
    # dependencies on external data apart from its inputs that could influence execution results).
    # In other words, pure nodes are deterministic in that they will always produce the same output
    # attribute values for a given set of input attribute values, and do not access, rely on, or
    # otherwise mutate data external to the node's scope.
    PURE = "pure"
    """

    # end-scheduling-hints
    GLOBAL_DATA = "global"
    GLOBAL_DATA_READ = "global-read"
    GLOBAL_DATA_WRITE = "global-write"
    STATIC_DATA = "static"
    STATIC_DATA_READ = "static-read"
    STATIC_DATA_WRITE = "static-write"
    THREADSAFE = "threadsafe"
    TOPOLOGY = "topology"
    TOPOLOGY_READ = "topology-read"
    TOPOLOGY_WRITE = "topology-write"
    USD = "usd"
    USD_READ = "usd-read"
    USD_WRITE = "usd-write"
    COMPUTERULE_DEFAULT = "compute-default"
    COMPUTERULE_ON_REQUEST = "compute-on-request"
    PURE = "pure"

    def __init__(self, scheduling_hints: Union[List[str], str]):
        """Initialize the scheduling hints from the .ogn description"""
        self.global_data = None
        self.static_data = None
        self.threadsafe = None
        self.topology = None
        self.usd = None
        self.compute_rule = None
        self.pure = None
        self._allowed_tokens = [
            getattr(self, token_name) for token_name in dir(SchedulingHints) if token_name.isupper()
        ]

        if not isinstance(scheduling_hints, list) and not isinstance(scheduling_hints, str):
            raise ParseError("Scheduling hints must be a comma-separated string or a list of strings")
        if isinstance(scheduling_hints, str):
            # This trick allows lists to be delimited by arbitrary combinations of commas and spaces, so that the
            # user doesn't have to remember which one to use
            scheduling_hints = [element for element in re.split(" |, |,", scheduling_hints) if element]
        for hints in scheduling_hints:
            self.set_flag(hints)

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns a string with the set of flags currently set"""
        result = []
        result.append(f"GLOBAL={None if self.global_data is None else self.global_data.value}")
        result.append(f"STATIC={None if self.static_data is None else self.static_data.value}")
        result.append(f"THREADSAFE={False if self.threadsafe is None else self.threadsafe}")
        result.append(f"TOPOLOGY={None if self.topology is None else self.topology.value}")
        result.append(f"USD={None if self.usd is None else self.usd.value}")
        result.append(f'COMPUTE_RULE="{None if self.compute_rule is None else self.compute_rule.value}"')
        result.append(f"PURE={False if self.pure is None else self.pure}")
        return ", ".join(result)

    # --------------------------------------------------------------------------------------------------------------
    def parse_error(self, message: str):
        """Raises a parse error with common information attached to the given message"""
        raise ParseError(f"{message} - [{self}]")

    # --------------------------------------------------------------------------------------------------------------
    def flags_set(self) -> list[str]:
        """Returns the list of flags currently set as flag names"""
        result = [
            self.global_data.value if self.global_data is not None else None,
            self.static_data.value if self.static_data is not None else None,
            self.THREADSAFE if self.threadsafe is not None and self.threadsafe else None,
            self.topology.value if self.topology is not None else None,
            self.usd.value if self.usd is not None else None,
            self.compute_rule.value if self.compute_rule is not None else None,
        ]
        return [flag for flag in result if flag is not None]

    # --------------------------------------------------------------------------------------------------------------
    def set_flag(self, flag_to_set: str):
        """Tries to enable the named flag.
        Raises ParseError if the flag is not legal or not compatible with current flags"""
        flag_to_set = flag_to_set.lower()
        if flag_to_set not in self._allowed_tokens:
            self.parse_error(f"Scheduling flag '{flag_to_set}' not in allowed list {self._allowed_tokens}")

        if flag_to_set == self.THREADSAFE:
            if self.topology not in [None, _AccessType.READ]:
                self.parse_error(
                    f"'{flag_to_set}' scheduling type not compatible with topology data modification flags"
                )
            elif self.pure:
                self.parse_error(
                    f"{flag_to_set} not compatible with {self.PURE} flag due to redundancy; {self.PURE} "
                    "already implies that the node is threadsafe"
                )
            self.threadsafe = True

        elif flag_to_set in [self.USD, self.USD_READ, self.USD_WRITE]:
            if self.usd is not None:
                self.parse_error(f"{flag_to_set} must be the only USD flag set")
            self.usd = _AccessType.flag_access_type(flag_to_set)

        elif flag_to_set in [self.STATIC_DATA, self.STATIC_DATA_READ, self.STATIC_DATA_WRITE]:
            if self.static_data is not None:
                self.parse_error(f"{flag_to_set} must be the only static_data flag set")
            self.static_data = _AccessType.flag_access_type(flag_to_set)

        elif flag_to_set in [self.GLOBAL_DATA, self.GLOBAL_DATA_READ, self.GLOBAL_DATA_WRITE]:
            if self.global_data is not None:
                self.parse_error(f"{flag_to_set} must be the only global data flag set")
            self.global_data = _AccessType.flag_access_type(flag_to_set)

        elif flag_to_set in [self.TOPOLOGY, self.TOPOLOGY_READ, self.TOPOLOGY_WRITE]:
            if self.topology is not None:
                self.parse_error(f"{flag_to_set} must be the only topology flag set")
            if self.threadsafe and flag_to_set != self.TOPOLOGY_READ:
                self.parse_error(f"{flag_to_set} not compatible with {self.THREADSAFE} flag")
            self.topology = _AccessType.flag_access_type(flag_to_set)

        elif flag_to_set in [self.COMPUTERULE_DEFAULT, self.COMPUTERULE_ON_REQUEST]:
            if self.compute_rule is not None:
                self.parse_error(f"{flag_to_set} must be the only compute-rule flag set")
            self.compute_rule = _ComputeRule.flag_compute_rule(flag_to_set)

        elif flag_to_set == self.PURE:
            if self.threadsafe:
                self.parse_error(
                    f"{flag_to_set} not compatible with {self.THREADSAFE} flag due to redundancy; {self.PURE} "
                    "already implies that the node is threadsafe"
                )
            self.pure = True

    # --------------------------------------------------------------------------------------------------------------
    def compare(self, other: SchedulingHints) -> List[str]:
        """Compare this object against another of the same type to see if their flag configurations match.
        If they don't match then a list of differences is returned, otherwise an empty list
        """
        errors = []
        if self.usd != other.usd:
            errors.append(f"usd flag mismatch '{self.usd}' != '{other.usd}'")
        if self.global_data != other.global_data:
            errors.append(f"global_data flag mismatch '{self.global_data}' != '{other.global_data}'")
        if self.topology != other.topology:
            errors.append(f"topology flag mismatch '{self.topology}' != '{other.topology}'")
        if self.static_data != other.static_data:
            errors.append(f"static_data flag mismatch '{self.static_data}' != '{other.static_data}'")
        if self.threadsafe != other.threadsafe:
            errors.append(f"threadsafe flag mismatch '{self.threadsafe}' != '{other.threadsafe}'")
        if self.compute_rule != other.compute_rule:
            errors.append(f"compute-rule flag mismatch '{self.compute_rule}' != '{other.compute_rule}'")
        if self.pure != other.pure:
            errors.append(f"purity-status flag mismatch '{self.pure}' != '{other.pure}'")
        return errors

    # --------------------------------------------------------------------------------------------------------------
    def has_values_set(self) -> bool:
        """Returns True if any of the scheduling hints values have been set"""
        return [
            self.threadsafe,
            self.global_data,
            self.static_data,
            self.topology,
            self.usd,
            self.compute_rule,
            self.pure,
        ] != [None] * 7

    # --------------------------------------------------------------------------------------------------------------
    def cpp_includes_required(self) -> List[str]:
        """Returns a list of files required to be included for the generated C++ code to work"""
        return ["#include <omni/graph/core/ISchedulingHints2.h>"] if self.has_values_set() else []

    # --------------------------------------------------------------------------------------------------------------
    def emit_cpp(self, out: IndentedOutput) -> bool:
        """Write the C++ initialization code to the given output stream, writing nothing if no flags were set.
        Assumes there is a local variable called nodeTypeObj that contains the NodeTypeObj definition.
        Returns True if anything was written.
        """
        if not self.has_values_set():
            return False

        out.write("auto __schedulingInfo = nodeTypeObj.iNodeType->getSchedulingHints(nodeTypeObj);")
        out.write('CARB_ASSERT(__schedulingInfo, "Could not acquire the scheduling hints");')
        out.write("if (__schedulingInfo)")
        if out.indent("{"):
            if self.threadsafe:
                out.write("__schedulingInfo->setThreadSafety(eThreadSafety::eSafe);")
            elif self.threadsafe is not None:
                out.write("__schedulingInfo->setThreadSafety(eThreadSafety::eUnsafe);")
            if self.global_data is not None:
                out.write(
                    "__schedulingInfo->setDataAccess(eAccessLocation::eGlobal,"
                    f" {_AccessType.as_cpp_enum(self.global_data)});"
                )
            if self.static_data is not None:
                out.write(
                    "__schedulingInfo->setDataAccess(eAccessLocation::eStatic,"
                    f" {_AccessType.as_cpp_enum(self.static_data)});"
                )
            if self.topology is not None:
                out.write(
                    "__schedulingInfo->setDataAccess(eAccessLocation::eTopology,"
                    f" {_AccessType.as_cpp_enum(self.topology)});"
                )
            if self.usd is not None:
                out.write(
                    f"__schedulingInfo->setDataAccess(eAccessLocation::eUsd, {_AccessType.as_cpp_enum(self.usd)});"
                )
            if self.compute_rule is not None:
                out.write(f"__schedulingInfo->setComputeRule({_ComputeRule.as_cpp_enum(self.compute_rule)});")
            out.write("auto __schedulingInfo2 = omni::core::cast<ISchedulingHints2>(__schedulingInfo).get();")
            out.write("if (__schedulingInfo2)")
            if out.indent("{"):
                if self.pure:
                    out.write("__schedulingInfo2->setPurityStatus(ePurityStatus::ePure);")
                elif self.pure is not None:
                    out.write("__schedulingInfo2->setPurityStatus(ePurityStatus::eImpure);")
                out.exdent("}")
            out.exdent("}")

        return True

    # --------------------------------------------------------------------------------------------------------------
    def emit_python(self, out: IndentedOutput) -> bool:
        """Write the Python initialization code to the given output stream, writing nothing if no flags were set.
        Assumes there is a local variable called node_type that contains the Py_NodeType definition.
        Returns True if anything was written.
        """
        if not self.has_values_set():
            return False

        out.write("__hints = node_type.get_scheduling_hints()")
        if out.indent("if __hints is not None:"):
            if self.threadsafe:
                out.write("__hints.thread_safety = og.eThreadSafety.E_SAFE")
            elif self.threadsafe is not None:
                out.write("__hints.thread_safety = og.eThreadSafety.E_UNSAFE")
            if self.global_data is not None:
                out.write(
                    "__hints.set_data_access(og.eAccessLocation.E_GLOBAL,"
                    f" {_AccessType.as_python_enum(self.global_data)})"
                )
            if self.static_data is not None:
                out.write(
                    "__hints.set_data_access(og.eAccessLocation.E_STATIC,"
                    f" {_AccessType.as_python_enum(self.static_data)})"
                )
            if self.topology is not None:
                out.write(
                    "__hints.set_data_access(og.eAccessLocation.E_TOPOLOGY,"
                    f" {_AccessType.as_python_enum(self.topology)})"
                )
            if self.usd is not None:
                out.write(f"__hints.set_data_access(og.eAccessLocation.E_USD, {_AccessType.as_python_enum(self.usd)})")
            if self.compute_rule is not None:
                out.write(f"__hints.compute_rule = {_ComputeRule.as_python_enum(self.compute_rule)}")
            if self.pure:
                out.write("__hints.purity_status = og.ePurityStatus.E_PURE")
            elif self.pure is not None:
                out.write("__hints.purity_status = og.ePurityStatus.E_IMPURE")
            out.exdent()

        return True

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def illegal_configurations(cls) -> List[str]:
        """Returns a list of illegal parsing configurations for testing purposes. Keeps the data local"""
        return [
            '{"not": "a list or string"}',
            '["foo"]',  # List with bad values
            '"usd, bar"',  # String with bad values
            '["usd", "usd-read"]',  # Lists with incompatible values
            '["global-write", "global-read"]',
            '["topology", "topology-write"]',
            '["static", "static-read"]',
            '["compute-default", "compute-on-request"]',
            '["pure", "impure"]',
            '["pure", "threadsafe"]',
            '["threadsafe", "pure"]',
        ]

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def legal_configurations(cls) -> List[str]:
        """Returns a list of legal parsing configurations and expected results for testing purposes.
        The data is a list of pairs where the first element is the flags to be set on the scheduling hints
        in the .ogn file (possibly with extra information as needed) and the second element is a SchedulingHints
        object configured with the expected results. It has a compare operation so the test will use that to
        confirm results
        """

        def from_flags(
            global_data: Optional[_AccessType] = None,
            threadsafe: Optional[bool] = None,
            static_data: Optional[_AccessType] = None,
            topology: Optional[_AccessType] = None,
            usd: Optional[_AccessType] = None,
            compute_rule: Optional[_ComputeRule] = None,
            pure: Optional[bool] = None,
        ) -> SchedulingHints:
            """Returns a SchedulingHints object whose flags are set to the ones passed in"""
            scheduling = SchedulingHints([])
            scheduling.global_data = global_data
            scheduling.threadsafe = threadsafe
            scheduling.static_data = static_data
            scheduling.topology = topology
            scheduling.usd = usd
            scheduling.compute_rule = compute_rule
            scheduling.pure = pure
            return scheduling

        return [
            ('"global"', from_flags(global_data=_AccessType.ALL)),
            ('"threadsafe"', from_flags(threadsafe=True)),
            ('"static-read"', from_flags(static_data=_AccessType.READ)),
            ('"topology-write"', from_flags(topology=_AccessType.WRITE)),
            (
                '"usd,global-write,topology-read"',
                from_flags(usd=_AccessType.ALL, global_data=_AccessType.WRITE, topology=_AccessType.READ),
            ),
            (
                '["usd", "global-read", "topology-write"]',
                from_flags(usd=_AccessType.ALL, global_data=_AccessType.READ, topology=_AccessType.WRITE),
            ),
            ('"compute-on-request"', from_flags(compute_rule=_ComputeRule.ON_REQUEST)),
            ('"compute-default"', from_flags(compute_rule=_ComputeRule.DEFAULT)),
            ('"pure"', from_flags(pure=True)),
        ]
