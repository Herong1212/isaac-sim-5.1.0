# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
The Omni USD extension is the Python frontend of extension omni.usd.core. \
REMINDER: For those utilities that are marked as "Internal" but opened, it means those utilities are kept for back compatibility purpose, \
and should not be used out of this module. They may be deprecated or removed in the future release.
"""
__all__ = [
    "HydraEngineCreationConfig", "EngineCreationFlags", "OpaqueSharedHydraEngineContext", "create_hydra_engine",
    "destroy_hydra_engine", "AudioManager", "PickingMode", "PrimCaching", "Selection", "StageEventType",
    "StageRenderingEventType", "StageState", "TransformHelper", "UsdContext", "UsdContextInitialLoadSet",
    "UsdWatcher", "Value_On_Layer", "attach_all_hydra_engines", "attr_has_timesample_on_key",
    "can_be_copied", "can_prim_have_children", "check_ancestral", "clear_attr_val_at_time",
    "copy_timesamples_from_weaker_layer", "create_context", "create_material_input", "destroy_context", "duplicate_prim",
    "find_path_in_nodes", "find_spec_on_session_or_its_sublayers", "get_all_sublayers",
    "get_attribute_effective_defaultvalue_layer_info", "get_attribute_effective_timesample_layer_info",
    "get_attribute_effective_value_layer_info", "get_authored_prim", "get_composed_payloads_from_prim",
    "get_composed_references_from_prim", "get_context", "get_dirty_layers", "get_edit_target_identifier",
    "get_frame_time", "get_frame_time_code", "get_introducing_layer", "get_local_transform_SRT",
    "get_local_transform_matrix", "get_prim_at_path", "get_prim_descendents", "get_prop_at_path", "get_sdf_layer",
    "get_shader_from_material", "get_stage_next_free_path", "get_subidentifier_from_material", "get_subidentifier_from_mdl",
    "get_timesamples_count_in_authoring_layer", "get_url_from_prim", "get_watcher", "get_world_transform_matrix",
    "handle_exception", "is_ancestor_prim_type", "is_child_type", "is_hidden_type", "is_layer_locked",
    "is_layer_writable", "is_path_valid", "is_prim_material_supported", "is_usd_readable_filetype",
    "is_usd_writable_filetype", "make_path_relative_to_current_edit_target", "merge_layers", "merge_prim_spec",
    "on_layers_saved_result", "on_stage_result", "readable_usd_dotted_file_exts", "readable_usd_file_exts",
    "readable_usd_file_exts_str", "readable_usd_files_desc", "readable_usd_re", "release_all_hydra_engines",
    "remove_property", "resolve_paths", "resolve_prim_path_references", "resolve_prim_paths_references",
    "set_attr_val", "set_edit_target_by_identifier", "set_prop_val", "shutdown_usd", "stitch_prim_specs",
    "writable_usd_dotted_file_exts", "writable_usd_file_exts", "writable_usd_file_exts_str", "writable_usd_files_desc",
    "writable_usd_re", "get_context_from_stage", "get_context_from_stage_id", "correct_filename_case",
    "gather_default_attributes", "get_prop_auto_target_session_layer", "get_geometry_standard_prim_list",
    "get_light_prim_list", "make_valid_identifier", "create_hydra_engine_with_config", "add_hydra_engine", 
    "HydraEngineInvalidUniqueId", "is_usd_crate_file", "is_usd_crate_file_version_supported",
    "stage_event_name", "stage_event_type", "stage_rendering_event_name", "stage_rendering_event_type",
]
from ._impl import *
