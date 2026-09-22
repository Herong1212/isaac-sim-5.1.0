"""pybind11 carb.volume bindings"""
from __future__ import annotations
import omni.volume._volume
import typing
import numpy
_Shape = typing.Tuple[int, ...]

__all__ = [
    "GridData",
    "IVolume",
    "SaveVolumeParameters",
    "acquire_volume_interface",
    "kNanoVDBCodecBlosc",
    "kNanoVDBCodecEnd",
    "kNanoVDBCodecNone",
    "kNanoVDBCodecZip"
]


class GridData():
    pass
class IVolume():
    def create_from_dense(self, arg0: float, arg1: buffer, arg2: float, arg3: buffer, arg4: str) -> GridData: ...
    def create_from_file(self, arg0: str) -> GridData: ...
    def get_grid_class(self, arg0: GridData, arg1: int) -> int: ...
    def get_grid_data(self, arg0: GridData, arg1: int) -> typing.List[int]: ...
    def get_grid_type(self, arg0: GridData, arg1: int) -> int: ...
    def get_index_bounding_box(self, arg0: GridData, arg1: int) -> list: ...
    def get_num_grids(self, arg0: GridData) -> int: ...
    def get_short_grid_name(self, arg0: GridData, arg1: int) -> str: ...
    def get_world_bounding_box(self, arg0: GridData, arg1: int) -> list: ...
    def mesh_to_level_set(self, arg0: numpy.ndarray[numpy.float32], arg1: numpy.ndarray[numpy.int32], arg2: numpy.ndarray[numpy.int32], arg3: float, arg4: numpy.ndarray[numpy.int32]) -> GridData: ...
    def save_volume(self, gridData: GridData, path: str, saveVolumeParameters: SaveVolumeParameters = ...) -> bool: ...
    pass
class SaveVolumeParameters():
    def __init__(self) -> None: ...
    @property
    def flags(self) -> int:
        """
        :type: int
        """
    @flags.setter
    def flags(self, arg0: int) -> None:
        pass
    pass
def acquire_volume_interface(plugin_name: str = None, library_path: str = None) -> IVolume:
    pass
kNanoVDBCodecBlosc = 2
kNanoVDBCodecEnd = 3
kNanoVDBCodecNone = 0
kNanoVDBCodecZip = 1
