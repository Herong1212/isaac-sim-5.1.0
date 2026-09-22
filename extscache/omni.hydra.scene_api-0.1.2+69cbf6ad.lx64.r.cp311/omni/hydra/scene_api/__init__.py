"""APIs for adding and removing scene delegates."""

import omni.ext
from .bindings._omni_hydra_scene_api import *

__all__= [
    "add_background_loading_hydra_scene_delegate",
    "remove_hydra_scene_delegate",
    "compute_scene_delegate_world_bounding_box",
    "set_scene_delegate_root_transform",
    "get_wgs84_coords",
]
