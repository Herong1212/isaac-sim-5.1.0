from __future__ import annotations
import omni.kit.telemetry._telemetry
import typing
import omni.core._core

__all__ = [
    "ITelemetry",
    "ITelemetry2",
    "RunEnvironment"
]


class ITelemetry(_ITelemetry, omni.core._core.IObject):
    """
    Interface to handle performing telemetry related tasks.

     This provides an abstraction over the lower level telemetry and structured logging systems
     and allows control over some common features of it.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def send_custom_event(self, eventType: str, duration: float = 0.0, data1: str = None, data2: str = None, value1: float = 0.0, value2: float = 0.0) -> None: ...
    def send_generic_event(self, event_type: str, duration: float, data1: str, data2: str, value1: float, value2: float) -> None: 
        """
        Sends a generic structured log event with caller specified data.

         @param[in] eventType    A string describing the event that occurred.  There is no
                                 restriction on the content or formatting of this value.
                                 This should neither be ``nullptr`` nor an empty string.
         @param[in] duration     A generic duration value that can be optionally included
                                 with the event.  It is the caller's respsonsibility to
                                 decide on the usage and semantics of this value depending
                                 on the @p eventType value.  This may be 0.0 if no duration
                                 value is needed for the event.
         @param[in] data1        A string data value to be sent with the event.  The contents
                                 and interpretation of this string depend on the @p eventTyoe
                                 value.
         @param[in] data2        A string data value to be sent with the event.  The contents
                                 and interpretation of this string depend on the @p eventTyoe
                                 value.
         @param[in] value1       A floating point value to be sent with the event.  This value
                                 will be interpreted according to the @p eventType value.
         @param[in] value2       A floating point value to be sent with the event.  This value
                                 will be interpreted according to the @p eventType value.

         @returns No return value.

         @remarks This sends a generic event to the structured logging log file.  The contents,
                  semantics, and interpretation of this event are left entirely up to the caller.
                  This will be a no-op if telemetry is disabled (ie: the telemetry module either
                  intentionally was not loaded or failed to load).
        """
    pass
class ITelemetry2(_ITelemetry2, omni.core._core.IObject):
    """
    Interface to handle performing telemetry related tasks.

     This provides an abstraction over the lower level telemetry and structured logging systems
     and allows control over some common features of it.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def send_custom_event(self, eventType: str, duration: float = 0.0, data1: str = None, data2: str = None, value1: float = 0.0, value2: float = 0.0) -> None: ...
    @property
    def cloud_session(self) -> bool:
        """
        :type: bool
        """
    @property
    def cloud_session_id(self) -> str:
        """
        :type: str
        """
    @property
    def customer_id(self) -> str:
        """
        :type: str
        """
    @property
    def run_environment(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class RunEnvironment():
    """
    Names for the current Run environment used for telemetry.

     Identifiers used to outline what kind of environment this process is currently running
     in.  This may be individual (OVI), cloud (OVC), or enterprise (OVE).

    Members:

      UNDETERMINED : The run environment has not been determined yet.

      INDIVIDUAL : Omniverse individual (OVI) desktop session.

      CLOUD : Omniverse Cloud (OVC) session.

      ENTERPRISE : Omniverse Enterprise (OVE) session.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CLOUD: omni.kit.telemetry._telemetry.RunEnvironment # value = <RunEnvironment.CLOUD: 2>
    ENTERPRISE: omni.kit.telemetry._telemetry.RunEnvironment # value = <RunEnvironment.ENTERPRISE: 3>
    INDIVIDUAL: omni.kit.telemetry._telemetry.RunEnvironment # value = <RunEnvironment.INDIVIDUAL: 1>
    UNDETERMINED: omni.kit.telemetry._telemetry.RunEnvironment # value = <RunEnvironment.UNDETERMINED: 0>
    __members__: dict # value = {'UNDETERMINED': <RunEnvironment.UNDETERMINED: 0>, 'INDIVIDUAL': <RunEnvironment.INDIVIDUAL: 1>, 'CLOUD': <RunEnvironment.CLOUD: 2>, 'ENTERPRISE': <RunEnvironment.ENTERPRISE: 3>}
    pass
class _ITelemetry(omni.core._core.IObject):
    pass
class _ITelemetry2(omni.core._core.IObject):
    pass
