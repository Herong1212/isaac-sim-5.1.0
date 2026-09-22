"""Python bindings for sending Omniverse structured log events.
Note that this requires python 3.7+ or CPython 3.6 for ordered dictionary support.
"""
from __future__ import annotations
import omni.structuredlog._structuredlog
import typing
import omni.core._core

__all__ = [
    "ALL_SCHEMAS",
    "DEFAULT_LOG_PATH_EVENT",
    "IStructuredLogControl",
    "IStructuredLogControl2",
    "IStructuredLogExtraFields",
    "IStructuredLogFromILog",
    "IStructuredLogFromILog2",
    "IStructuredLogSettings",
    "IStructuredLogSettings2",
    "IdMode",
    "IdType",
    "InvalidEventException",
    "InvalidSchemaException",
    "StructuredLogEvent",
    "UniqueApp",
    "create_launch_guard",
    "register_schema",
    "send_event"
]


class IStructuredLogControl(_IStructuredLogControl, omni.core._core.IObject):
    """
    Structured log state control interface.  This allows for some control over the processing of
     events and log files for the structured log system.  The structured log system's event queue
     can be temporarily stopped if needed or the output log for a schema may be closed.  Each of
     these operations is only temporary as the event queue will be restarted and the log file
     opened when the next event is queued with @ref omni::structuredlog::IStructuredLog::allocEvent().

     This interface object can be acquired either by requesting it from the type factory or
     by casting an @ref omni::structuredlog::IStructuredLog object to this type.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def close_log(self, event: int) -> None: 
        """
        Closes one or more schema's persistently open log file(s).

         @param[in] event   The ID of the event to close the log for.  This may also be
                            @ref omni::structuredlog::kAllSchemas to close all log file for
                            the process.  The log file for the schema that the given event
                            belongs to will be closed.

         @returns No return value.

         @remarks This closes the persistently open log file(s) for one or more schemas.  This
                  operation will effectively be ignored for schemas that were not registered
                  using the @ref omni::structuredlog::fSchemaFlagKeepLogOpen schema flag since those schemas will
                  not leave their logs open.  The named log files will only remain closed until
                  the next attempt to write an event message to it.  It is the responsibility
                  of the host app to ensure no events are written to the effected log file(s)
                  for the duration that the log needs to remain closed.

         @note This call itself is thread safe.  However the log file may be reopened if a
               pending event is processed in the event queue or a new event is sent while
               the calling thread expects the log to remain closed.  It is the caller's
               responsibility to either stop the event queue, disable structured logging, or
               prevent other events from being sent while the log(s) need to remain closed.
        """
    def stop(self) -> None: 
        """
        Stop the structured log event consumer thread.

         @returns No return value.

         @remarks This stops the structured log event processing system.  This will stop the
                  processing thread and flush all pending event messages to the log.  The
                  processing system will be restarted when the next
                  @ref omni::structuredlog::IStructuredLog::allocEvent()
                  call is made to attempt to send a new message.  This call is useful if the
                  structured log plugin needs to be unloaded.  If the processing thread is left
                  running, it will prevent the plugin from being unloaded (or even being attempted
                  to be unloaded).  This can also be used to temporarily disable the structured
                  log system if its not needed or wanted.  If the structured log system needs to
                  be disabled completely, a call to @ref omni::structuredlog::IStructuredLog::setEnabled()
                  using the @ref omni::structuredlog::fEnableFlagAll flag should be made before stopping
                  the event queue.

         @thread_safety This call is thread safe.
        """
    pass
class IStructuredLogControl2(_IStructuredLogControl2, omni.core._core.IObject):
    """
    Interface for the second version of the IStructuredLogControl interface.  This interface
     exposes more functions to control the behavior of the structured logging system.  This
     object can be retrieved directly or by casting the main IStructuredLog interface to this
     type using ``omni::core::ObjectPtr::as<>()``.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def emit_process_lifetime_exit_event(self, reason: str) -> None: 
        """
        Immediately emits the process lifetime exit event for the process.

         @param[in] reason   The reason why the exit event is being emitted.  This can be any text
                             that gives and indication for why an exit is occurring.  This may not
                             be ``nullptr`` and should not be an empty string.

         @returns No return value.

         @remarks This forces the process lifetime exit event to be emitted early for the process.
                  If this is called, it will pre-empt the normal attempt to emit it automatically
                  when ``omni.structuredlog.plugin`` unloads.  This can be used to provide a
                  different reason message for the exit event or to explicitly emit the event in
                  situations where ``omni.structuredlog.plugin`` cannot be properly unloaded (ie:
                  another system leaks or hangs onto a reference to one of the objects from the
                  library).

         @note This should only ever be called when a process shutdown is iminent and cannot be
               cancelled or avoided.  If this is emitted earlier in the process than exit time,
               the analysis of the process' duration could be incorrect.

         @note Calling this will flush the structuredlog queue to ensure the event is flushed to disk
               before the process exits.
        """
    pass
class IStructuredLogExtraFields(_IStructuredLogExtraFields, omni.core._core.IObject):
    """
    Interface to manage extra CloudEvent fields to be included in each emitted message.  This
     allows for fields to be added and removed as needed.  It also allows existing registered
     fields to be enumerated at any given time.  An extra field is a key/value pair that is
     included at the top level of the JSON object for each message that follows.  Only string
     values are allowed for each key.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def set_value(self, field_name: str, value: str, flags: int) -> bool: 
        """
        Adds, modifies, or removes an extra field key/value pair.

         @param[in] fieldName    The name of the field to add, modify or remove.  This may not be
                                 ``nullptr`` or and empty string.  The field name must only contain
                                 alphabetic, numeric, or underscore ASCII characters.  Any
                                 characters outside these will cause the field to not be updated.
                                 Further, this may not be one of the reserved CloudEvent field
                                 names such as "specversion", "data", "time", "source", "session",
                                 "dataschema", "type", or "subject".
         @param[in] value        The new value to set for the requested extra field.  This may be
                                 ``nullptr`` to indicate that the named field should be removed.
                                 The value string may include any characters, but should be limited
                                 to a small number of characters (ideally less than 64 characters).
         @param[in] flags        Flags to control how the new value is added, modified, or removed.
                                 Currently no flags are defined.  This must be set to
                                 @ref omni::structuredlog::fExtraFieldFlagNone.
         @returns ``true`` if the requested extra field is successfully added, modified, or removed.
                  Returns ``false`` if an invalid field name is given, or the operation could not
                  be completed for any reason.

         @remarks This adds, modifies, or removes a registered extra field and value.  Any extra
                  fields that are registered at the time a message is emitted will be added to the
                  message on output.  At least for the first version of this interface it is
                  expected that extra fields be largely static.

         @thread_safety This call is thread safe.
        """
    pass
class IStructuredLogFromILog(_IStructuredLogFromILog, omni.core._core.IObject):
    """
    This interface controls the ability to send Carbonite and Omniverse logging through the
     structured log system. The output is equivalent to the standard logging output, except that it
     is in JSON, so it will be easier for programs to consume.

     The default state of structured log logging is off, but it can be enabled by calling
     @ref omni::structuredlog::IStructuredLogFromILog::enableLogging() or setting ``/structuredLog/enableLogConsumer``
     to true with ISettings.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def disable_logging(self) -> None: 
        """
        Disables the structured log logger.
         @remarks After this is called, log messages will no longer be sent as structured log
                  events to the structured log system's log file.
        """
    def enable_logging(self) -> None: 
        """
        Enable the structured log logger.
         @remarks Enabling this will result in all Carbonite logging (e.g. CARB_LOG_*) and all
                  Omniverse logging (e.g. OMNI_LOG_*) going to the structured log log file.
                  This may be useful if you want the logs to be consumed by some sort of log reader
                  program.
                  These log events will be sent to the default structured log system's log file if
                  there is one; they will otherwise go to a log file named
                  "omni.structuredlog.logging-{version}".
                  These log events will not be sent to the collection servers.
        """
    @property
    def logging_event_id(self) -> int:
        """
        :type: int
        """
    pass
class IStructuredLogFromILog2(_IStructuredLogFromILog2, omni.core._core.IObject):
    """
    This extends the functionality of the @ref omni::structuredlog::IStructuredLogFromILog
     interface.  This allows for the event flags of the log consumer event to be modified.  This
     is an internal interface however and is not intended to be used externally.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def set_logging_event_flags(self, set_flags: int, clear_flags: int) -> bool: 
        """
        Modifies the flags for the log consumer event.

         @param[in] setFlags     The set of flags to add to the log consumer event.

         @param[in] clearFlags   The set of flags to remove from the log consumer event.  These
                                 flags will be cleared before the flags from @p setFlags are
                                 added.

         @returns ``true`` if the log consumer event's flags were successfully modified.  Returns
                  ``false`` if the log consumer event or schema is not present or did not get loaded.
        """
    @property
    def log_level(self) -> int:
        """
        :type: int
        """
    @log_level.setter
    def log_level(self, arg1: int) -> None:
        pass
    pass
class IStructuredLogSettings(_IStructuredLogSettings, omni.core._core.IObject):
    """
    Structured log settings interface.  This allows a host app to modify some behavior of the
     structured log system for the process or to retrieve information about the current settings.
     These settings control features such as the event queue size, log rotation, event ID
     generation, the output log path, and the user ID.  Most of the default settings should be
     sufficient for most apps with the exception of the user ID.  For host apps that use at
     least one non-anonymized schema the only settings that must be set is the user ID.

     This interface object can be acquired either by requesting it from the type factory or
     by casting an IStructuredLog object to this type.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def enable_schemas_from_settings(self) -> bool: 
        """
        Checks app settings to see if any schemas or events should be disabled or enabled.

         @returns ``true`` if the settings registry was successfully checked for enable or disable
                  states.  Returns ``false`` if the \\ref carb::settings::ISettings or \\ref carb::dictionary::IDictionary
                  plugins have not been loaded yet.

         @remarks This checks the settings registry to determine if any schemas or events should
                  be disabled initially.  The keys in the settings registry that will be looked
                  at are under @ref omni::structuredlog::kSchemasStateListSetting,
                  @ref omni::structuredlog::kEventsStateListSetting,
                  @ref omni::structuredlog::kEventsStateArraySetting,
                  and @ref omni::structuredlog::kSchemasStateArraySetting.  Each of these parts
                  of the settings registry expects the schema or event name to be specified in
                  a different way.  Once the settings have been loaded, they are cached internally
                  and will be used as the initial state of any newly registered schemas or events.
                  Any state changes to events or schemas after these settings are cached can still
                  be done programmatically with @ref omni::structuredlog::IStructuredLog::setEnabled().
        """
    def get_log_path_for_event(self, event_id: int) -> str: 
        """
        Retrieves the log path that a given event will be written to.

         @param[in] eventId  The ID of the event to retrieve the log path for.  This must be the
                             same ID used when the event was registered.  This may also be
                             @ref omni::structuredlog::kDefaultLogPathEvent to retrieve the
                             path for the default log.
         @returns The name and path of the log file that the requested event would go to if it
                  were emitted with current settings.
         @returns the name and path of the default log file if kDefaultLogPathEvent is used for
                  for the event ID.
         @returns ``nullptr`` if the given event ID is unknown or kDefaultLogPathEvent was used
                  and no default log name has been set.

         @thread_safety This call itself is thread safe.  However, the returned string is only
                        valid until either the log path or the default log name changes.  It is
                        the caller's responsibility to ensure the returned string is used safely.
        """
    def load_privacy_settings(self) -> bool: 
        """
        Attempts to load the privacy settings file.

         @returns ``true`` if the privacy settings file was successfully loaded.

         @returns ``false`` if the privacy settings file could not be loaded.  This failure may be
                  caused by the file being missing, failing to open the file due to permissions,
                  failing to allocate memory to read in the file, the file not being formatted
                  correctly as a TOML file, or failing to merge the new values into the settings
                  registry.

         @remarks This will attempt to load the privacy settings file for the current user.  Regardless
                  of whether the file is successfully loaded, appropriate defaults will always be set
                  for each of the expected privacy settings (as long as the ISettings interface is
                  available).

         @note This expects that some other system has already found and attempted to load the
               plugin that implements the ISettings interface.
        """
    @staticmethod
    def set_event_id_mode(*args, **kwargs) -> typing.Any: 
        """
        Sets the current event identifier mode and type.

         @param[in] mode     The new identifier mode to use.  This will take effect on the next
                             event that is sent.  The default is IdMode::eFastSequential.

         @param[in] type     The new identifier type to use.  This will take effect on the next
                             event that is sent.  The default is IdType::eUuid.

         @returns No return value.

         @thread_safety This call is thread safe.
        """
    @property
    def event_id_mode(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def event_id_type(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def event_queue_size(self) -> int:
        """
        :type: int
        """
    @event_queue_size.setter
    def event_queue_size(self, arg1: int) -> None:
        pass
    @property
    def log_default_name(self) -> str:
        """
        :type: str
        """
    @log_default_name.setter
    def log_default_name(self, arg1: str) -> None:
        pass
    @property
    def log_output_path(self) -> str:
        """
        :type: str
        """
    @log_output_path.setter
    def log_output_path(self, arg1: str) -> None:
        pass
    @property
    def log_retention_count(self) -> int:
        """
        :type: int
        """
    @log_retention_count.setter
    def log_retention_count(self, arg1: int) -> None:
        pass
    @property
    def log_size_limit(self) -> int:
        """
        :type: int
        """
    @log_size_limit.setter
    def log_size_limit(self, arg1: int) -> None:
        pass
    @property
    def session_id(self) -> int:
        """
        :type: int
        """
    @property
    def user_id(self) -> str:
        """
        :type: str
        """
    @user_id.setter
    def user_id(self, arg1: str) -> None:
        pass
    pass
class IStructuredLogSettings2(_IStructuredLogSettings2, omni.core._core.IObject):
    """
    Interface for the second version of the IStructuredLogSettings interface.  This interface
     exposes more settings to control the behaviour of the structured logging system.  This
     object can be retrieved directly or by casting the main IStructuredLog interface to this
     type using ``omni::core::ObjectPtr::as<>()``.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def set_output_flags(self, flags_to_add: int, flags_to_remove: int) -> None: 
        """
        Sets or clears one or more output flags for structured logging.

         @param[in] flagsToAdd       A set of zero or more flag bits to set.  These must be either
                                     @ref omni::structuredlog::fOutputFlagNone or one or more of
                                     the @ref omni::structuredlog::OutputFlags flags.

         @param[in] flagsToRemove    A set of zero or more flag bits to cleared.  These must be
                                     either @ref omni::structuredlog::fOutputFlagNone or one or
                                     more of the @ref omni::structuredlog::OutputFlags flags.

         @returns No return value.

         @remarks This sets or clears flags that affect the output from the structured logging
                  system.  These flags are all disabled by default.  These flags will take effect
                  the next time a message is emitted.
        """
    @property
    def heartbeat_period(self) -> int:
        """
        :type: int
        """
    @heartbeat_period.setter
    def heartbeat_period(self, arg1: int) -> None:
        pass
    @property
    def need_log_headers(self) -> bool:
        """
        :type: bool
        """
    @need_log_headers.setter
    def need_log_headers(self, arg1: bool) -> None:
        pass
    @property
    def output_flags(self) -> int:
        """
        :type: int
        """
    pass
class IdMode():
    """
    Names to control how the next event identifier is generated after each event message. 

    Members:

      RANDOM : Each event identifier will be completely random.  There will be no ordering relationship  between any two events.  This mode is useful when a sense of ordering is not needed but  a very small probability of an event identifier collision is needed.

      SEQUENTIAL : Each event identifier will be incremented by one from the previous one.  When using a  UUID identifier, this will increment the previous identifier by one starting from the  rightmost value.  When using a 64-bit identifier, this the previous identifier will just  be incremented by one.  This is useful when ordering is important and events may need  to be sorted.

      FAST_SEQUENTIAL : Each event identifier will be incremented by one from the previous one, but a faster  method will be used.  When using a UUID identifier, this will not produce an easily  sortable set of identifiers, but it will be faster to produce versus the other methods.  When using a 64-bit identifier, this mode is the same as @ref IdMode::eSequential and will  produce an easily sortable set of identifiers.  This is useful when event handling  performance is the most important.
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
    FAST_SEQUENTIAL: omni.structuredlog._structuredlog.IdMode # value = <IdMode.FAST_SEQUENTIAL: 2>
    RANDOM: omni.structuredlog._structuredlog.IdMode # value = <IdMode.RANDOM: 0>
    SEQUENTIAL: omni.structuredlog._structuredlog.IdMode # value = <IdMode.SEQUENTIAL: 1>
    __members__: dict # value = {'RANDOM': <IdMode.RANDOM: 0>, 'SEQUENTIAL': <IdMode.SEQUENTIAL: 1>, 'FAST_SEQUENTIAL': <IdMode.FAST_SEQUENTIAL: 2>}
    pass
class IdType():
    """
    Names to control what type of event identifiers will be used for each message. 

    Members:

      UUID : Generate a 128 bit UUID identifier.  The probability of an identifier collision between  two events will be especially small with this type, especially when using random  identifiers.  This however does have a small performance penalty to process these  identifiers and could result in the event processing thread getting backed up if  a large number of events are being pushed frequently.

      UINT64 : Generate a 64-bit integer identifier.  The probability of an identifier collision  between two events will be higher but still small with this type, especially when  using random identifiers.  This identifier type is more performant and more easily  sortable however.  This identifier type is useful when event processing performance  is most important.
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
    UINT64: omni.structuredlog._structuredlog.IdType # value = <IdType.UINT64: 1>
    UUID: omni.structuredlog._structuredlog.IdType # value = <IdType.UUID: 0>
    __members__: dict # value = {'UUID': <IdType.UUID: 0>, 'UINT64': <IdType.UINT64: 1>}
    pass
class InvalidEventException():
    """
    An exception thrown when invalid data is passed to send_event()
    """
    pass
class InvalidSchemaException():
    """
    An exception thrown when an invalid schema is registered
    """
    pass
class StructuredLogEvent():
    """
    An opaque handle which identifies an individual telemetry event
    """
    @property
    def eventId(self) -> int:
        """
        :type: int
        """
    @property
    def schema(self) -> dict:
        """
        :type: dict
        """
    pass
class UniqueApp():
    """
    Helper class to manage the unique telemetry transmitter instance on the system.
    This can be used to 'connect' to the transmitter as a client which will prevent it from
    shutting down until your client has exited or disconnected.

    Launching a transmitter through launchTransmitter() will create this guard already, so
    using a guard manually is only necessary in cases where that's not being used, such as
    tests.
    """
    def connect_client_process(self) -> bool: 
        """
        Notifies the unique app that a host app is running.

         This lets the unique app know that the calling host app is still running.  This
         is done by adding a shared lock reference to a marker file that the unique app
         can poll on periodically.  The operating system will automatically remove the lock
         reference(s) for this call once the calling process exits (naturally or otherwise).

        This call is not thread safe.  It is the caller's responsibility to
        ensure calls to it are protected.  However, since it is meant to
        operate between processes, there may still be unavoidable race conditions
        that could arise.

        Returns:
            `true` if the unique app was successfully notified of the new running
             host app.  Returns `false` if the notification either couldn't be sent or
             could not be completed.
        """
    def disconnect_client_process(self) -> None: 
        """
        'Disconnect' the calling process from the exit guard.

        This closes the calling process's reference to the exit guard file.  This will allow
        the exit guard for a host app process to be explicitly cleaned up before exit if
        needed.

        This call is not thread safe.  It is the caller's responsibility to
        ensure calls to it are protected.

        Returns:
            None
        """
    pass
class _IStructuredLogControl(omni.core._core.IObject):
    pass
class _IStructuredLogControl2(omni.core._core.IObject):
    pass
class _IStructuredLogExtraFields(omni.core._core.IObject):
    pass
class _IStructuredLogFromILog(omni.core._core.IObject):
    pass
class _IStructuredLogFromILog2(omni.core._core.IObject):
    pass
class _IStructuredLogSettings(omni.core._core.IObject):
    pass
class _IStructuredLogSettings2(omni.core._core.IObject):
    pass
def create_launch_guard() -> UniqueApp:
    """
    Create a guard with the standard name and path for the transmitter.

    This guard is needed by all telemetry clients to let the transmitter
    know when all clients have shut down so it can exit as well.

    Returns:
        A UniqueApp guard that is used to let the transmitter know when
        it should exit on its own.  Telemetry clients should use this to
        'connect' to the transmitter (note that this does not require the
        transmitter to be running yet). See launchTransmitter() for an
        example usage.
    """
def register_schema(schema: dict) -> dict:
    """
    Register a schema with the structured logging system
    To be able to send events, you need to register a schema that specifies the
    data layout of your events.

    Args:
        schema: The dict specifying your message schema.
                This dict can be directly loaded from your JSON schema.
                If this schema isn't a valid structured logging schema, this call will throw.
                Note that the ordering of the events in this dictionary, as well
                as the ordering of non-constant properties in the events is important.
                If you pass a schema in with events/properties rearranged, this call
                will throw an exception.
    Returns:
        This returns a dict, which contains a handle for each event that is used to call send_event().
        The keys of this dictionary are the short names of each event.
        The value of each dictionary entry is opaque and should just be passed to send_event().
    """
def send_event(*args, **kwargs) -> typing.Any:
    pass
ALL_SCHEMAS = 18446744073709551613
DEFAULT_LOG_PATH_EVENT = 0
