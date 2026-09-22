from __future__ import annotations
import pxr.Kind._kind
import typing
import Boost.Python

__all__ = [
    "Registry",
    "Tokens"
]


class Registry(Boost.Python.instance):
    @staticmethod
    def GetAllKinds(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetBaseKind(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def HasKind(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsA(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsAssembly(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsComponent(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsGroup(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsModel(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsSubComponent(*args, **kwargs) -> typing.Any: ...
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    pass
class Tokens(Boost.Python.instance):
    assembly = 'assembly'
    component = 'component'
    group = 'group'
    model = 'model'
    subcomponent = 'subcomponent'
    pass
__MFB_FULL_PACKAGE_NAME = 'kind'
