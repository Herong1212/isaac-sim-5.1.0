# Public API for module omni.kit.raycast.query:

## Classes

- class Result
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - INVALID_PARAMETER: omni.kit.raycast.query._omni_kit_raycast_query.Result
  - PARAMETER_IS_NULL: omni.kit.raycast.query._omni_kit_raycast_query.Result
  - RAYCAST_QUERY_MANAGER_DOES_NOT_EXIT: omni.kit.raycast.query._omni_kit_raycast_query.Result
  - RAYCAST_SEQUENCE_ADDITION_FAILED: omni.kit.raycast.query._omni_kit_raycast_query.Result
  - RAYCAST_SEQUENCE_DOES_NOT_EXIST: omni.kit.raycast.query._omni_kit_raycast_query.Result
  - SUCCESS: omni.kit.raycast.query._omni_kit_raycast_query.Result

- class Ray
  - def __init__(self, origin: object, direction: object, min_t: float = 0.0, max_t: float = inf, adjust_for_section: bool = True)
  - [property] def forward(self) -> object
  - [forward.setter] def forward(self, arg1: object)
  - [property] def max_t(self) -> float
  - [max_t.setter] def max_t(self, arg1: float)
  - [property] def min_t(self) -> float
  - [min_t.setter] def min_t(self, arg1: float)
  - [property] def origin(self) -> object
  - [origin.setter] def origin(self, arg1: object)

- class RayQueryResult
  - def __init__(self)
  - def get_target_usd_path(self) -> str
  - [property] def hit_position(self) -> object
  - [property] def hit_t(self) -> float
  - [property] def instance_id(self) -> int
  - [property] def normal(self) -> object
  - [property] def primitive_id(self) -> int
  - [property] def valid(self) -> bool

- class IRaycastQuery
  - def add_raycast_sequence(self) -> int
  - def get_latest_result_from_raycast_sequence(self, arg0: int) -> typing.Tuple[Result, Ray, RayQueryResult]
  - def get_latest_result_from_raycast_sequence_array(self, arg0: int) -> typing.Tuple[Result, typing.List[Ray], typing.List[RayQueryResult]]
  - def get_raycast_sequence_array_size(self, arg0: int) -> typing.Tuple[Result, int]
  - def remove_raycast_sequence(self, arg0: int) -> Result
  - def set_raycast_sequence_array_size(self, arg0: int, arg1: int) -> Result
  - def submit_ray_to_raycast_sequence(self, arg0: int, arg1: Ray) -> Result
  - def submit_ray_to_raycast_sequence_array(self, arg0: int, arg1: typing.List[Ray]) -> Result
  - def submit_raycast_query(self, ray: Ray, callback: typing.Callable[[Ray, RayQueryResult], None])

## Functions

- def acquire_raycast_query_interface(*args, **kwargs) -> typing.Any
