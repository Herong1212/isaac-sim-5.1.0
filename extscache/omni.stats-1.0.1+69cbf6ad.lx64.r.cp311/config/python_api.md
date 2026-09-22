# Public API for module omni.stats:

## Classes

- class IStats
  - def get_scope_count(self) -> int
  - def get_scopes(self) -> tuple
  - def get_stats(self, scopeId: capsule) -> tuple
  - def get_stats_count(self, scopeId: capsule) -> int

## Functions

- def acquire_stats_interface(plugin_name: str = None, library_path: str = None) -> IStats
- def release_stats_interface(arg0: IStats)
- def get_stats_interface() -> IStats

## Variables

- SCOPE_FLAG_AS_MEMORY: int
- SCOPE_FLAG_AS_RATE: int
- SCOPE_FLAG_HIDE: int
- SCOPE_FLAG_NONE: int
