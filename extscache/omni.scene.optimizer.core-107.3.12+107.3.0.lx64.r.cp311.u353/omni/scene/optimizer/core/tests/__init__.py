__copyright__ = "Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

from .test_command_find_coinciding_meshes import *
from .test_commands import *
from .test_operation_decimate_meshes import *
from .test_operation_deduplicate_geometry import *
from .test_operation_delete_hidden_prims import *
from .test_operation_delete_prims import *
from .test_operation_edit_stage_metrics import *
from .test_operation_find_hidden_meshes import *
from .test_operation_flatten_hierarchy import *
from .test_operation_generate_atlas_uvs import *
from .test_operation_generate_normals import *
from .test_operation_generate_projection_uvs import *
from .test_operation_generate_scene import *
from .test_operation_manifold import *
from .test_operation_merge import *
from .test_operation_merge_spatial import *
from .test_operation_merge_vertices import *
from .test_operation_misc import *
from .test_operation_optimize_materials import *
from .test_operation_optimize_primvars import *
from .test_operation_optimize_skel_roots import *
from .test_operation_optimize_timesamples import *
from .test_operation_organize_prototypes import *
from .test_operation_pivot import *
from .test_operation_prune_leaves import *
from .test_operation_python_script import *
from .test_operation_remesh_meshes import *
from .test_operation_split_merge_spatial import *
from .test_operation_split_meshes import *
from .test_operation_subdivide_meshes import *
from .test_operation_triangulate_meshes import *
from .test_operation_utility import *
from .test_python_operation import *

# Disable standalone tests until the executable is deployed.
# Otherwise the tests fail when invoked from Teamcity and the Extension Manager.
# from .test_standalone import *
