# Public API for module omni.ujitso.default:

## Classes

- class DataStoreClearing
  - def __init__(self)
  - def clear_percentage(self, arg0: float) -> bool

- class DataStoreFailureInjector
  - def __init__(self)
  - def clear_failures(self) -> bool
  - def inject_failure(self, arg0: DataStoreOperation, arg1: HashKey, arg2: int, arg3: bool) -> bool
  - def remove_failure(self, arg0: DataStoreOperation, arg1: HashKey) -> bool

- class DataStoreOperation
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - Get: omni.ujitso.default._ujitsodefault.DataStoreOperation
  - Set: omni.ujitso.default._ujitsodefault.DataStoreOperation
  - Stat: omni.ujitso.default._ujitsodefault.DataStoreOperation

- class HashKey
  - def __init__(self, hex_key: str = '')
