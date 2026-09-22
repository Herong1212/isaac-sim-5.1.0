from typing import List, Optional, Dict, AsyncIterator
from idl.types import Enum, Record, Literal


Capabilities = Dict[str, int]
SearchServerRemoteCapabilities = Capabilities
SearchServerLocalCapabilities = {'find': 3, 'find2': 2, 'find_paged_cursor': 1, 'find_paged_skip': 1, 'get_prefixes': 0}
SearchServerCapabilities = SearchServerRemoteCapabilities
SearchClientRemoteCapabilities = Capabilities
SearchClientLocalCapabilities = {'find': 3, 'find2': 2, 'find_paged_cursor': 1, 'find_paged_skip': 1, 'get_prefixes': 0}
SearchClientCapabilities = SearchClientLocalCapabilities
SearchGetPrefixesServerRemoteVersion = int
SearchGetPrefixesServerLocalVersion = 0
SearchGetPrefixesServerVersion = SearchGetPrefixesServerRemoteVersion
SearchGetPrefixesClientRemoteVersion = int
SearchGetPrefixesClientLocalVersion = 0
SearchFindPagedSkipServerRemoteVersion = int
SearchFindPagedSkipServerLocalVersion = 1
SearchFindPagedSkipServerVersion = SearchFindPagedSkipServerRemoteVersion
SearchFindPagedSkipClientRemoteVersion = int
SearchFindPagedSkipClientLocalVersion = 1
SearchFindPagedCursorServerRemoteVersion = int
SearchFindPagedCursorServerLocalVersion = 1
SearchFindPagedCursorServerVersion = SearchFindPagedCursorServerRemoteVersion
SearchFindPagedCursorClientRemoteVersion = int
SearchFindPagedCursorClientLocalVersion = 1
SearchFind2ServerRemoteVersion = int
SearchFind2ServerLocalVersion = 2
SearchFind2ServerVersion = SearchFind2ServerRemoteVersion
SearchFind2ClientRemoteVersion = int
SearchFind2ClientLocalVersion = 2
SearchFindServerRemoteVersion = int
SearchFindServerLocalVersion = 3
SearchFindServerVersion = SearchFindServerRemoteVersion
SearchFindClientRemoteVersion = int
SearchFindClientLocalVersion = 3


class PathEvent(metaclass=Enum):
    Full = "full"
    Create = "create"
    Update = "update"
    Delete = "delete"
    ChangeAcl = "change_acl"
    Options = "set_path_options"
    Locked = "lock"
    Unlocked = "unlock"
    Rename = "rename"
    Copy = "copy"
    VersionReplaced = "replace_version"


class PathPermission(metaclass=Enum):
    Read = "read"
    Write = "write"
    Admin = "admin"


class PathType(metaclass=Enum):
    All = ""
    Asset = "asset"
    Folder = "folder"
    Channel = "channel"
    Mount = "mount"
    Object = "object"
    Empty = "none"


class Path(Record):
    version: Optional[int]
    type: Optional[PathType]
    uri: Optional[str]
    acl: Optional[List[PathPermission]]
    created: Optional[str]
    created_by: Optional[str]
    modified: Optional[str]
    modified_by: Optional[str]
    size: Optional[float]
    etag: Optional[str]
    event: Optional[PathEvent]
    mounted: Optional[bool]
    transaction_id: Optional[str]
    destination: Optional[str]
    score: Optional[float]


class StatusType(metaclass=Enum):
    OK = "OK"
    Denied = "DENIED"
    TokenExpired = "TOKEN_EXPIRED"
    ESRequestError = "ES_REQUEST_ERROR"
    ESConnectionTimeout = "ES_CONNECTION_TIMEOUT"
    FileNotFoundError = "FILE_NOT_FOUND_ERROR"
    InvalidPrefix = "INVALID_PREFIX"
    UnknownError = "UNKNOWN_ERROR"


class PrefixResult(Record):
    prefixes: List[str]
    version: int


SearchGetPrefixesClientVersion = SearchGetPrefixesClientLocalVersion


class SearchResult(Record):
    status: StatusType
    paths: List[Path]
    version: int


class SearchQuery2(Record):
    query: Optional[str]
    parent: str


SearchFindPagedSkipClientVersion = SearchFindPagedSkipClientLocalVersion


class SearchResultCursor(Record):
    paths: List[Path]
    version: int
    cursor_id: str


SearchFindPagedCursorClientVersion = SearchFindPagedCursorClientLocalVersion


class SearchQuery(Record):
    name: Optional[str]
    tags: Optional[List[str]]
    parent: str


SearchFind2ClientVersion = SearchFind2ClientLocalVersion
SearchFindClientVersion = SearchFindClientLocalVersion