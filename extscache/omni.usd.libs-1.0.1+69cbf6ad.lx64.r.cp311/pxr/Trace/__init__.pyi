from __future__ import annotations
import pxr.Trace._trace
import typing
import Boost.Python
import pxr.Trace

__all__ = [
    "AggregateNode",
    "Collector",
    "GetElapsedSeconds",
    "GetTestEventName",
    "PythonGarbageCollectionCallback",
    "Reporter",
    "TestAuto",
    "TestCreateEvents",
    "TestNesting"
]


class AggregateNode(Boost.Python.instance):
    @property
    def children(self) -> None:
        """
        :type: None
        """
    @property
    def count(self) -> None:
        """
        :type: None
        """
    @property
    def exclusiveCount(self) -> None:
        """
        :type: None
        """
    @property
    def exclusiveTime(self) -> None:
        """
        :type: None
        """
    @property
    def expanded(self) -> None:
        """
        :type: None
        """
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    @property
    def id(self) -> None:
        """
        :type: None
        """
    @property
    def inclusiveTime(self) -> None:
        """
        :type: None
        """
    @property
    def key(self) -> None:
        """
        :type: None
        """
    pass
class Collector(Boost.Python.instance):
    @staticmethod
    def BeginEvent(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def BeginEventAtTime(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Clear(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def EndEvent(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def EndEventAtTime(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLabel(*args, **kwargs) -> typing.Any: ...
    @property
    def enabled(self) -> None:
        """
        :type: None
        """
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    @property
    def pythonTracingEnabled(self) -> None:
        """
        :type: None
        """
    pass
class Reporter(Boost.Python.instance):
    @staticmethod
    def ClearTree(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLabel(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Report(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ReportChromeTracing(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ReportChromeTracingToFile(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ReportTimes(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def UpdateTraceTrees(*args, **kwargs) -> typing.Any: ...
    @property
    def aggregateTreeRoot(self) -> None:
        """
        :type: None
        """
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    @property
    def foldRecursiveCalls(self) -> None:
        """
        :type: None
        """
    @property
    def groupByFunction(self) -> None:
        """
        :type: None
        """
    @property
    def shouldAdjustForOverheadAndNoise(self) -> None:
        """
        :type: None
        """
    globalReporter: pxr.Trace.Reporter
    pass
def GetElapsedSeconds(*args, **kwargs) -> typing.Any:
    pass
def GetTestEventName(*args, **kwargs) -> typing.Any:
    pass
def PythonGarbageCollectionCallback(*args, **kwargs) -> typing.Any:
    pass
def TestAuto(*args, **kwargs) -> typing.Any:
    pass
def TestCreateEvents(*args, **kwargs) -> typing.Any:
    pass
def TestNesting(*args, **kwargs) -> typing.Any:
    pass
__MFB_FULL_PACKAGE_NAME = 'trace'
