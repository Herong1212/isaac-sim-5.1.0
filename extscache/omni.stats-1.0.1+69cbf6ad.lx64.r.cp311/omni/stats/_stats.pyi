"""
        This module contains bindings to the C++ carb::stats::Istats interface.
        This provides functionality to display various statistics through the editor UI.
    """
from __future__ import annotations
import omni.stats._stats
import typing

__all__ = [
    "IStats",
    "SCOPE_FLAG_AS_MEMORY",
    "SCOPE_FLAG_AS_RATE",
    "SCOPE_FLAG_HIDE",
    "SCOPE_FLAG_NONE",
    "acquire_stats_interface",
    "release_stats_interface"
]


class IStats():
    def get_scope_count(self) -> int: 
        """
        Get the number of the scopes.
        """
    def get_scopes(self) -> tuple: 
        """
        Get the scope nodes as tuple of dictionaries, which contains the information of all the scopes.
        """
    def get_stats(self, scopeId: capsule) -> tuple: 
        """
        Get the stat nodes as tuple of dictionaries, which contains the information of all the stats within the specified scope.
        """
    def get_stats_count(self, scopeId: capsule) -> int: 
        """
        Get the number of the stats within the specified scope.
        """
    pass
def acquire_stats_interface(plugin_name: str = None, library_path: str = None) -> IStats:
    pass
def release_stats_interface(arg0: IStats) -> None:
    pass
SCOPE_FLAG_AS_MEMORY = 2
SCOPE_FLAG_AS_RATE = 1
SCOPE_FLAG_HIDE = 4
SCOPE_FLAG_NONE = 0
