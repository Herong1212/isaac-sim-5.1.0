# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Library of material UI functions and bridge to lower level neuray_lib.
"""

__all__ = ['multi_descendents_dialog', 'drop_material', 'bind_material_to_selected_prims', 'get_material_prim_path', 'create_mdl_material', 'create_mtlx_material', 'get_material_filename_from_prim', 'CreateAndBindMdlMaterialFromLibrary', 'CreateAndBindPreviewSurfaceFromLibrary', 'CreateAndBindPreviewSurfaceTextureFromLibrary', 'get_mdl_lib_paths', 'get_mdl_usd_source_asset_list', 'get_material_hidden_list', 'get_mdl_list_async', 'get_mdl_list', 'add_material_list_refresh_callback', 'remove_material_list_refresh_callback', 'delayed_material_list_refresh', 'add_material_list_item', 'remove_material_list_item', 'material_list_refresh', 'get_material_list', 'custom_material_dialog', 'get_instance', 'get_subidentifier_from_material', 'get_subidentifier_from_mdl', 'remove_mdl_from_cache', 'get_material_enums', 'bind_material_to_prims_dialog', 'add_usd_source_asset_path_to_mtl_lib', 'remove_usd_source_asset_path_from_mtl_lib', 'add_to_mtl_lib', 'remove_from_mtl_lib', 'UpdateState', 'MaterialUtils', 'initalize_material_utils', 'destroy_material_utils', 'add_cache_changed_fn', 'remove_cache_changed_fn', 'get_materials_from_stage', 'get_materials_from_stage_async', 'add_materials_from_stage_filter_func', 'remove_materials_from_stage_filter_func', 'get_prim_children_paths', 'get_cache_filename', 'SearchWidget']

from .material_library import *
from .material_library import MaterialLibraryExtension
from .material_utils import *

from .search_widget import SearchWidget