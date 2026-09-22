from __future__ import annotations
import omni.client.impl._omniclient
import typing

__all__ = [
    "AccessFlags",
    "AclEntry",
    "AuthDeviceFlowParams",
    "ChannelEvent",
    "ConnectionStatus",
    "Content",
    "CopyBehavior",
    "FileStatus",
    "ItemFlags",
    "ListEntry",
    "ListEvent",
    "ListIncludeOption",
    "LiveUpdateType",
    "LogLevel",
    "MetricsEvent",
    "Registration",
    "Request",
    "Result",
    "ServerInfo",
    "Url",
    "VERSION",
    "WriteFileExInfo",
    "add_bookmark",
    "add_default_search_path",
    "add_user_to_group_with_callback",
    "authentication_cancel",
    "break_url",
    "break_url_reference",
    "bypass_list_cache",
    "close_cached_file",
    "combine_urls",
    "combine_with_base_url",
    "copy_file_with_callback",
    "copy_folder_with_callback",
    "copy_with_callback",
    "create_checkpoint_with_callback",
    "create_folder_with_callback",
    "create_group_with_callback",
    "create_with_hash_with_callback",
    "delete_single_with_callback",
    "delete_with_callback",
    "enable_nucleus_cache_bypass",
    "get_acls_with_callback",
    "get_base_url",
    "get_branch_and_checkpoint_from_query",
    "get_default_search_paths",
    "get_group_users_with_callback",
    "get_groups_with_callback",
    "get_hub_http_uri_with_callback",
    "get_hub_version_with_callback",
    "get_local_file_with_callback",
    "get_server_info_with_callback",
    "get_user_groups_with_callback",
    "get_users_with_callback",
    "get_version",
    "initialize",
    "join_channel_with_callback",
    "list_bookmarks_with_callback",
    "list_checkpoints_with_callback",
    "list_subscribe_with_callback",
    "list_with_callback",
    "live_get_latest_server_time",
    "live_process",
    "live_process_up_to",
    "live_register_queued_callback",
    "live_set_queued_callback",
    "live_wait_for_pending_updates",
    "lock_with_callback",
    "make_file_url",
    "make_printable",
    "make_query_from_branch_and_checkpoint",
    "make_relative_url",
    "make_url",
    "move_file_with_callback",
    "move_folder_with_callback",
    "move_with_callback",
    "normalize_url",
    "obliterate_with_callback",
    "open_cached_file_with_callback",
    "pop_base_url",
    "push_base_url",
    "read_file_with_callback",
    "reconnect",
    "refresh_auth_token_with_callback",
    "register_authentication_callback",
    "register_authorize_callback",
    "register_connection_status_callback",
    "register_device_flow_auth_callback",
    "register_file_status_callback",
    "remove_bookmark",
    "remove_default_search_path",
    "remove_group_with_callback",
    "remove_user_from_group_with_callback",
    "rename_group_with_callback",
    "resolve_subscribe_with_callback",
    "resolve_with_callback",
    "send_message_with_callback",
    "set_acls_with_callback",
    "set_alias",
    "set_authentication_message_box_callback",
    "set_azure_sas_token",
    "set_hang_detection_time_ms",
    "set_http_header",
    "set_log_callback",
    "set_log_level",
    "set_product_info",
    "set_retries",
    "set_s3_configuration",
    "shutdown",
    "sign_out",
    "stat_subscribe_with_callback",
    "stat_with_callback",
    "trace_start",
    "trace_stop",
    "undelete_with_callback",
    "unlock_with_callback",
    "write_file_ex_with_callback",
    "write_file_with_callback"
]


class AccessFlags():
    """
                Access flags that define permissions for files and folders.

                These flags can be combined using bitwise operations to represent
                different levels of access permissions.
            

    Members:

      READ : Can read this thing

      WRITE : Can write to this thing

      ADMIN : Can change ACLs for this thing
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
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
    ADMIN: omni.client.impl._omniclient.AccessFlags # value = <AccessFlags.ADMIN: 4>
    READ: omni.client.impl._omniclient.AccessFlags # value = <AccessFlags.READ: 1>
    WRITE: omni.client.impl._omniclient.AccessFlags # value = <AccessFlags.WRITE: 2>
    __members__: dict # value = {'READ': <AccessFlags.READ: 1>, 'WRITE': <AccessFlags.WRITE: 2>, 'ADMIN': <AccessFlags.ADMIN: 4>}
    pass
class AclEntry():
    """
    Access Control List entry for user or group permissions.

    This object represents a single entry in an access control list,
    defining the permissions for a specific user or group.
    """
    def __init__(self, arg0: str, arg1: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def access(self) -> int:
        """
                        The access level for this user or group.

                        This is a combination of AccessFlags that apply to this user or group.
                        Use bitwise operations to test and set individual flags.
                    

        :type: int
        """
    @access.setter
    def access(self, arg0: int) -> None:
        """
        The access level for this user or group.

        This is a combination of AccessFlags that apply to this user or group.
        Use bitwise operations to test and set individual flags.
        """
    @property
    def name(self) -> str:
        """
                        The name of the user or group.

                        This identifies the user or group that this ACL entry applies to.
                    

        :type: str
        """
    @name.setter
    def name(self, arg0: str) -> None:
        """
        The name of the user or group.

        This identifies the user or group that this ACL entry applies to.
        """
    pass
class AuthDeviceFlowParams():
    """
    Parameters for device flow authentication.

    This object contains the information needed for device flow authentication,
    including the authorization URL and code that the user needs to enter.
    """
    @property
    def code(self) -> str:
        """
        The code the user should type in on the auth web page

        :type: str
        """
    @property
    def expiration(self) -> int:
        """
        Time in seconds that the user has to enter the code before auth is automatically cancelled

        :type: int
        """
    @property
    def server(self) -> str:
        """
        The server that we are trying to authorize with

        :type: str
        """
    @property
    def url(self) -> str:
        """
        The URL of a webpage where the user can go to authorize

        :type: str
        """
    pass
class ChannelEvent():
    """
                Channel event types for real-time messaging.

                These events are reported when channel-related activities occur,
                such as messages being sent or users joining/leaving.
            

    Members:

      ERROR : An unknown error occurred

      MESSAGE : Someone sent a message

      HELLO : You joined a channel that someone else was already in, and they said hello

      JOIN : Someone joined the channel

      LEFT : Someone left the channel (as of Nucleus 114, the server does not appear to send these)

      DELETED : Someone deleted the channel or changed ACLs so you no longer have access
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
    DELETED: omni.client.impl._omniclient.ChannelEvent # value = <ChannelEvent.DELETED: 5>
    ERROR: omni.client.impl._omniclient.ChannelEvent # value = <ChannelEvent.ERROR: 0>
    HELLO: omni.client.impl._omniclient.ChannelEvent # value = <ChannelEvent.HELLO: 2>
    JOIN: omni.client.impl._omniclient.ChannelEvent # value = <ChannelEvent.JOIN: 3>
    LEFT: omni.client.impl._omniclient.ChannelEvent # value = <ChannelEvent.LEFT: 4>
    MESSAGE: omni.client.impl._omniclient.ChannelEvent # value = <ChannelEvent.MESSAGE: 1>
    __members__: dict # value = {'ERROR': <ChannelEvent.ERROR: 0>, 'MESSAGE': <ChannelEvent.MESSAGE: 1>, 'HELLO': <ChannelEvent.HELLO: 2>, 'JOIN': <ChannelEvent.JOIN: 3>, 'LEFT': <ChannelEvent.LEFT: 4>, 'DELETED': <ChannelEvent.DELETED: 5>}
    pass
class ConnectionStatus():
    """
                Connection status values for server connections.

                Valid transitions:
                - Disconnected -> Connecting or InvalidHost
                - Connecting -> All except Disconnected
                - Connected -> Disconnected or SignedOut

                These status values are reported through connection status callbacks.
            

    Members:

      CONNECTING : Attempting to connect to the server

      CONNECTED : Successfully connected to the server

      CONNECT_ERROR : Error while trying to connect to the server

      DISCONNECTED : Disconnected after a successful connection

      SIGNED_OUT : Sign out was called

      NO_USERNAME : No username was provided (This status is no longer used)

      AUTH_ABORT : Application returned an abort code in the authentication callback

      AUTH_CANCELLED : User clicked 'Cancel' or the application called authentication_cancel

      AUTH_ERROR : Internal error while trying to authenticate

      AUTH_FAILED : Authentication failed

      SERVER_INCOMPATIBLE : The server is not compatible with this version of the client library

      INVALID_HOST : The host name is invalid
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
    AUTH_ABORT: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.AUTH_ABORT: 6>
    AUTH_CANCELLED: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.AUTH_CANCELLED: 7>
    AUTH_ERROR: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.AUTH_ERROR: 8>
    AUTH_FAILED: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.AUTH_FAILED: 9>
    CONNECTED: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.CONNECTED: 1>
    CONNECTING: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.CONNECTING: 0>
    CONNECT_ERROR: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.CONNECT_ERROR: 2>
    DISCONNECTED: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.DISCONNECTED: 3>
    INVALID_HOST: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.INVALID_HOST: 11>
    NO_USERNAME: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.NO_USERNAME: 5>
    SERVER_INCOMPATIBLE: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.SERVER_INCOMPATIBLE: 10>
    SIGNED_OUT: omni.client.impl._omniclient.ConnectionStatus # value = <ConnectionStatus.SIGNED_OUT: 4>
    __members__: dict # value = {'CONNECTING': <ConnectionStatus.CONNECTING: 0>, 'CONNECTED': <ConnectionStatus.CONNECTED: 1>, 'CONNECT_ERROR': <ConnectionStatus.CONNECT_ERROR: 2>, 'DISCONNECTED': <ConnectionStatus.DISCONNECTED: 3>, 'SIGNED_OUT': <ConnectionStatus.SIGNED_OUT: 4>, 'NO_USERNAME': <ConnectionStatus.NO_USERNAME: 5>, 'AUTH_ABORT': <ConnectionStatus.AUTH_ABORT: 6>, 'AUTH_CANCELLED': <ConnectionStatus.AUTH_CANCELLED: 7>, 'AUTH_ERROR': <ConnectionStatus.AUTH_ERROR: 8>, 'AUTH_FAILED': <ConnectionStatus.AUTH_FAILED: 9>, 'SERVER_INCOMPATIBLE': <ConnectionStatus.SERVER_INCOMPATIBLE: 10>, 'INVALID_HOST': <ConnectionStatus.INVALID_HOST: 11>}
    pass
class Content():
    """
    Content buffer for file operations.

    This object represents a buffer of data that can be passed to various client library functions.
    The library will take ownership of the buffer and free it when finished, unless the buffer was
    created using a reference.

    Use python :obj:`memoryview` to access the buffer data. For example::

            _, content = await omni.client.read_file_async("omniverse://ov-sandbox/some/file.txt")
            print(memoryview(content).tobytes())

    The buffer can be accessed using standard Python indexing and slicing operations.
    """
    def __getitem__(self, arg0: int) -> str: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg0: int, arg1: str) -> None: ...
    pass
class CopyBehavior():
    """
                Copy behavior options for file and folder operations.

                These options control what happens when the destination already exists
                during copy or move operations.
            

    Members:

      ERROR_IF_EXISTS : Fail with an error if the destination already exists (default behavior)

      OVERWRITE : Overwrite the destination if it already exists
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
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
    ERROR_IF_EXISTS: omni.client.impl._omniclient.CopyBehavior # value = <CopyBehavior.ERROR_IF_EXISTS: 0>
    OVERWRITE: omni.client.impl._omniclient.CopyBehavior # value = <CopyBehavior.OVERWRITE: 1>
    __members__: dict # value = {'ERROR_IF_EXISTS': <CopyBehavior.ERROR_IF_EXISTS: 0>, 'OVERWRITE': <CopyBehavior.OVERWRITE: 1>}
    pass
class FileStatus():
    """
                File status values for file transfer operations.

                These status values are reported through file status callbacks to indicate
                the progress of file operations like reading, writing, copying, etc.
            

    Members:

      READING : Reading a file from the server

      WRITING : Writing a file to the server

      COPYING : Copying a file (the URL is the source URL)

      MOVING : Moving a file (the URL is the source URL)

      DELETING : Deleting a file

      OBLITERATING : Obliterating a file

      SENDING_UPDATE : Sending a live update (deprecated - use live_register_queued_callback2)

      RECEIVED_UPDATE : Received a live update (deprecated - use live_register_queued_callback2)

      LISTING : Performing a list operation

      STATING : Performing a stat operation
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
    COPYING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.COPYING: 2>
    DELETING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.DELETING: 4>
    LISTING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.LISTING: 8>
    MOVING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.MOVING: 3>
    OBLITERATING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.OBLITERATING: 5>
    READING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.READING: 0>
    RECEIVED_UPDATE: omni.client.impl._omniclient.FileStatus # value = <FileStatus.RECEIVED_UPDATE: 7>
    SENDING_UPDATE: omni.client.impl._omniclient.FileStatus # value = <FileStatus.SENDING_UPDATE: 6>
    STATING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.STATING: 9>
    WRITING: omni.client.impl._omniclient.FileStatus # value = <FileStatus.WRITING: 1>
    __members__: dict # value = {'READING': <FileStatus.READING: 0>, 'WRITING': <FileStatus.WRITING: 1>, 'COPYING': <FileStatus.COPYING: 2>, 'MOVING': <FileStatus.MOVING: 3>, 'DELETING': <FileStatus.DELETING: 4>, 'OBLITERATING': <FileStatus.OBLITERATING: 5>, 'SENDING_UPDATE': <FileStatus.SENDING_UPDATE: 6>, 'RECEIVED_UPDATE': <FileStatus.RECEIVED_UPDATE: 7>, 'LISTING': <FileStatus.LISTING: 8>, 'STATING': <FileStatus.STATING: 9>}
    pass
class ItemFlags():
    """
                Item flags that describe properties and capabilities of files and folders.

                These flags provide information about what operations can be performed
                on an item and what type of item it is.
            

    Members:

      READABLE_FILE : You can call read_file on this (note: ACLs may still prevent you from reading it)

      WRITEABLE_FILE : You can call write_file on this (note: ACLs may still prevent you from writing it)

      CAN_HAVE_CHILDREN : This thing can contain other things (a folder-like thing)

      DOES_NOT_HAVE_CHILDREN : This thing does not have any children. The lack of this flag does not mean it does have children. Sometimes we are not sure if it has children until you attempt to list the children. This is only intended to be used for UI elements to hide the 'expand' button if we are sure it does not have any children.

      IS_MOUNT : This thing is the root of a mount point

      IS_INSIDE_MOUNT : This thing is located inside a mounted folder

      CAN_LIVE_UPDATE : This thing supports live updates

      IS_OMNI_OBJECT : This thing is in omni-object format. You must use live_read to read it and live_update to update it

      IS_CHANNEL : You can call join_channel on this

      IS_CHECKPOINTED : This item is a checkpoint

      IS_DELETED : This item is deleted - never set if the server does not support soft-delete
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
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
    CAN_HAVE_CHILDREN: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.CAN_HAVE_CHILDREN: 4>
    CAN_LIVE_UPDATE: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.CAN_LIVE_UPDATE: 64>
    DOES_NOT_HAVE_CHILDREN: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.DOES_NOT_HAVE_CHILDREN: 8>
    IS_CHANNEL: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.IS_CHANNEL: 256>
    IS_CHECKPOINTED: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.IS_CHECKPOINTED: 512>
    IS_DELETED: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.IS_DELETED: 1024>
    IS_INSIDE_MOUNT: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.IS_INSIDE_MOUNT: 32>
    IS_MOUNT: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.IS_MOUNT: 16>
    IS_OMNI_OBJECT: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.IS_OMNI_OBJECT: 128>
    READABLE_FILE: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.READABLE_FILE: 1>
    WRITEABLE_FILE: omni.client.impl._omniclient.ItemFlags # value = <ItemFlags.WRITEABLE_FILE: 2>
    __members__: dict # value = {'READABLE_FILE': <ItemFlags.READABLE_FILE: 1>, 'WRITEABLE_FILE': <ItemFlags.WRITEABLE_FILE: 2>, 'CAN_HAVE_CHILDREN': <ItemFlags.CAN_HAVE_CHILDREN: 4>, 'DOES_NOT_HAVE_CHILDREN': <ItemFlags.DOES_NOT_HAVE_CHILDREN: 8>, 'IS_MOUNT': <ItemFlags.IS_MOUNT: 16>, 'IS_INSIDE_MOUNT': <ItemFlags.IS_INSIDE_MOUNT: 32>, 'CAN_LIVE_UPDATE': <ItemFlags.CAN_LIVE_UPDATE: 64>, 'IS_OMNI_OBJECT': <ItemFlags.IS_OMNI_OBJECT: 128>, 'IS_CHANNEL': <ItemFlags.IS_CHANNEL: 256>, 'IS_CHECKPOINTED': <ItemFlags.IS_CHECKPOINTED: 512>, 'IS_DELETED': <ItemFlags.IS_DELETED: 1024>}
    pass
class ListEntry():
    """
    Information about a file or folder from list operations.

    This object contains metadata about an item returned from list operations.
    The exact meaning of some fields depends on the function being called.
    """
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def access(self) -> int:
        """
                        YOUR access level for this item.

                        This is a combination of AccessFlags indicating what operations
                        you can perform on this item.
                    

        :type: int
        """
    @property
    def comment(self) -> str:
        """
                        Provider-specific comment.

                        This will only be set for checkpoint operations.
                        Not all providers support this, so it may be empty.
                    

        :type: str
        """
    @property
    def created_by(self) -> str:
        """
                        User name of the client that created it.

                        Not all providers support this, so it may be empty.
                    

        :type: str
        """
    @property
    def created_time(self) -> datetime.datetime:
        """
                        When the file was created.

                        This is a datetime object representing when the file was first created.
                    

        :type: datetime.datetime
        """
    @property
    def deleted_by(self) -> str:
        """
                        User name of the client that deleted it.

                        Not all providers support this, so it may be empty.
                    

        :type: str
        """
    @property
    def deleted_time(self) -> datetime.datetime:
        """
                        When the file was deleted.

                        This is a datetime object representing when the file was deleted.
                        Only set if the server supports soft-delete.
                    

        :type: datetime.datetime
        """
    @property
    def flags(self) -> int:
        """
                        Information about this item.

                        This is a combination of ItemFlags indicating the properties
                        and capabilities of this item.
                    

        :type: int
        """
    @property
    def hash(self) -> str:
        """
                        Provider specific file hash.

                        Not all providers support this, so it may be empty.
                    

        :type: str
        """
    @property
    def locked_by(self) -> str:
        """
                        User name of the client that locked it.

                        Empty if it's not locked. Not all providers support this.
                    

        :type: str
        """
    @property
    def modified_by(self) -> str:
        """
                        User name of the last client to modify it.

                        Not all providers support this, so it may be empty.
                    

        :type: str
        """
    @property
    def modified_time(self) -> datetime.datetime:
        """
                        The last time the file was modified.

                        This is a datetime object representing when the file was last changed.
                    

        :type: datetime.datetime
        """
    @property
    def relative_path(self) -> str:
        """
                        The relative path for this item.

                        The exact meaning depends on the function being called:
                        - For list operations: it's the name of the item
                        - For checkpoint operations: it's the "query" part of the URL
                    

        :type: str
        """
    @property
    def size(self) -> int:
        """
                        For files, the size in bytes. Undefined for other types.
                    

        :type: int
        """
    @property
    def version(self) -> str:
        """
                        Provider-specific version.

                        May not be an always incrementing number (could be a hash, for example).
                        Not all providers support this, so it may be empty.
                    

        :type: str
        """
    pass
class ListEvent():
    """
                List subscription event types.

                These events are reported when items you've subscribed to change.
            

    Members:

      UNKNOWN : Unknown event type

      CREATED : An item was created

      UPDATED : An item (contents) were updated

      DELETED : An item was deleted

      METADATA : An item's metadata was changed

      LOCKED : A file was locked

      UNLOCKED : A file was unlocked

      OBLITERATED : A file was obliterated
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
    CREATED: omni.client.impl._omniclient.ListEvent # value = <ListEvent.CREATED: 1>
    DELETED: omni.client.impl._omniclient.ListEvent # value = <ListEvent.DELETED: 3>
    LOCKED: omni.client.impl._omniclient.ListEvent # value = <ListEvent.LOCKED: 5>
    METADATA: omni.client.impl._omniclient.ListEvent # value = <ListEvent.METADATA: 4>
    OBLITERATED: omni.client.impl._omniclient.ListEvent # value = <ListEvent.OBLITERATED: 7>
    UNKNOWN: omni.client.impl._omniclient.ListEvent # value = <ListEvent.UNKNOWN: 0>
    UNLOCKED: omni.client.impl._omniclient.ListEvent # value = <ListEvent.UNLOCKED: 6>
    UPDATED: omni.client.impl._omniclient.ListEvent # value = <ListEvent.UPDATED: 2>
    __members__: dict # value = {'UNKNOWN': <ListEvent.UNKNOWN: 0>, 'CREATED': <ListEvent.CREATED: 1>, 'UPDATED': <ListEvent.UPDATED: 2>, 'DELETED': <ListEvent.DELETED: 3>, 'METADATA': <ListEvent.METADATA: 4>, 'LOCKED': <ListEvent.LOCKED: 5>, 'UNLOCKED': <ListEvent.UNLOCKED: 6>, 'OBLITERATED': <ListEvent.OBLITERATED: 7>}
    pass
class ListIncludeOption():
    """
                Options for controlling which items are included in list operations.

                These options control whether deleted items are included when listing
                files and folders.
            

    Members:

      NO_DELETED_FILES : List only files which are not deleted (default)

      INCLUDE_DELETED_FILES : List both deleted and non-deleted files

      ONLY_DELETED_FILES : List only files which are deleted
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
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
    INCLUDE_DELETED_FILES: omni.client.impl._omniclient.ListIncludeOption # value = <ListIncludeOption.INCLUDE_DELETED_FILES: 1>
    NO_DELETED_FILES: omni.client.impl._omniclient.ListIncludeOption # value = <ListIncludeOption.NO_DELETED_FILES: 0>
    ONLY_DELETED_FILES: omni.client.impl._omniclient.ListIncludeOption # value = <ListIncludeOption.ONLY_DELETED_FILES: 2>
    __members__: dict # value = {'NO_DELETED_FILES': <ListIncludeOption.NO_DELETED_FILES: 0>, 'INCLUDE_DELETED_FILES': <ListIncludeOption.INCLUDE_DELETED_FILES: 1>, 'ONLY_DELETED_FILES': <ListIncludeOption.ONLY_DELETED_FILES: 2>}
    pass
class LiveUpdateType():
    """
                Live update types for real-time file synchronization.

                These types indicate the source and nature of live updates,
                helping you understand whether updates are local or remote.
            

    Members:

      REMOTE : A remote client sent an update

      LOCAL : The server acknowledged a local update

      MORE : Due to Jitter reduction, a queued update may not be processed by live_process. When this happens, the callback is called with this update type indicating that it's now time to process the update
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
    LOCAL: omni.client.impl._omniclient.LiveUpdateType # value = <LiveUpdateType.LOCAL: 1>
    MORE: omni.client.impl._omniclient.LiveUpdateType # value = <LiveUpdateType.MORE: 2>
    REMOTE: omni.client.impl._omniclient.LiveUpdateType # value = <LiveUpdateType.REMOTE: 0>
    __members__: dict # value = {'REMOTE': <LiveUpdateType.REMOTE: 0>, 'LOCAL': <LiveUpdateType.LOCAL: 1>, 'MORE': <LiveUpdateType.MORE: 2>}
    pass
class LogLevel():
    """
                Log levels for controlling the verbosity of logging output.

                These levels control which messages are displayed by the client library.
                Any messages below the set level will not be logged.
            

    Members:

      DEBUG : Extra chatty

      VERBOSE : Chatty

      INFO : Not a problem

      WARNING : Potential problem

      ERROR : Definite problem
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
    DEBUG: omni.client.impl._omniclient.LogLevel # value = <LogLevel.DEBUG: 0>
    ERROR: omni.client.impl._omniclient.LogLevel # value = <LogLevel.ERROR: 4>
    INFO: omni.client.impl._omniclient.LogLevel # value = <LogLevel.INFO: 2>
    VERBOSE: omni.client.impl._omniclient.LogLevel # value = <LogLevel.VERBOSE: 1>
    WARNING: omni.client.impl._omniclient.LogLevel # value = <LogLevel.WARNING: 3>
    __members__: dict # value = {'DEBUG': <LogLevel.DEBUG: 0>, 'VERBOSE': <LogLevel.VERBOSE: 1>, 'INFO': <LogLevel.INFO: 2>, 'WARNING': <LogLevel.WARNING: 3>, 'ERROR': <LogLevel.ERROR: 4>}
    pass
class MetricsEvent():
    """
                Metrics event types for performance monitoring.

                These events are reported when operations complete and provide
                performance metrics for monitoring and debugging.
            

    Members:

      STAT_COMPLETE : A stat operation completed

      READ_COMPLETE : A read operation completed

      WRITE_COMPLETE : A write operation completed

      LIST_COMPLETE : A list operation completed

      ENUMERATE_VERSIONS_COMPLETE : A version enumeration operation completed

      LIST_SERVICES_COMPLETE : A list services operation completed

      GET_METADATA_COMPLETE : A get metadata operation completed

      DELETE_COMPLETE : A delete operation completed
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
    DELETE_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.DELETE_COMPLETE: 7>
    ENUMERATE_VERSIONS_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.ENUMERATE_VERSIONS_COMPLETE: 4>
    GET_METADATA_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.GET_METADATA_COMPLETE: 6>
    LIST_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.LIST_COMPLETE: 3>
    LIST_SERVICES_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.LIST_SERVICES_COMPLETE: 5>
    READ_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.READ_COMPLETE: 1>
    STAT_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.STAT_COMPLETE: 0>
    WRITE_COMPLETE: omni.client.impl._omniclient.MetricsEvent # value = <MetricsEvent.WRITE_COMPLETE: 2>
    __members__: dict # value = {'STAT_COMPLETE': <MetricsEvent.STAT_COMPLETE: 0>, 'READ_COMPLETE': <MetricsEvent.READ_COMPLETE: 1>, 'WRITE_COMPLETE': <MetricsEvent.WRITE_COMPLETE: 2>, 'LIST_COMPLETE': <MetricsEvent.LIST_COMPLETE: 3>, 'ENUMERATE_VERSIONS_COMPLETE': <MetricsEvent.ENUMERATE_VERSIONS_COMPLETE: 4>, 'LIST_SERVICES_COMPLETE': <MetricsEvent.LIST_SERVICES_COMPLETE: 5>, 'GET_METADATA_COMPLETE': <MetricsEvent.GET_METADATA_COMPLETE: 6>, 'DELETE_COMPLETE': <MetricsEvent.DELETE_COMPLETE: 7>}
    pass
class Registration():
    """
    Registration object for managing callback subscriptions.

    This object represents a registered callback subscription that can be used to
    automatically unregister the callback when the object goes out of scope.
    Supports context manager protocol for automatic cleanup.

    Example::

        with omni.client.register_connection_status_callback(callback) as reg:
            # Callback is active during this block
            pass
        # Callback is automatically unregistered when exiting the context
    """
    def __enter__(self) -> Registration: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    pass
class Request():
    """
    Generic request object for managing asynchronous operations.

    This object represents an asynchronous request that can be used to control
    the operation lifecycle. You can stop the request before it completes,
    wait for it to finish, or check its status.

    Supports context manager protocol for automatic cleanup.

    Example::

        with omni.client.read_file_async(url, callback) as request:
            # Request is active during this block
            if some_condition:
                request.stop()  # Cancel the request
        # Request is automatically stopped when exiting the context
    """
    def __enter__(self) -> Request: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def is_finished(self) -> bool: ...
    def stop(self) -> None: ...
    def wait(self) -> None: ...
    @property
    def id(self) -> int:
        """
        :type: int
        """
    pass
class Result():
    """
                Result codes returned by client library operations.

                These codes indicate the success or failure of various operations.
                Use :py:func:`omni.client.get_result_string` to get a human-readable
                description of any result code.
            

    Members:

      OK : The operation was successful

      OK_LATEST : Returned only by live_read and indicates that you have the latest version

      OK_NOT_YET_FOUND : Returned by stat_subscribe and resolve_subscribe to indicate the file wasn't found but is being monitored

      ERROR : An unknown error occurred while processing the request

      ERROR_CONNECTION : The request failed because the connection to the server was lost

      ERROR_NOT_SUPPORTED : The requested operation is not supported by the server or provider

      ERROR_ACCESS_DENIED : You don't have access to perform the requested operation

      ERROR_NOT_FOUND : The operation failed because the specified thing does not exist

      ERROR_BAD_VERSION : This is no longer used

      ERROR_ALREADY_EXISTS : You tried to copy or move over a thing that already exists and behavior was not OVERWRITE

      ERROR_SOURCE_IS_DEST : Tried to copy or move a thing to itself or a child of itself

      ERROR_ACCESS_LOST : Returned when the thing you were subscribed to was deleted or ACLs were changed

      ERROR_LOCKED : Returned when the file you are trying to write is locked by another client

      ERROR_BAD_REQUEST : Returned by HTTP providers when server receives a malformed HTTP request

      ERROR_FOLDER_NOT_EMPTY : Returned if a non-empty folder is passed to obliterate or delete_single

      ERROR_WRONG_TYPE : Returned when trying to perform an operation on an item that doesn't support it

      ERROR_UNSUPPORTED_VERSION : This version is not yet supported
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
    ERROR: omni.client.impl._omniclient.Result # value = <Result.ERROR: 3>
    ERROR_ACCESS_DENIED: omni.client.impl._omniclient.Result # value = <Result.ERROR_ACCESS_DENIED: 6>
    ERROR_ACCESS_LOST: omni.client.impl._omniclient.Result # value = <Result.ERROR_ACCESS_LOST: 11>
    ERROR_ALREADY_EXISTS: omni.client.impl._omniclient.Result # value = <Result.ERROR_ALREADY_EXISTS: 9>
    ERROR_BAD_REQUEST: omni.client.impl._omniclient.Result # value = <Result.ERROR_BAD_REQUEST: 13>
    ERROR_BAD_VERSION: omni.client.impl._omniclient.Result # value = <Result.ERROR_BAD_VERSION: 8>
    ERROR_CONNECTION: omni.client.impl._omniclient.Result # value = <Result.ERROR_CONNECTION: 4>
    ERROR_FOLDER_NOT_EMPTY: omni.client.impl._omniclient.Result # value = <Result.ERROR_FOLDER_NOT_EMPTY: 14>
    ERROR_LOCKED: omni.client.impl._omniclient.Result # value = <Result.ERROR_LOCKED: 12>
    ERROR_NOT_FOUND: omni.client.impl._omniclient.Result # value = <Result.ERROR_NOT_FOUND: 7>
    ERROR_NOT_SUPPORTED: omni.client.impl._omniclient.Result # value = <Result.ERROR_NOT_SUPPORTED: 5>
    ERROR_SOURCE_IS_DEST: omni.client.impl._omniclient.Result # value = <Result.ERROR_SOURCE_IS_DEST: 10>
    ERROR_UNSUPPORTED_VERSION: omni.client.impl._omniclient.Result # value = <Result.ERROR_UNSUPPORTED_VERSION: 16>
    ERROR_WRONG_TYPE: omni.client.impl._omniclient.Result # value = <Result.ERROR_WRONG_TYPE: 15>
    OK: omni.client.impl._omniclient.Result # value = <Result.OK: 0>
    OK_LATEST: omni.client.impl._omniclient.Result # value = <Result.OK_LATEST: 1>
    OK_NOT_YET_FOUND: omni.client.impl._omniclient.Result # value = <Result.OK_NOT_YET_FOUND: 2>
    __members__: dict # value = {'OK': <Result.OK: 0>, 'OK_LATEST': <Result.OK_LATEST: 1>, 'OK_NOT_YET_FOUND': <Result.OK_NOT_YET_FOUND: 2>, 'ERROR': <Result.ERROR: 3>, 'ERROR_CONNECTION': <Result.ERROR_CONNECTION: 4>, 'ERROR_NOT_SUPPORTED': <Result.ERROR_NOT_SUPPORTED: 5>, 'ERROR_ACCESS_DENIED': <Result.ERROR_ACCESS_DENIED: 6>, 'ERROR_NOT_FOUND': <Result.ERROR_NOT_FOUND: 7>, 'ERROR_BAD_VERSION': <Result.ERROR_BAD_VERSION: 8>, 'ERROR_ALREADY_EXISTS': <Result.ERROR_ALREADY_EXISTS: 9>, 'ERROR_SOURCE_IS_DEST': <Result.ERROR_SOURCE_IS_DEST: 10>, 'ERROR_ACCESS_LOST': <Result.ERROR_ACCESS_LOST: 11>, 'ERROR_LOCKED': <Result.ERROR_LOCKED: 12>, 'ERROR_BAD_REQUEST': <Result.ERROR_BAD_REQUEST: 13>, 'ERROR_FOLDER_NOT_EMPTY': <Result.ERROR_FOLDER_NOT_EMPTY: 14>, 'ERROR_WRONG_TYPE': <Result.ERROR_WRONG_TYPE: 15>, 'ERROR_UNSUPPORTED_VERSION': <Result.ERROR_UNSUPPORTED_VERSION: 16>}
    pass
class ServerInfo():
    """
    Information about a connected server.

    This object contains metadata about the server you are connected to,
    including version information, connection details, and feature flags.
    """
    @property
    def auth_token(self) -> str:
        """
        The authentication token you are using (this should no longer be used)

        :type: str
        """
    @property
    def cache_enabled(self) -> bool:
        """
        True if the local nucleus cache is enabled for this server

        :type: bool
        """
    @property
    def checkpoints_enabled(self) -> bool:
        """
        True if checkpoints are enabled on this server

        :type: bool
        """
    @property
    def connection_id(self) -> str:
        """
        Provider specific connection identifier (same value other users see in 'from' field)

        :type: str
        """
    @property
    def omniojects_enabled(self) -> bool:
        """
        True if omni-objects are enabled on this server

        :type: bool
        """
    @property
    def undelete_enabled(self) -> bool:
        """
        True if the server supports the 'undelete' command

        :type: bool
        """
    @property
    def username(self) -> str:
        """
        The username you are signed in as

        :type: str
        """
    @property
    def version(self) -> str:
        """
        The version of software the server is running

        :type: str
        """
    pass
class Url():
    """
    Parsed URL structure for Omniverse URLs.

    This object contains the individual components of a parsed URL,
    making it easy to access and manipulate different parts of the URL.
    """
    @property
    def fragment(self) -> str:
        """
        The part of the URL containing the fragment parameter (percent-decoded)

        :type: str
        """
    @property
    def host(self) -> str:
        """
        The part of the URL indicating the host name or IP address to connect to

        :type: str
        """
    @property
    def is_raw(self) -> bool:
        """
        True if this is a 'raw' URL such as 'C:\\file'. Prevents percent-encoding of the path

        :type: bool
        """
    @property
    def path(self) -> str:
        """
        The part of the URL indicating the path of the item on the server (percent-decoded)

        :type: str
        """
    @property
    def port(self) -> str:
        """
        The part of the URL indicating the port to connect to

        :type: str
        """
    @property
    def query(self) -> str:
        """
        The part of the URL containing the query parameter (percent-decoded)

        :type: str
        """
    @property
    def scheme(self) -> str:
        """
        The part of the URL before the first colon (e.g., 'omniverse', 'http')

        :type: str
        """
    @property
    def user(self) -> str:
        """
        The part of the URL to indicate the user to sign in as

        :type: str
        """
    pass
class WriteFileExInfo():
    """
    Extended information returned from write file operations.

    This object contains additional metadata returned when writing files,
    such as version and hash information if the provider supports it.
    """
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def hash(self) -> str:
        """
                        If the provider supports hashing, this is the hash of the file that was just written.

                        Otherwise blank.
                    

        :type: str
        """
    @property
    def version(self) -> str:
        """
                        If the provider supports versioning, this is the version of the file that was just written.

                        Otherwise blank.
                    

        :type: str
        """
    pass
def add_bookmark(name: str, url: str) -> None:
    """
    Add a bookmark.

    This function adds a URL to the list of bookmarks for quick access.
    Bookmarks are stored locally and persist between application sessions.

    Args:
        name: The name of the bookmark for easy identification
        url: The URL to bookmark

    Note:
        Bookmarks are stored locally and are not synchronized across different
        machines or applications. Each application maintains its own bookmark list.
    """
def add_default_search_path(search_path: str) -> None:
    """
    Add a default search path to the list of search paths used by resolve

    New default search paths are added to the top of the stack (meaning they
    will match before older default search paths), but all default search paths
    are underneath the search_paths explicitly provided to resolve.

    If this search_path is already in the list, it is moved to the top
    """
def add_user_to_group_with_callback(url: str, user: str, group: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Add a user to a group.

    This function adds the specified user to the specified group on the server.
    The callback will be called when the operation completes.

    Args:
        url: The URL of the server to add the user to the group on
        user: The name of the user to add
        group: The name of the group to add the user to
        callback: Callback function that receives the operation result

    Returns:
        A Request object that can be used to control the operation.

    Note:
        This operation requires appropriate permissions on the server.
        The user and group must exist. If the user is already in the group,
        the operation will complete successfully.
    """
def authentication_cancel(auth_handle: int) -> None:
    """
    Cancel an authentication attempt.

    This should be called in response to a user clicking the "Cancel" button in an authentication message box.

    Args:
        auth_handle: The parameter passed to a callback registered with set_authentication_message_box_callback.
    """
def break_url(url: str) -> Url:
    """
    Break a URL into components.

    This function parses a URL and breaks it down into its constituent parts (scheme, user,
    host, port, path, query, fragment). It behaves similarly to :py:func:`omni.client.break_url_reference`
    except it assumes the URL is either a full URL (which starts with a scheme:) or is a raw
    local file path (such as "C:\\path" on Windows or "/path" on Linux).

    Args:
        url: The URL to break into components.

    Returns:
        An OmniClientUrl object containing the parsed URL components.

    Note:
        This function affects how it handles special characters such as : % ? and #.
        If `is_raw` on the returned object is True, the URL was determined to be a raw
        local file path, and only the 'path' value is set.
    """
def break_url_reference(url: str) -> Url:
    """
    Break a URL into components (reference style).

    This function parses a URL and breaks it down into its constituent parts (scheme, user,
    host, port, path, query, fragment). It should be used instead of :py:func:`omni.client.break_url`
    if you have a URL such as '/path?query#fragment' which could be interpreted as a local file path.

    Args:
        url: The URL to break into components.

    Returns:
        An OmniClientUrl object containing the parsed URL components.

    Note:
        This function is useful for parsing relative URLs or URLs that may not have a scheme.
    """
def bypass_list_cache(bypass: bool) -> None:
    """
    Enable or disable list cache bypass.

    This function controls whether the client library bypasses the list cache and goes
    directly to the server for list operations. Typically, when a folder is listed or
    an item in a folder is stat'd, the library establishes a subscription to keep the
    cache up-to-date.

    Args:
        bypass: True to bypass the cache, False to use the cache.

    Note:
        If you are going to be performing a lot of lists on many different folders,
        these subscriptions can add up. If you are not listing the same folders over
        and over again, the cache can end up doing more harm than good. In this case,
        you can call this function with True and future list requests will go directly
        to the server, bypassing the cache.
    """
def close_cached_file(handle: Request) -> None:
    """
    Close a cached file handle.

    This function closes a file handle that was opened with :py:func:`omni.client.open_cached_file_with_callback`.
    This allows the file to be garbage collected and frees up system resources.

    Args:
        handle: The Request object returned by :py:func:`omni.client.open_cached_file_with_callback`.

    Note:
        After calling this function, the local file path from the original callback is no longer
        valid and should not be used. The file may be removed from the cache if it's no longer
        needed by other clients.
    """
def combine_urls(base_url: str, other_url: str) -> str:
    """
    Combine two URLs into a single URL.

    This function combines a base URL and another URL (which may be relative) into a single
    resolved URL. The combination follows standard URL resolution rules as defined by RFC 3986.

    Args:
        base_url: The base URL to resolve against.
        other_url: The URL to combine with the base URL (may be relative or absolute).

    Returns:
        A string containing the combined URL.

    Note:
        This function is useful for resolving relative URLs in the context of a base URL.
    """
def combine_with_base_url(other_url: str) -> str:
    """
    Combine a URL with the current base URL stack.

    This function combines the provided URL with the URL on top of the base URL stack,
    as set by :py:func:`omni.client.push_base_url`. This is useful for resolving relative
    URLs in the context of a previously set base URL.

    Args:
        other_url: The URL to combine with the current base URL (may be relative or absolute).

    Returns:
        A string containing the combined URL.

    Note:
        The base URL stack is thread-local, so each thread can have its own base URL context.
    """
def copy_file_with_callback(src_url: str, dst_url: str, callback: typing.Callable[[Result], None], behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = None) -> Request:
    """
    Copy a file from ``src_url`` to ``dst_url``.

    This operation will fail with Result.ERROR_WRONG_TYPE if the item at 'src_url' is not a file.
    It will fail with Result.ERROR_NOT_FOUND if the item at 'src_url' does not exist.
    It will fail with Result.ERROR_ALREADY_EXISTS if the item at 'dst_url' already exists and 'behavior' is CopyBehavior.ERROR_IF_EXISTS.
    It will also fail with Result.ERROR_ALREADY_EXISTS if the item at 'dst_url' exists but is not a file and 'behavior' is CopyBehavior.OVERWRITE.

    Destination folders will be created as needed.

    Args:
        src_url: Source url.
        dst_url: Destination url.
        callback: Callback to be called with the result.
        behavior: Behavior if the destination exists (CopyBehavior.ERROR_IF_EXISTS or CopyBehavior.OVERWRITE).
        message: Message to apply to atomic checkpoint of destination url.

    Returns:
        Request object.
    """
def copy_folder_with_callback(src_url: str, dst_url: str, callback: typing.Callable[[Result], None], behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = None) -> Request:
    """
    Recursively copy a folder from ``src_url`` to ``dst_url``.

    This operation will fail with Result.ERROR_WRONG_TYPE if the item at 'src_url' is not a folder.
    It will fail with Result.ERROR_NOT_FOUND if the item at 'src_url' does not exist.
    It will fail with Result.ERROR_ALREADY_EXISTS if the item at 'dst_url' already exists and 'behavior' is CopyBehavior.ERROR_IF_EXISTS.
    It will also fail with Result.ERROR_ALREADY_EXISTS if the item at 'dst_url' exists but is not a folder and 'behavior' is CopyBehavior.OVERWRITE.

    Setting 'behavior' to CopyBehavior.OVERWRITE will overwrite each individual file inside the folder, but will not remove files that exist in 'dst_url' but not in 'src_url'.
    Trailing slashes are ignored.

    Destination folders will be created as needed.

    Args:
        src_url: Source url.
        dst_url: Destination url.
        callback: Callback to be called with the result.
        behavior: Behavior if the destination exists (CopyBehavior.ERROR_IF_EXISTS or CopyBehavior.OVERWRITE).
        message: Message to apply to atomic checkpoint of destination url.

    Returns:
        Request object.
    """
def copy_with_callback(src_url: str, dst_url: str, callback: typing.Callable[[Result], None], behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = None) -> Request:
    """
    Copy a thing from ``src_url`` to ``dst_url``.

    This is equivalent to first checking the type of the item at 'src_url' and then copying it as either a file or a folder. The copy is done server-side if both 'src_url' and 'dst_url' are on the same server. Otherwise, it is downloaded from 'src_url' and then uploaded to 'dst_url'.

    Destination folders will be created as needed.

    Args:
        src_url: Source url.
        dst_url: Destination url.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
        behavior: Behavior if the destination exists:
                 - CopyBehavior.ERROR_IF_EXISTS: Fail if destination exists (default)
                 - CopyBehavior.OVERWRITE: Overwrite if destination exists
        message: Optional message to apply to the checkpoint created after the copy operation.

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        If the source doesn't exist, the result will be Result.ERROR_NOT_FOUND.
        If the destination already exists and behavior is ERROR_IF_EXISTS, the result will be Result.ERROR_ALREADY_EXISTS.
        If you don't have permission to access the source or write to the destination, the result will be Result.ERROR_ACCESS_DENIED.
    """
def create_checkpoint_with_callback(*args, **kwargs) -> typing.Any:
    """
    Create a checkpoint for a file.

    This function creates a checkpoint (version) of the specified file. Checkpoints allow
    you to save the current state of a file and return to it later if needed. The checkpoint
    includes a comment that describes what changes were made.

    Args:
        url: URL of file to create a checkpoint for.
        comment: Comment to associate with the checkpoint describing the changes made.
        force: If true, create a checkpoint even if there are no changes since the last checkpoint.
               If false, only create a checkpoint if there are actual changes.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - checkpoint_query: String containing a query that can be used to reference this checkpoint

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        You must have write permissions to create checkpoints. If checkpoints are not enabled
        on the server, the result will be Result.ERROR_NOT_SUPPORTED. The checkpoint_query
        can be used with other functions to reference this specific version of the file.
    """
def create_folder_with_callback(url: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Create a folder.

    This function creates a new folder at the specified URL. If the folder already exists,
    the operation will fail.

    Args:
        url: URL of folder to create.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        If the folder already exists, the result will be Result.ERROR_ALREADY_EXISTS.
        If you don't have permission to create folders at the specified location, the result
        will be Result.ERROR_ACCESS_DENIED.
    """
def create_group_with_callback(url: str, group: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Create a group.

    This function creates a new group with the specified name on the server for the given URL.

    Args:
        url: The URL of the server or resource where the group should be created.
        group: The name of the group to create.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        You must have administrative permissions to create groups. If the group already exists,
        the result will be Result.ERROR_ALREADY_EXISTS.
    """
def create_with_hash_with_callback(url: str, hash: str, overwrite: bool, callback: typing.Callable[[Result, str, str], None], message: str = None) -> Request:
    """
    Create a new file with the content the hash describes, will fail if the server doesn't know the hash

    Args:
        url: URL of file to create.
        hash: Hash of content.
        overwrite: Allow to overwrite an existing file or fail if file exists
        callback: Callback to be called with the result.
        message: Message to apply to atomic checkpoint of destination url.

    Returns:
        Request object.
    """
def delete_single_with_callback(url: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Delete a file or an empty folder.

    This function performs a "soft delete" operation on a single item. Unlike the general delete
    function, this will fail if trying to delete a non-empty folder.

    Args:
        url: URL of item to delete.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        This is a soft delete operation. The item can be restored using :py:func:`omni.client.undelete_with_callback`.
        If the folder is not empty, the result will be Result.ERROR_FOLDER_NOT_EMPTY.
        If the item doesn't exist, the result will be Result.ERROR_NOT_FOUND.
        If you don't have permission to delete the item, the result will be Result.ERROR_ACCESS_DENIED.
    """
def delete_with_callback(url: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Delete something (file, folder, mount, live object, channel etc..).

    This function performs a "soft delete" operation, which moves the item to a deleted state
    but preserves it for potential recovery. The item can be restored using :py:func:`omni.client.undelete_with_callback`.

    Args:
        url: URL of item to delete.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        This is a soft delete operation. For permanent deletion, use :py:func:`omni.client.obliterate_with_callback`.
        If the item doesn't exist, the result will be Result.ERROR_NOT_FOUND.
        If you don't have permission to delete the item, the result will be Result.ERROR_ACCESS_DENIED.
    """
def enable_nucleus_cache_bypass(bypass_on: bool) -> bool:
    """
    Enable or disable Nucleus Cache bypass (for unit tests only).

    This function controls whether the client library bypasses the Nucleus cache and goes
    directly to the server for all operations. This is primarily intended for unit testing
    scenarios where you want to ensure fresh data from the server.

    Args:
        bypass_on: True to bypass the cache, False to use the cache.

    Returns:
        True if cache bypass is enabled after the call, False otherwise.

    Note:
        This function is intended for unit tests only and should not be used in production code.
    """
def get_acls_with_callback(url: str, callback: typing.Callable[[Result, typing.List[AclEntry]], None]) -> Request:
    """
    Get the ACLs (Access Control Lists) on a folder or file.

    This function retrieves the current access control list for the specified item. The ACL
    contains information about which users and groups have what level of access to the item.

    Args:
        url: URL of item to get the ACLs for.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - acls: List of AclEntry objects containing user/group names and their access levels

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        Each AclEntry contains a name (user or group) and access flags indicating what
        operations that user/group can perform. If you don't have permission to view ACLs
        for this item, the result will be Result.ERROR_ACCESS_DENIED.
    """
def get_base_url() -> str:
    """
    Returns the top of the base URL stack.

    This function returns the base URL that is currently at the top of the thread-local
    base URL stack, without removing it from the stack.

    Returns:
        str: The top of the base URL stack, or None if the stack is empty.

    Note:
        This function is useful for checking the current base URL context without
        modifying the stack.
    """
def get_branch_and_checkpoint_from_query(query: str) -> tuple:
    """
    Extract the branch and checkpoint from a query parameter.

    This function parses a query string to extract branch and checkpoint information.
    The query can be in either expanded format ("branch=my_branch&checkpoint=30") or
    shortened format ("my_branch&30").

    Args:
        query: The query string to parse, containing branch and checkpoint information

    Returns:
        A tuple containing (branch_name, checkpoint_number) or (None, None) if parsing fails.

    Note:
        The function handles both the full query format with parameter names and
        the shortened format where only values are provided.
    """
def get_default_search_paths() -> typing.List[str]:
    """
    Retrieve the current list of default search paths.

    This function returns the current list of default search paths that are used by
    :py:func:`omni.client.resolve` when no explicit search paths are provided.

    Returns:
        List[str]: The list of default search paths, in order of priority (newest first).

    Note:
        The returned list is a copy of the internal search path list. Modifying this
        list will not affect the actual search paths used by resolve.
    """
def get_group_users_with_callback(url: str, group: str, callback: typing.Callable[[Result, typing.List[str]], None]) -> Request:
    """
    Get a list of users in a group.

    This function retrieves all users that belong to the specified group on the server.
    The callback will be called with the list of user names.

    Args:
        url: The URL of the server to get group users from
        group: The name of the group to get users for
        callback: Callback function that receives the list of users

    Returns:
        A Request object that can be used to control the operation.

    Note:
        The callback receives a list of user names as strings.
        This operation requires appropriate permissions on the server.
    """
def get_groups_with_callback(url: str, callback: typing.Callable[[Result, typing.List[str]], None]) -> Request:
    """
    Get a list of all groups.

    This function retrieves all groups registered with the specified server.
    The callback will be called with the list of group names.

    Args:
        url: The URL of the server to get groups from
        callback: Callback function that receives the list of groups

    Returns:
        A Request object that can be used to control the operation.

    Note:
        The callback receives a list of group names as strings.
        This operation requires appropriate permissions on the server.
    """
def get_hub_http_uri_with_callback(callback: typing.Callable[[Result, str], None]) -> Request:
    """
    Get the HTTP URI of the connected Hub.

    This function retrieves the HTTP URI of the Hub server that this client is connected to.
    This URI can be used for direct HTTP communication with the Hub server.

    Args:
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - uri: String containing the Hub HTTP URI

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        This function requires an active connection to a Hub server. If not connected,
        the result will be Result.ERROR_CONNECTION.
    """
def get_hub_version_with_callback(callback: typing.Callable[[Result, str], None]) -> Request:
    """
    Get the version of the connected Hub.

    This function retrieves the version information of the Hub server that this client
    is connected to. This can be useful for determining server capabilities or for
    debugging connection issues.

    Args:
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - version: String containing the Hub version information

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        This function requires an active connection to a Hub server. If not connected,
        the result will be Result.ERROR_CONNECTION.
    """
def get_local_file_with_callback(*args, **kwargs) -> typing.Any:
    """
    DEPRECATED: Use :py:func:`omni.client.open_cached_file_with_callback` instead.
    """
def get_server_info_with_callback(url: str, callback: typing.Callable[[Result, ServerInfo], None]) -> Request:
    """
    Retrieve information about the server for a specified URL.

    This function retrieves server information including version, username, authentication token,
    connection ID, and various feature flags like cache, omni-objects, checkpoints, and undelete support.

    Args:
        url: The URL of the server to get information about
        callback: Callback to be called with the results. The callback receives:
                 - result: Result indicating success or failure
                 - server_info: ServerInfo object containing server details, or None if result is not Ok

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        If this function is called after :py:func:`omni.client.shutdown`, kInvalidRequestId will be returned, 
        and the callback will not be called.
        
        The authentication token returned in the server info should not be used for external service calls
        as it may expire. Use :py:func:`omni.client.refresh_auth_token_with_callback` to get a fresh token.
    """
def get_user_groups_with_callback(url: str, user: str, callback: typing.Callable[[Result, typing.List[str]], None]) -> Request:
    """
    Retrieve the groups a user is in.

    This function retrieves all groups that the specified user belongs to on the server.
    The callback will be called with the list of group names.

    Args:
        url: The URL of the server to get user groups from
        user: The name of the user to get groups for
        callback: Callback function that receives the list of groups

    Returns:
        A Request object that can be used to control the operation.

    Note:
        The callback receives a list of group names as strings.
        This operation requires appropriate permissions on the server.
    """
def get_users_with_callback(url: str, callback: typing.Callable[[Result, typing.List[str]], None]) -> Request:
    """
    Get a list of all users.

    This function retrieves all users registered with the specified server.
    The callback will be called with the list of user names.

    Args:
        url: The URL of the server to get users from
        callback: Callback function that receives the list of users

    Returns:
        A Request object that can be used to control the operation.

    Note:
        The callback receives a list of user names as strings.
        This operation requires appropriate permissions on the server.
    """
def get_version() -> str:
    """
    Get the version of the client library being used.

    Returns:
        Returns a human readable version string.
    """
def initialize(version: int = 563237716230144) -> bool:
    """
    Initialize the client library.

    Returns:
        False if the library failed to initialize.
    """
def join_channel_with_callback(url: str, callback: typing.Callable[[Result, ChannelEvent, str, Content], None]) -> Request:
    """
    Join a channel for real-time communication.

    This function joins a channel that allows real-time communication with other clients
    connected to the same channel. The callback will be called for various channel events
    such as when other users join, leave, or send messages.

    Args:
        url: URL of the channel to join.
        callback: Callback to be called with channel events. The callback receives:
                 - result: Result indicating success or failure
                 - event_type: ChannelEvent indicating the type of event (Message, Join, Leave, etc.)
                 - from_user: String containing the username of the user who triggered the event
                 - content: Content object containing the message data (for Message events)

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        This is a recurring callback that will be called multiple times for different channel
        events. The callback will continue to receive events until you stop the request or
        leave the channel. You can send messages to the channel using :py:func:`omni.client.send_message_with_callback`.
    """
def list_bookmarks_with_callback(callback: typing.Callable[[typing.Dict[str, str]], None]) -> Request:
    """
    Retrieve a list of bookmarks. The callback is called any time the list changes (by this application or any other).

    This function retrieves the current list of bookmarks and sets up a subscription
    to receive notifications when the bookmark list changes.

    Args:
        callback: Callback function that receives the list of bookmarks

    Returns:
        A Request object that can be used to control the operation.

    Note:
        The callback is called once with the initial list of bookmarks, and then
        again any time the bookmark list is modified by any application.
        Call stop() on the returned request to stop receiving bookmark updates.
    """
def list_checkpoints_with_callback(url: str, callback: typing.Callable[[Result, typing.List[ListEntry]], None]) -> Request:
    """
    List checkpoints for a file.

    This function retrieves a list of all checkpoints (versions) that have been created for
    the specified file. Each checkpoint entry contains information about when it was created,
    who created it, and any comments associated with it.

    Args:
        url: URL of file to list the checkpoints of.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - entries: List of ListEntry objects containing checkpoint information

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        You must have read permissions to list checkpoints. If checkpoints are not enabled
        on the server, the result will be Result.ERROR_NOT_SUPPORTED. Each ListEntry contains
        information such as the checkpoint comment, creation time, and creator.
    """
def list_subscribe_with_callback(url: str, list_callback: typing.Callable[[Result, typing.List[ListEntry]], None], subscribe_callback: typing.Callable[[Result, ListEvent, ListEntry], None], include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Request:
    """
    Subscribe to change notifications for a url.

    '`list_callback` is called once with the initial list,
     then '`subscribe_callback`' may be called multiple times after that as items change.

    Args:
        url: URL of folder to subscribe to.
        list_callback: Callback to be called once with the list.
        subscribe_callback: Callback to be called when changes happen.
        include_deleted_option: Option to include deleted files (default NO_DELETED_FILES)

    Returns:
        Subscription object.
    """
def list_with_callback(url: str, callback: typing.Callable[[Result, typing.List[ListEntry]], None], include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Request:
    """
    List content of a folder.

    This function retrieves a list of files and folders in the specified directory.

    Args:
        url: URL of a folder to list the contents of.
        callback: Callback to be called with the results. The callback receives:
                 - result: Result indicating success or failure
                 - entries: List of ListEntry objects containing file/folder information
        include_deleted_option: Option to include deleted files:
                              - ListIncludeOption.DEFAULT_NOT_DELETED: List only non-deleted files (default)
                              - ListIncludeOption.INCLUDE_DELETED: List both deleted and non-deleted files
                              - ListIncludeOption.ONLY_DELETED: List only deleted files

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        Each ListEntry contains information such as relative path, access flags, size,
        modification time, version, hash, and metadata about who created/modified the item.
    """
def live_get_latest_server_time(url: str) -> int:
    """
    Get the latest server timestamp.

    This function returns the server timestamp of the most recently received live update
    message for the specified server. This can be used to determine how up-to-date your
    local state is compared to the server.

    Args:
        url: URL of server to get the latest timestamp for. Only the "prefix" such as
             "omniverse://content.ov.nvidia.com" is needed, the path is ignored.

    Returns:
        Server timestamp of the most recently received message, or 0 if no messages have been received.

    Note:
        This timestamp can be used with :py:func:`omni.client.live_process_up_to` to process
        updates up to a specific point in time.
    """
def live_process() -> None:
    """
    Process live updates received from the server.

    This function processes any live updates that have been queued since the last call.
    Live updates are notifications about changes to files that you're subscribed to.
    You should call this function regularly from your main application loop after
    receiving notifications from :py:func:`omni.client.live_register_queued_callback`.

    Note:
        This function processes all available updates for all servers. If you want to
        process updates only up to a specific server time, use :py:func:`omni.client.live_process_up_to`.
    """
def live_process_up_to(url: str, server_time: int) -> None:
    """
    Process live updates up to a specific server time.

    This function is similar to :py:func:`omni.client.live_process` but allows you to specify
    a server time limit. Updates will only be processed up to the specified server time,
    which can be useful for controlling the rate of update processing.

    Args:
        url: URL of server to process updates for. Only the "prefix" such as "omniverse://content.ov.nvidia.com" is needed, the path is ignored.
        server_time: The server time to stop processing updates. Only updates with timestamps
                   less than or equal to this time will be processed.

    Note:
        This function is useful when you want to process updates in controlled batches
        or when you need to ensure updates are processed in chronological order.
    """
def live_register_queued_callback(callback: typing.Callable[[LiveUpdateType, Result, str, int, int, int], None]) -> Registration:
    """
    Register a callback for live update notifications.

    This function registers a callback that will be called whenever a live update is received
    from the server. The callback is intended to notify you that you should call
    :py:func:`omni.client.live_process` to process the queued updates.

    Args:
        callback: Callback to be called with information about the live update. The callback receives:
                 - update_type: LiveUpdateType indicating the type of update (Remote, Local, More)
                 - result: Result indicating success or failure
                 - url: String containing the URL of the file being updated
                 - object_id: Object ID of the update
                 - sequence_num: Sequence number of the update
                 - server_time: Server timestamp when the update was sent

    Returns:
        Subscription Object. Callback will be unregistered once subscription is released.

    Note:
        DO NOT call :py:func:`omni.client.live_process` from within the callback function!
        The callback is just a notification that updates are available. Process the updates
        from your main application loop by calling :py:func:`omni.client.live_process`.
    """
def live_set_queued_callback(callback: typing.Callable[[], None]) -> None:
    """
    DEPRECATED: Use :py:func:`omni.client.live_register_queued_callback` instead.
    """
def live_wait_for_pending_updates() -> None:
    """
    Wait for all pending live updates to complete.

    This function blocks until all pending live updates have been processed. This is
    useful when you want to ensure that all updates have been applied before continuing
    with other operations.

    Note:
        This function will block until all queued updates are processed. Use this
        carefully to avoid blocking your application for extended periods.
    """
def lock_with_callback(url: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Lock a file so only this client can modify it.

    This function acquires an exclusive lock on the specified file, preventing other clients
    from modifying it until the lock is released. This is useful for preventing conflicts
    when multiple users might be working on the same file.

    Args:
        url: URL of file to lock.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        If the file is already locked by another client, the result will be Result.ERROR_LOCKED.
        If you don't have permission to lock the file, the result will be Result.ERROR_ACCESS_DENIED.
        The lock will remain active until you call :py:func:`omni.client.unlock_with_callback` or
        disconnect from the server.
    """
def make_file_url(path: str) -> str:
    """
    Returns a "file:" URL for the given `path`.

    This function converts a local file path to a proper "file:" URL format.
    The conversion follows the rules defined by the File URI scheme standard.

    Args:
        path: The local file path to convert (e.g., "C:\\\\Users\\\\file.txt" on Windows or "/home/user/file.txt" on Linux)

    Returns:
        A "file:" URL string representing the local file path.

    Note:
        The function handles platform-specific path separators and converts them
        to the proper URL format. On Windows, backslashes are converted to forward slashes.
    """
def make_printable(url: str) -> str:
    """
    Returns a URL which is safe for printing.

    This function returns a URL that is safe for printing by removing or escaping any invalid
    UTF-8 sequences or ASCII control characters.

    Args:
        url: The URL to make printable.

    Returns:
        A string containing the printable URL.

    Note:
        Use this function before displaying URLs in logs or user interfaces to avoid encoding issues.
    """
def make_query_from_branch_and_checkpoint(branch: str, checkpoint: int) -> str:
    """
    Return a query parameter that can be used to reference this branch and checkpoint.

    This function creates a query string that can be appended to a URL to reference
    a specific branch and checkpoint combination.

    Args:
        branch: The branch name to reference
        checkpoint: The checkpoint number to reference

    Returns:
        A query string that can be used to reference the specified branch and checkpoint.

    Note:
        The returned query string follows the format "branch=<branch>&checkpoint=<checkpoint>"
        and can be directly appended to URLs for version-specific references.
    """
def make_relative_url(base_url: str, other_url: str) -> str:
    """
    Returns a url which will result in `other_url`, when combined with `base_url`.

    This function creates a relative URL that, when combined with the base URL using
    the URL combination rules, will result in the specified other URL.

    Args:
        base_url: The base URL to make relative to
        other_url: The target URL that should result from the combination

    Returns:
        A relative URL string that can be combined with base_url to produce other_url.

    Note:
        The function attempts to create the shortest possible relative URL while
        guaranteeing that combining it with base_url will produce other_url.
        Trailing slashes in the base URL affect the resulting relative path.
    """
def make_url(scheme: str = None, user: str = None, host: str = None, port: str = None, path: str = None, query: str = None, fragment: str = None) -> str:
    """
    Compose a URL from the provided parts.

    This function creates a URL by combining the individual components (scheme, host, port, path, etc.)
    into a properly formatted URL string. The components are percent-encoded as needed according to
    URL standards.

    Args:
        scheme: The URL scheme (e.g., "http", "https", "omniverse", "file")
        user: The username for authentication (optional)
        host: The hostname or IP address
        port: The port number (optional)
        path: The path component of the URL
        query: The query string (optional)
        fragment: The fragment identifier (optional)

    Returns:
        A properly formatted URL string combining all the provided components.

    Note:
        If any component is None or empty, it will be omitted from the final URL.
    """
def move_file_with_callback(src_url: str, dst_url: str, callback: typing.Callable[[Result, bool], None], behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = None) -> Request:
    """
    Move a file from ``src_url`` to ``dst_url``.

    This operation fails with Result.ERROR_WRONG_TYPE if 'src_url' is not a file, with Result.ERROR_NOT_FOUND if 'src_url' doesn't exist, and with Result.ERROR_ALREADY_EXISTS if 'dst_url' already exists and 'behavior' is CopyBehavior.ERROR_IF_EXISTS, or if 'dst_url' exists but is not a file and 'behavior' is CopyBehavior.OVERWRITE.

    The move is done server-side if both 'src_url' and 'dst_url' are on the same server. Otherwise, it is first copied, then deleted from 'src_url'. Note: It is possible for the copy to succeed and the delete to fail.

    Destination (parent) folders will be created as needed.

    Args:
        src_url: Source url.
        dst_url: Destination url.
        callback: Callback to be called with the result.
        behavior: Behavior if the destination exists (CopyBehavior.ERROR_IF_EXISTS or CopyBehavior.OVERWRITE).
        message: Message to apply to atomic checkpoint of destination url.

    Returns:
        Request object.
    """
def move_folder_with_callback(src_url: str, dst_url: str, callback: typing.Callable[[Result, bool], None], behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = None) -> Request:
    """
    Recursively move a folder from ``src_url`` to ``dst_url``.

    This operation fails with Result.ERROR_WRONG_TYPE if 'src_url' is not a folder, with Result.ERROR_NOT_FOUND if 'src_url' doesn't exist, and with Result.ERROR_ALREADY_EXISTS if 'dst_url' already exists and 'behavior' is CopyBehavior.ERROR_IF_EXISTS, or if 'dst_url' exists but is not a folder and 'behavior' is CopyBehavior.OVERWRITE.

    The move is done server-side if both 'src_url' and 'dst_url' are on the same server. Otherwise, it is first copied, then deleted from 'src_url'. Note: It is possible for the copy to succeed and the delete to fail.

    Destination folders will be created as needed. Trailing slashes are ignored.

    Args:
        src_url: Source url.
        dst_url: Destination url.
        callback: Callback to be called with the result.
        behavior: Behavior if the destination exists (CopyBehavior.ERROR_IF_EXISTS or CopyBehavior.OVERWRITE).
        message: Message to apply to atomic checkpoint of destination url.

    Returns:
        Request object.
    """
def move_with_callback(src_url: str, dst_url: str, callback: typing.Callable[[Result, bool], None], behavior: CopyBehavior = CopyBehavior.ERROR_IF_EXISTS, message: str = None) -> Request:
    """
    Move a thing from ``src_url`` to ``dst_url``.

    This is equivalent to first checking the type of the item at 'src_url' and then moving it as either a file or a folder. The move is done server-side if both 'src_url' and 'dst_url' are on the same server. Otherwise, it is first copied from 'src_url' to 'dst_url', then deleted from 'src_url'.

    Note: It is possible for the copy to succeed and the delete to fail, resulting in an error code but with 'copied' being true. If the result is 'Ok' but 'copied' is false, the move was done entirely on the server, and no local copy was made.

    Destination folders will be created as needed.

    Args:
        src_url: Source url.
        dst_url: Destination url.
        callback: Callback to be called with the result.
        behavior: Behavior if the destination exists (CopyBehavior.ERROR_IF_EXISTS or CopyBehavior.OVERWRITE).
        message: Message to apply to atomic checkpoint of destination url.

    Returns:
        Request object.
    """
def normalize_url(url: str) -> str:
    """
    Normalize a URL by parsing it then recomposing it.

    This function parses the provided URL and then recomposes it into a normalized form.
    Normalization may include percent-encoding, removing redundant path segments, and
    standardizing the URL format.

    Args:
        url: The URL to normalize.

    Returns:
        A string containing the normalized URL.

    Note:
        Use this function to ensure URLs are in a canonical form before using them with
        other client library functions.
    """
def obliterate_with_callback(url: str, obliterate_checkpoints: bool, callback: typing.Callable[[Result], None]) -> Request:
    """
    Obliterate a path

    Doesn't support recursive removal, doesn't support wildcards
    Supports branches / checkpoints
    Only empty folders can be obliterated

    Args:
        url: URL of item to delete.
        obliterate_checkpoints: whether to obliterate all checkpoints
        callback: Callback to be called with the result of the operation

    Returns:
        Request object.
    """
def open_cached_file_with_callback(*args, **kwargs) -> typing.Any:
    """
    Open a file from the cache.

    This function retrieves the local file path for a cached file. If the file is not already
    cached and download is true, it will be downloaded first. The returned Request object
    should be kept alive while the file is being used, and then closed using :py:func:`omni.client.close_cached_file`.

    Args:
        url: URL of file to get the local path for.
        download: If true, download the file if it's not already cached. If false, return an error
                 if the file has not already been downloaded.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - request: The Request object that should be kept alive while using the file
                 - local_file_path: String containing the local file path, or empty string if result is not Ok

    Returns:
        Request object that should be kept alive while the file is being used.

    Note:
        The local file path is only valid while the Request object is alive. Once you're done
        with the file, call :py:func:`omni.client.close_cached_file` to allow the file to be
        garbage collected. If the file doesn't exist and download is false, the result will be
        Result.ERROR_NOT_FOUND.
    """
def pop_base_url(url: str) -> bool:
    """
    Pop a URL off the base URL stack.

    This function removes the top URL from the base URL stack that was previously pushed
    using :py:func:`omni.client.push_base_url`.

    Args:
        url: The URL that was popped from the stack (output parameter).

    Note:
        This function removes the URL from the stack and returns it in the url parameter.
        If the stack is empty, the behavior is undefined.
    """
def push_base_url(url: str) -> None:
    """
    Push a URL onto the base URL stack.

    This function pushes a URL onto an internal stack that is used by :py:func:`omni.client.combine_with_base_url`.
    The base URL stack allows you to set a context URL that can be combined with relative URLs.

    Args:
        url: The URL to push onto the base URL stack.

    Note:
        The base URL stack is used to provide context for relative URL resolution.
        You can pop URLs from the stack using :py:func:`omni.client.pop_base_url`.
    """
def read_file_with_callback(url: str, callback: typing.Callable[[Result, str, Content], None]) -> Request:
    """
    Read a file.

    This function reads the content of a file from the specified URL and returns both
    the file content and version information.

    Args:
        url: URL of file to read.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
                 - version: String containing the version of the file that was read
                 - content: Content object containing the file data, or None if result is not Ok

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        The Content object provides access to the file data as bytes and can be used
        like a buffer. If the file doesn't exist, the result will be Result.ERROR_NOT_FOUND.
        If you don't have access to the file, the result will be Result.ERROR_ACCESS_DENIED.
    """
def reconnect(url: str) -> None:
    """
    Reconnect to a URL after a failure.

    The client library doesn't automatically reconnect after failures.

    This triggers a background reconnect attempt, you can call a function such as :py:func:`omni.client.stat`
    or use :py:func:`omni.client.register_connection_status_callback` to determine if the reconnect attempt was successful.

    Args:
        url: Attempt to connect to this url
    """
def refresh_auth_token_with_callback(url: str, callback: typing.Callable[[Result, str], None]) -> Request:
    """
    Refresh the auth token for a given URL.

    Nucleus auth tokens (as received by :py:func:`omni.client.get_server_info_with_callback`) expire after some time. 
    If you attempt to connect to an external service using that auth token, and Nucleus responds with an error 
    indicating that the token is invalid, you may call this function to refresh the auth token. You will receive 
    a new auth token in the callback (or an error) and all future calls to :py:func:`omni.client.get_server_info_with_callback` 
    will also return the new auth token.

    Args:
        url: The URL of the server to refresh the auth token for
        callback: Callback to be called with the results. The callback receives:
                 - result: Result indicating success or failure
                 - auth_token: String containing the new authentication token, or empty string if result is not Ok

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        If this function is called after :py:func:`omni.client.shutdown`, kInvalidRequestId will be returned, 
        and the callback will not be called.
        
        The refreshed token can be used for external service calls that require authentication.
    """
def register_authentication_callback(callback: typing.Callable[[str], object]) -> Registration:
    """
    Register an authentication callback.

    The callback receives the URL prefix (such as "scheme://server:port") as a parameter and should return either:
        * None or False: Continue to the next authentication callback (or default authentication method)
        * AUTH_ABORT: Abort the connection
        * String: The auth_token provided by get_server_info
        * (String, String): A username and password or you can return ("$omni-api-token", api_token) to use an API token.

    Args:
        callback: Callback to be called to provide authentication information.

    Returns:
        Subscription Object. Callback will be unregistered once subscription is released.

    Note:
        This function is called when the library needs authentication information to connect to a server.
        The callback should return the appropriate authentication data based on the URL prefix provided.
    """
def register_authorize_callback(callback: typing.Callable[[str], object]) -> Registration:
    """
    DEPRECATED - Use register_authentication_callback
    """
def register_connection_status_callback(callback: typing.Callable[[str, ConnectionStatus], None]) -> Registration:
    """
    Register connection status callback.

    This callback is called whenever the connection status to a server changes, such as when
    connecting, disconnecting, or encountering authentication errors.

    Args:
        callback: Callback to be called with the status. The callback receives:
                 - url: String containing the server URL
                 - status: ConnectionStatus enum value indicating the connection state

    Returns:
        Subscription Object. Callback will be unregistered once subscription is released.

    Note:
        Common status values include:
        - ConnectionStatus.CONNECTING: Attempting to connect
        - ConnectionStatus.CONNECTED: Successfully connected
        - ConnectionStatus.DISCONNECTED: Disconnected after a successful connection
        - ConnectionStatus.AUTH_FAILED: Authentication failed
        - ConnectionStatus.CONNECT_ERROR: Error while trying to connect
    """
def register_device_flow_auth_callback(callback: typing.Callable[[int, AuthDeviceFlowParams], None]) -> Registration:
    """
    Register a "Device Flow" authentication callback.

    If _any_ device flow auth callbacks are registered, we will prefer the device flow auth instead of launching a web browser.

    Args:
        callback: Function to be called when performing device flow auth.
                  It receives an auth handle (which can be used with `authentication_cancel`) and an object containing information
                  that you should display to the user to complete authentication. If the information object is `None` that means the
                  authentication attempt is finished (either sucessfully or not, register a connection status callback to determine which).

    Returns:
        Subscription Object. The callback will be unregistered once subcription is released.
    """
def register_file_status_callback(callback: typing.Callable[[str, FileStatus, int], None]) -> Registration:
    """
    Register file status callback.

    This callback is called to provide progress information during file operations such as
    reading, writing, copying, moving, or deleting files.

    Args:
        callback: Callback to be called with the status. The callback receives:
                 - url: String containing the file URL being operated on
                 - status: FileStatus enum value indicating the operation type
                 - percent: Integer percentage (0-100) indicating progress

    Returns:
        Subscription Object. Callback will be unregistered once subscription is released.

    Note:
        Common status values include:
        - FileStatus.READING: Reading a file
        - FileStatus.WRITING: Writing a file
        - FileStatus.COPYING: Copying a file
        - FileStatus.MOVING: Moving a file
        - FileStatus.DELETING: Deleting a file
        - FileStatus.LISTING: Performing a list operation
    """
def remove_bookmark(name: str) -> None:
    """
    Remove a bookmark.

    This function removes a bookmark from the local bookmark list.
    The bookmark is identified by its name.

    Args:
        name: The name of the bookmark to remove

    Note:
        If the bookmark with the specified name doesn't exist, this function
        will complete successfully without any effect.
    """
def remove_default_search_path(search_path: str) -> None:
    """
    Remove a default search path from the list of search paths used by resolve.

    This function removes a search path from the default search path list that is used by
    :py:func:`omni.client.resolve` when no explicit search paths are provided.

    Args:
        search_path: The search path to remove from the default list.

    Note:
        If the search path is not in the list, this function has no effect.
    """
def remove_group_with_callback(url: str, group: str, callback: typing.Callable[[Result, int], None]) -> Request:
    """
    Remove a group.

    This function removes a group from the server.
    The callback will be called when the operation completes.

    Args:
        url: The URL of the server to remove the group from
        group: The name of the group to remove
        callback: Callback function that receives the operation result

    Returns:
        A Request object that can be used to control the operation.

    Note:
        This operation requires administrative permissions on the server.
        The group must exist and should not have any remaining members.
    """
def remove_user_from_group_with_callback(url: str, user: str, group: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Remove a user from a group.

    This function removes a user from the specified group on the server.
    The callback will be called when the operation completes.

    Args:
        url: The URL of the server to remove the user from the group on
        user: The name of the user to remove
        group: The name of the group to remove the user from
        callback: Callback function that receives the operation result

    Returns:
        A Request object that can be used to control the operation.

    Note:
        This operation requires appropriate permissions on the server.
        The user must exist and be a member of the specified group.
    """
def rename_group_with_callback(url: str, group: str, new_group: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Rename a group.

    This function renames an existing group on the server.
    The callback will be called when the operation completes.

    Args:
        url: The URL of the server to rename the group on
        group: The current name of the group
        new_group: The new name for the group
        callback: Callback function that receives the operation result

    Returns:
        A Request object that can be used to control the operation.

    Note:
        This operation requires administrative permissions on the server.
        The group must exist and the new name must not conflict with existing groups.
    """
def resolve_subscribe_with_callback(url: str, search_urls: typing.List[str], resolve_callback: typing.Callable[[Result, ListEntry, str], None], subscribe_callback: typing.Callable[[Result, ListEvent, ListEntry, str], None]) -> Request:
    """
    Resolve & subscribe to change notifications for a url.

    Performs 'resolve' but also establishes a subscription so you will be notified if the resolution changes.

    If 'url' is a file, you will only receive information about that file.
    If 'url' is a folder, you will only receive information about that folder.
    '`resolve_callback` is called once with the initial resolve info,then '`subscribe_callback`' may be called multiple times after that the item changes.

    Args:
        url: URL of item to resolve. Can be relative or absolute.
        search_urls: List of URLs to search.
        resolve_callback: Callback to be called once with the initial resolve.
        subscribe_callback: Callback to be called when changes happen.

    Returns:
        Subscrption object.
    """
def resolve_with_callback(url: str, search_urls: typing.List[str], callback: typing.Callable[[Result, ListEntry, str], None]) -> Request:
    """
    Resolve a file or folder, looking in the search paths for it.

    Args:
        url: URL of item to resolve.
        search_urls: List of URLs to search.
        callback: Callback to be called with the results.

    Returns:
        Request object.
    """
def send_message_with_callback(join_request_id: int, content: buffer, callback: typing.Callable[[Result], None]) -> Request:
    """
    Send a message to a channel.

    This function sends a message to a channel that you have previously joined using
    :py:func:`omni.client.join_channel_with_callback`. The message will be received by
    all other clients currently joined to the same channel.

    Args:
        join_request_id: The Request.id that you received from :py:func:`omni.client.join_channel_with_callback`.
        content: Message content as a buffer (bytes, bytearray, or any object supporting the buffer protocol).
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        The content buffer is copied internally, so it's safe to modify or delete the original
        buffer after calling this function. The message will be delivered to all clients
        currently joined to the channel, including yourself.
    """
def set_acls_with_callback(url: str, acls: list, callback: typing.Callable[[Result], None]) -> Request:
    """
    Set the ACLs (Access Control Lists) on a folder or file.

    This function replaces the entire access control list for the specified item with the
    provided list. This is a complete replacement - any existing ACLs not included in the
    new list will be removed.

    Args:
        url: URL of item to set the ACLs on.
        acls: The complete new set of ACLs to apply to this file/folder. Each AclEntry should
              contain a user/group name and the access flags they should have.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        You must have administrative permissions to modify ACLs. If you don't have permission,
        the result will be Result.ERROR_ACCESS_DENIED. The ACLs are applied atomically - either
        all changes succeed or none do.
    """
def set_alias(alias: str, value: str) -> None:
    """
    Redirect a URL to a different location.

    This function creates URL aliases that redirect one URL scheme or path to another.
    This is useful for creating shortcuts or mapping local paths to URL schemes.

    Args:
        alias: The URL alias to create (e.g., "home:", "work:", "project:")
        value: The target URL or path to redirect to (e.g., "C:\\Users\\myname\\")

    Note:
        For example: set_alias("home:", "C:\\Users\\myname\\")
        Call with value=None to remove an existing alias.
        Aliases are stored locally and persist between application sessions.
    """
def set_authentication_message_box_callback(callback: typing.Callable[[bool, str, int], None]) -> None:
    """
    Set an authentication message box callback.

    The callback is called when authentication requires opening a web browser to complete sign-in.
        The intention is the application should show a dialog box letting the user know that
        a browser window has opened and to complete signing in using the web browser.

    The callback receives:
        1. A bool indicating if the dialog should be shown (true) or hidden (false)
        2. A string indicating the host name that the authentication is for
        3. An integer handle that can be passed to "authentication_cancel"

    You should provide a "Cancel" button and call cancel_authentication if the user presses it.

    You should call this function with "None" as the callback prior to shutting down in order to
        free memory that was allocated to store the callback.

    Note that signing in to multiple servers simultaneously is allowed, so you may receive multiple
    callbacks with "show" set to true before receiving them with "show" set to false. You can use
    the third parameter to track show/hide pairs.

    Args:
        callback: Callback to be called to show an authentication dialog box.
    """
def set_azure_sas_token(host: str, container: str, sasToken: str, writeConfig: bool) -> Result:
    """
    Set SAS Token for an Azure blob container.

    This function configures Azure Blob Storage access using a Shared Access Signature (SAS) token.
    The SAS token provides secure, time-limited access to Azure storage resources.

    Args:
        host: The Azure host to configure
        container: The blob container name
        sasToken: The Shared Access Signature token for authentication
        writeConfig: Whether to write configuration to disk (optional)

    Returns:
        OmniClient Result code indicating success or failure.

    Note:
        The SAS token should include the necessary permissions (read, write, list, etc.)
        and be valid for the specified container. The configuration is stored locally
        and persists between application sessions.
    """
def set_hang_detection_time_ms(timeout: int) -> None:
    """
    Configure the amount of time to wait before the blocking versions of each function prints a warning (and a stack trace).

    Note: this value must be set per thread!

    Args:
        timeout: The amount of time to wait (in milliseconds) before printing a warning.
    """
def set_http_header(key: str, value: str) -> None:
    """
    Set a header to pass along with any HTTP request.

    This function sets a custom HTTP header that will be included with all HTTP requests
    made by the client library. This can be useful for adding authentication tokens,
    custom headers for debugging, or other HTTP-specific requirements.

    Args:
        key: The HTTP header name (e.g., 'Authorization', 'User-Agent').
        value: The HTTP header value. Pass None to clear a previously set header.

    Note:
        This does not apply to redirects from Nucleus. Headers are only sent with
        direct HTTP requests, not with redirected requests.
    """
def set_log_callback(callback: typing.Callable[[str, str, LogLevel, str], None]) -> None:
    """
    Set a log callback function.

    This sets a function that will be called when the library wants to write anything to a log.
    This is the only function that's safe to call before :py:func:`omni.client.initialize`.

    Args:
        callback: The callback function to register, or None to clear the callback.
                 The callback should have the signature: callback(thread, component, level, message)
                 where thread and component are strings, level is a LogLevel enum value,
                 and message is the log message string.

    Example::

            def log_callback(thread, component, level, message):
                print(f"{thread} {component} {level} {message}")

            omni.client.set_log_callback(log_callback)

    Note:
        The callback is called from a background thread, so it's safe to perform I/O operations.
        If the callback raises an exception, it will be caught and logged as an error.
    """
def set_log_level(log_level: LogLevel) -> None:
    """
    Set the log level.

    Any messages below this level will not be logged.

    Args:
        log_level: The minimum log level to display (LogLevel.DEBUG, LogLevel.VERBOSE, 
                  LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR)

    Note:
        This function can be called before :py:func:`omni.client.initialize`.
    """
def set_product_info(name: str, version: str = None, extra: str = None) -> None:
    """
    Sets product information that's sent to Nucleus when connecting.

    If you're already connected to a Nucleus server, this will not send the new values to the server,
    only on reconnect. For this reason you should set the product information prior to connecting.

    This is also used in Hub to help identify which applications are running.

    Args:
        name: The human-readable name of this product.
        version: The version of this product (not the client library version).
        extra: Any additional information you think would be valuable in the logs.
    """
def set_retries(max_ms: int, base_ms: int, jitter_ms: int) -> tuple:
    """
    Set parameters to control retry behavior

    The formula for delay between retries is:
    delay_ms = (base_ms * count * count) + rand(0, jitter_ms * count)
    where "count" is the current retry count.

    Retries are aborted after 'max_ms' time has elapsed. Set it to 0 to disable retries.

    Default behavior is:
    max_ms = 120,000
    base_ms = 100
    jitter_ms = 100

    Returns previous values in a tuple of (max_ms, base_ms, jitter_ms).
    """
def set_s3_configuration(url: str, bucket: str = None, region: str = None, accessKeyId: str = None, secretAccessKey: str = None, sessionToken: str = None, cloudfrontUrl: str = None, cloudfrontForList: bool = False, writeConfig: bool = False) -> Result:
    """
    Set S3 configuration for a host.

    This function configures S3 storage settings for a specific host. The configuration
    includes bucket information, region, access credentials, and optional CloudFront settings.

    Args:
        url: The host to configure (can be a plain hostname or full URL)
        bucket: S3 bucket name (optional, required if region is specified)
        region: S3 region (optional, required if bucket is specified)
        accessKeyId: S3 access key ID (optional)
        secretAccessKey: S3 secret access key (optional)
        sessionToken: S3 session token (optional)
        cloudfrontUrl: CloudFront URL for CDN access (optional)
        cloudfrontForList: Whether to use CloudFront for list operations (optional)
        writeConfig: Whether to write configuration to disk (optional)

    Returns:
        OmniClient Result code indicating success or failure.

    Note:
        For backwards compatibility, the host parameter is named 'url' and can accept
        either a plain host name or a full URL. The configuration is stored locally
        and persists between application sessions.
    """
def shutdown() -> None:
    """
    Shut down the client library.

    It is not safe to call any client library functions after calling shutdown.
    """
def sign_out(url: str) -> None:
    """
    Sign out specific url connection.

    Args:
        url: Immediately disconnect from the server specified by this URL.
             Any outstanding requests will call their callbacks with Result.ERROR_CONNECTION.
             Additionally, clear the saved authentication token so future requests to this server will
             trigger re-authentication.
    """
def stat_subscribe_with_callback(url: str, stat_callback: typing.Callable[[Result, ListEntry], None], subscribe_callback: typing.Callable[[Result, ListEvent, ListEntry], None], include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Request:
    """
    Subscribe to change notifications for a url.

    If 'url' is a file, you will only receive information about that file.
    If 'url' is a folder, you will only receive information about that folder.
    '`stat_callback` is called once with the initial stat info,then '`subscribe_callback`' may be called multiple times after that the item changes.

    Args:
        url: URL of item to stat.
        stat_callback: Callback to be called once with the initial stat.
        subscribe_callback: Callback to be called when changes happen.
        include_deleted_option: Option to include deleted files (default NO_DELETED_FILES)

    Returns:
        Subscription object.
    """
def stat_with_callback(url: str, callback: typing.Callable[[Result, ListEntry], None], include_deleted_option: ListIncludeOption = ListIncludeOption.NO_DELETED_FILES) -> Request:
    """
    Retrieve information about a file or folder.

    This function retrieves detailed metadata about a specific file or folder, including
    size, modification time, access permissions, version information, and more.

    Args:
        url: URL of item to stat.
        callback: Callback to be called with the results. The callback receives:
                 - result: Result indicating success or failure
                 - entry: ListEntry object containing file/folder information, or empty entry if result is not Ok
        include_deleted_option: Option to include deleted files:
                              - ListIncludeOption.DEFAULT_NOT_DELETED: Don't include deleted files (default)
                              - ListIncludeOption.INCLUDE_DELETED: Include deleted files
                              - ListIncludeOption.ONLY_DELETED: Only include deleted files

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        The ListEntry contains information such as relative path, access flags, size,
        modification time, version, hash, and metadata about who created/modified the item.
        If the item doesn't exist, the result will be Result.ERROR_NOT_FOUND.
    """
def trace_start() -> bool:
    """
    Start tracing using carb::tracer.

    This function starts tracing functionality using the carb::tracer library. Tracing
    provides detailed performance and debugging information about client library operations.

    Returns:
        True if tracing was enabled (or was already enabled), False otherwise.

    Note:
        Tracing is automatically started when the library is loaded, but this function
        may be used if the tracer library was downloaded and installed while the
        application was running.
    """
def trace_stop() -> None:
    """
    Stop tracing using carb::tracer.

    This function stops tracing functionality that was previously started with
    :py:func:`omni.client.trace_start`.

    Note:
        If the client library is not using tracer, this does nothing. Tracing is
        automatically stopped when the library is unloaded, but this can be used to
        stop it early.
    """
def undelete_with_callback(url: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Undelete soft-deleted paths

    Supports recursive parents undelete

    Args:
        url: URL of item to undelete
        callback: Callback to be called with the result of the operation

    Returns:
        Request object.
    """
def unlock_with_callback(url: str, callback: typing.Callable[[Result], None]) -> Request:
    """
    Unlock a file so other clients can modify it.

    This function releases an exclusive lock on the specified file that was previously
    acquired using :py:func:`omni.client.lock_with_callback`. Once unlocked, other clients
    can acquire locks and modify the file.

    Args:
        url: URL of file to unlock.
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        You can only unlock a file that you previously locked. If you didn't lock the file,
        the result will be Result.ERROR_ACCESS_DENIED. The lock is also automatically
        released when you disconnect from the server.
    """
def write_file_ex_with_callback(url: str, content: buffer, callback: typing.Callable[[Result, WriteFileExInfo], None], message: str = None, skip_checkpoint: bool = False) -> Request:
    """
    Create a new file, overwriting if it already exists.

    Args:
        url: URL of file to create.
        content: File content.
        callback: Callback to be called with the result.
        message: Message to apply to atomic checkpoint of destination url.
        skip_checkpoint: If true, a checkpoint will not be created.
                         This is a destructive operation that will not keep the history of the changes.

    Returns:
        Request object.
    """
def write_file_with_callback(url: str, content: buffer, callback: typing.Callable[[Result], None], message: str = None) -> Request:
    """
    Create a new file, overwriting if it already exists.

    This function writes the provided content to a file at the specified URL. If the file
    already exists, it will be overwritten. A checkpoint is automatically created after
    the write operation completes.

    Args:
        url: URL of file to create or overwrite.
        content: File content as a buffer (bytes, bytearray, or any object supporting the buffer protocol).
        callback: Callback to be called with the result. The callback receives:
                 - result: Result indicating success or failure
        message: Optional message to apply to the checkpoint created after writing the file.

    Returns:
        Request object that can be used to wait for completion or cancel the operation.

    Note:
        The content buffer is copied internally, so it's safe to modify or delete the original
        buffer after calling this function. If the file is locked by another client, the result
        will be Result.ERROR_LOCKED.
    """
VERSION = 563237716230144
