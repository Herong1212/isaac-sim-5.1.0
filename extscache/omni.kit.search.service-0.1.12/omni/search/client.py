from typing import AsyncIterator, Dict, List, Optional

from idl.connection.transport import Client
from idl.types import Literal, Record

from .data import *


class Search:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'Search':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def find(self, query: SearchQuery, token: str) -> AsyncIterator[Path]:
        """
        @deprecated
        """
        _request = {}
        _request["version"] = SearchFindClientVersion
        _request["query"] = query
        _request["token"] = token
        agen = self.transport.call_many("Search", "find", _request, request_type=SearchFindArgs, return_type=Path)
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
    
    async def find2(self, query: SearchQuery, token: str) -> SearchResult:
        """
        
        """
        _request = {}
        _request["version"] = SearchFind2ClientVersion
        _request["query"] = query
        _request["token"] = token
        _response = await self.transport.call("Search", "find2", _request, request_type=SearchFind2Args, return_type=SearchResult)
        return _response
    
    async def find_paged_cursor(self, query: SearchQuery2, token: str, size: Optional[float] = None, cursor_id: Optional[str] = None) -> SearchResultCursor:
        """
        
        """
        _request = {}
        _request["version"] = SearchFindPagedCursorClientVersion
        _request["query"] = query
        _request["token"] = token
        if size is not None:
            _request["size"] = size
        if cursor_id is not None:
            _request["cursor_id"] = cursor_id
        _response = await self.transport.call("Search", "find_paged_cursor", _request, request_type=SearchFindPagedCursorArgs, return_type=SearchResultCursor)
        return _response
    
    async def find_paged_skip(self, query: SearchQuery2, token: str, size: Optional[float] = None, skip_first: Optional[float] = None) -> SearchResult:
        """
        
        """
        _request = {}
        _request["version"] = SearchFindPagedSkipClientVersion
        _request["query"] = query
        _request["token"] = token
        if size is not None:
            _request["size"] = size
        if skip_first is not None:
            _request["skip_first"] = skip_first
        _response = await self.transport.call("Search", "find_paged_skip", _request, request_type=SearchFindPagedSkipArgs, return_type=SearchResult)
        return _response
    
    async def get_prefixes(self, ) -> PrefixResult:
        """
        
        """
        _request = {}
        _request["version"] = SearchGetPrefixesClientVersion
        _response = await self.transport.call("Search", "get_prefixes", _request, request_type=SearchGetPrefixesArgs, return_type=PrefixResult)
        return _response
    
    __interface_name__ = "Search"
    __interface_origin__ = "Search.idl.ts"
    __interface_capabilities__ = SearchClientLocalCapabilities


class SearchFindArgs(Record):
    version: Literal(SearchFindClientVersion) = SearchFindClientVersion
    query: SearchQuery
    token: str


class SearchFind2Args(Record):
    version: Literal(SearchFind2ClientVersion) = SearchFind2ClientVersion
    query: SearchQuery
    token: str


class SearchFindPagedCursorArgs(Record):
    version: Literal(SearchFindPagedCursorClientVersion) = SearchFindPagedCursorClientVersion
    query: SearchQuery2
    token: str
    size: Optional[float]
    cursor_id: Optional[str]


class SearchFindPagedSkipArgs(Record):
    version: Literal(SearchFindPagedSkipClientVersion) = SearchFindPagedSkipClientVersion
    query: SearchQuery2
    token: str
    size: Optional[float]
    skip_first: Optional[float]


class SearchGetPrefixesArgs(Record):
    version: Literal(SearchGetPrefixesClientVersion) = SearchGetPrefixesClientVersion

