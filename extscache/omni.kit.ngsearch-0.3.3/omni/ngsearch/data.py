from typing import AsyncIterator, Dict, List, Optional

from idl.types import Enum, Literal, Record

Capabilities = Dict[str, int]
NGSearchServiceServerRemoteCapabilities = Capabilities
NGSearchServiceServerLocalCapabilities = {
    "demo_test": 1,
    "datasource_info": 0,
    "find": 3,
    "find2": 3,
    "find_paged_cursor": 2,
    "find_paged_skip": 2,
    "get_prefixes": 0,
    "search": 0,
    "scroll": 0,
    "search_gen": 0,
    "list_searchable_keywords": 0,
    "get_predictions": 0,
    "get_embeddings": 0,
    "search_gen_2": 0,
    "get_embedding_hierarchy": 0,
    "compute_hierarchical_clustering": 0,
    "telemetry_event_click": 0,
    "telemetry_event_results_presented": 0,
    "livez": 0,
    "readyz": 0,
}
NGSearchServiceServerCapabilities = NGSearchServiceServerRemoteCapabilities
NGSearchServiceClientRemoteCapabilities = Capabilities
NGSearchServiceClientLocalCapabilities = {
    "demo_test": 1,
    "datasource_info": 0,
    "find": 3,
    "find2": 3,
    "find_paged_cursor": 2,
    "find_paged_skip": 2,
    "get_prefixes": 0,
    "search": 0,
    "scroll": 0,
    "search_gen": 0,
    "list_searchable_keywords": 0,
    "get_predictions": 0,
    "get_embeddings": 0,
    "search_gen_2": 0,
    "get_embedding_hierarchy": 0,
    "compute_hierarchical_clustering": 0,
    "telemetry_event_click": 0,
    "telemetry_event_results_presented": 0,
    "livez": 0,
    "readyz": 0,
}
NGSearchServiceClientCapabilities = NGSearchServiceClientLocalCapabilities
NGSearchServiceComputeHierarchicalClusteringServerRemoteVersion = int
NGSearchServiceComputeHierarchicalClusteringServerLocalVersion = 0
NGSearchServiceComputeHierarchicalClusteringServerVersion = (
    NGSearchServiceComputeHierarchicalClusteringServerRemoteVersion
)
NGSearchServiceComputeHierarchicalClusteringClientRemoteVersion = int
NGSearchServiceComputeHierarchicalClusteringClientLocalVersion = 0
NGSearchServiceGetEmbeddingHierarchyServerRemoteVersion = int
NGSearchServiceGetEmbeddingHierarchyServerLocalVersion = 0
NGSearchServiceGetEmbeddingHierarchyServerVersion = NGSearchServiceGetEmbeddingHierarchyServerRemoteVersion
NGSearchServiceGetEmbeddingHierarchyClientRemoteVersion = int
NGSearchServiceGetEmbeddingHierarchyClientLocalVersion = 0
NGSearchServiceSearchGen2ServerRemoteVersion = int
NGSearchServiceSearchGen2ServerLocalVersion = 0
NGSearchServiceSearchGen2ServerVersion = NGSearchServiceSearchGen2ServerRemoteVersion
NGSearchServiceSearchGen2ClientRemoteVersion = int
NGSearchServiceSearchGen2ClientLocalVersion = 0
NGSearchServiceGetPrefixesServerRemoteVersion = int
NGSearchServiceGetPrefixesServerLocalVersion = 0
NGSearchServiceGetPrefixesServerVersion = NGSearchServiceGetPrefixesServerRemoteVersion
NGSearchServiceGetPrefixesClientRemoteVersion = int
NGSearchServiceGetPrefixesClientLocalVersion = 0
NGSearchServiceFindPagedSkipServerRemoteVersion = int
NGSearchServiceFindPagedSkipServerLocalVersion = 2
NGSearchServiceFindPagedSkipServerVersion = NGSearchServiceFindPagedSkipServerRemoteVersion
NGSearchServiceFindPagedSkipClientRemoteVersion = int
NGSearchServiceFindPagedSkipClientLocalVersion = 2
NGSearchServiceFindPagedCursorServerRemoteVersion = int
NGSearchServiceFindPagedCursorServerLocalVersion = 2
NGSearchServiceFindPagedCursorServerVersion = NGSearchServiceFindPagedCursorServerRemoteVersion
NGSearchServiceFindPagedCursorClientRemoteVersion = int
NGSearchServiceFindPagedCursorClientLocalVersion = 2
NGSearchServiceFind2ServerRemoteVersion = int
NGSearchServiceFind2ServerLocalVersion = 3
NGSearchServiceFind2ServerVersion = NGSearchServiceFind2ServerRemoteVersion
NGSearchServiceFind2ClientRemoteVersion = int
NGSearchServiceFind2ClientLocalVersion = 3
NGSearchServiceFindServerRemoteVersion = int
NGSearchServiceFindServerLocalVersion = 3
NGSearchServiceFindServerVersion = NGSearchServiceFindServerRemoteVersion
NGSearchServiceFindClientRemoteVersion = int
NGSearchServiceFindClientLocalVersion = 3
SearchServerRemoteCapabilities = Capabilities
SearchServerLocalCapabilities = {"find": 3, "find2": 3, "find_paged_cursor": 2, "find_paged_skip": 2, "get_prefixes": 0}
SearchServerCapabilities = SearchServerRemoteCapabilities
SearchClientRemoteCapabilities = Capabilities
SearchClientLocalCapabilities = {"find": 3, "find2": 3, "find_paged_cursor": 2, "find_paged_skip": 2, "get_prefixes": 0}
SearchClientCapabilities = SearchClientLocalCapabilities
SearchGetPrefixesServerRemoteVersion = int
SearchGetPrefixesServerLocalVersion = 0
SearchGetPrefixesServerVersion = SearchGetPrefixesServerRemoteVersion
SearchGetPrefixesClientRemoteVersion = int
SearchGetPrefixesClientLocalVersion = 0
SearchFindPagedSkipServerRemoteVersion = int
SearchFindPagedSkipServerLocalVersion = 2
SearchFindPagedSkipServerVersion = SearchFindPagedSkipServerRemoteVersion
SearchFindPagedSkipClientRemoteVersion = int
SearchFindPagedSkipClientLocalVersion = 2
SearchFindPagedCursorServerRemoteVersion = int
SearchFindPagedCursorServerLocalVersion = 2
SearchFindPagedCursorServerVersion = SearchFindPagedCursorServerRemoteVersion
SearchFindPagedCursorClientRemoteVersion = int
SearchFindPagedCursorClientLocalVersion = 2
SearchFind2ServerRemoteVersion = int
SearchFind2ServerLocalVersion = 3
SearchFind2ServerVersion = SearchFind2ServerRemoteVersion
SearchFind2ClientRemoteVersion = int
SearchFind2ClientLocalVersion = 3
SearchFindServerRemoteVersion = int
SearchFindServerLocalVersion = 3
SearchFindServerVersion = SearchFindServerRemoteVersion
SearchFindClientRemoteVersion = int
SearchFindClientLocalVersion = 3


class InputSpaceMetric(metaclass=Enum):
    cosine = "cosine"
    euclidean = "euclidean"


class ClusteringMethod(metaclass=Enum):
    AgglomerativeClustering = "AgglomerativeClustering"


class ProjectionMethod(metaclass=Enum):
    umap = "umap"
    pca = "pca"
    pca32umap2 = "pca32umap2"


class SearchMethod(metaclass=Enum):
    exact = "exact"
    lsh = "lsh"


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


class Prediction(Record):
    tag: str
    prob: float


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
    is_deleted: Optional[bool]
    deleted_by: Optional[str]
    deleted_timestamp: Optional[float]


class StatusType(metaclass=Enum):
    OK = "OK"
    Denied = "DENIED"
    TokenExpired = "TOKEN_EXPIRED"
    ESRequestError = "ES_REQUEST_ERROR"
    ESConnectionTimeout = "ES_CONNECTION_TIMEOUT"
    FileNotFoundError = "FILE_NOT_FOUND_ERROR"
    ThumbnailMissingError = "THUMBNAIL_MISSING_ERROR"
    InvalidPrefix = "INVALID_PREFIX"
    UnknownError = "UNKNOWN_ERROR"
    ProjectionServiceUnavailable = "PROJECTION_SERVICE_UNAVAILABLE"


class SearchItem(Record):
    status: Optional[StatusType]
    path: Optional[Path]
    url: Optional[str]
    image: Optional[str]
    embed: Optional[str]
    predictions: Optional[List[Prediction]]
    projection: Optional[str]


class FormatOption(metaclass=Enum):
    flat = 0
    recycle_bin = 1


class Keyword(Record):
    keyword: str
    count: float


class Item(Record):
    path: str
    url: str
    id: float
    value: float
    predictions: List[Prediction]
    image: str
    enabled: bool
    embed: str


class DataContent(Record):
    data: str


class Vec2d(Record):
    x: float
    y: float


class ReadyzResponse(Record):
    ready: bool


class LivezResponse(Record):
    live: bool


class StatusOnlyResponse(Record):
    status: StatusType


class TelemetryContext(Record):
    session_id: str
    app_name: str
    app_version: str
    ui_name: str
    ui_version: str
    kit_version: Optional[str]
    search_request_id: Optional[str]


class HierarchicalClustering(Record):
    version: int
    status: StatusType
    hierarchy_nodes: str


class ClusteringConfig(Record):
    projection_method: ProjectionMethod
    clustering_method: ClusteringMethod


NGSearchServiceComputeHierarchicalClusteringClientVersion = (
    NGSearchServiceComputeHierarchicalClusteringClientLocalVersion
)


class EmbeddingHierarchy(Record):
    version: int
    status: StatusType
    clusters: str
    search_request_id: str


class SearchConfig(Record):
    method: SearchMethod
    candidates: Optional[float]


class SearchQuery2(Record):
    query: Optional[str]
    parent: str
    format: Optional[FormatOption]


NGSearchServiceGetEmbeddingHierarchyClientVersion = NGSearchServiceGetEmbeddingHierarchyClientLocalVersion


class BatchedSearchItem(Record):
    version: int
    status: StatusType
    item_list: Optional[List[SearchItem]]
    search_request_id: str


class ProjectionConfig(Record):
    method: ProjectionMethod


NGSearchServiceSearchGen2ClientVersion = NGSearchServiceSearchGen2ClientLocalVersion


class DataItems(Record):
    status: StatusType
    data: Optional[List[DataContent]]


class PredictionList(Record):
    status: StatusType
    predictions: Optional[List[Prediction]]


class KeywordList(Record):
    data: List[Keyword]


class Results(Record):
    data: List[Item]
    status: str
    scroll_id: str


class PrefixResult(Record):
    status: StatusType
    prefixes: Optional[List[str]]
    version: int


NGSearchServiceGetPrefixesClientVersion = NGSearchServiceGetPrefixesClientLocalVersion


class SearchResult(Record):
    status: StatusType
    paths: List[Path]
    version: int
    search_request_id: Optional[str]


NGSearchServiceFindPagedSkipClientVersion = NGSearchServiceFindPagedSkipClientLocalVersion


class SearchResultCursor(Record):
    status: StatusType
    paths: List[Path]
    version: int
    cursor_id: Optional[str]


NGSearchServiceFindPagedCursorClientVersion = NGSearchServiceFindPagedCursorClientLocalVersion


class SearchQuery(Record):
    name: Optional[str]
    tags: Optional[List[str]]
    parent: str
    format: Optional[FormatOption]


NGSearchServiceFind2ClientVersion = NGSearchServiceFind2ClientLocalVersion
NGSearchServiceFindClientVersion = NGSearchServiceFindClientLocalVersion


class Datasource(Record):
    name: str
    type: str
    count: float
    description: str


SearchGetPrefixesClientVersion = SearchGetPrefixesClientLocalVersion
SearchFindPagedSkipClientVersion = SearchFindPagedSkipClientLocalVersion
SearchFindPagedCursorClientVersion = SearchFindPagedCursorClientLocalVersion
SearchFind2ClientVersion = SearchFind2ClientLocalVersion
SearchFindClientVersion = SearchFindClientLocalVersion
name = "deepsearch"
