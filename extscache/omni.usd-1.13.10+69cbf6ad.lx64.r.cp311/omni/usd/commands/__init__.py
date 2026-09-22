# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
This module provides a set of pre-defined undoable USD commands to help other extensions to implement undo/redo workflow. \
REMINDER: For those utilities that are marked as "Internal" but opened, it means those utilities are kept for back compatibility purpose, \
and should not be used out of this module. They may be deprecated or removed in the future release.
"""

__all__ = [
    "GroupPrimsCommand", "UngroupPrimsCommand", "CreatePrimWithDefaultXformCommand", "CreatePrimCommand",
    "CopyPrimCommand", "CopyPrimsCommand", "CreateInstanceCommand", "CreateInstancesCommand", "DeletePrimsCommand",
    "CreatePrimsCommand", "CreateDefaultXformOnPrimCommand", "BindMaterialCommand", "SetMaterialStrengthCommand",
    "TransformPrimCommand", "TransformPrimSRTCommand", "TransformPrimsCommand", "TransformPrimsSRTCommand",
    "FramePrimsCommand", "SelectPrimsCommand", "ToggleVisibilitySelectedPrimsCommand", "UnhideAllPrimsCommand",
    "MovePrimCommand", "MovePrimsCommand", "RenamePrimCommand", "ReplaceReferencesCommand", "CreateUsdAttributeOnPathCommand",
    "CreateUsdAttributeCommand", "ChangePropertyCommand", "RemovePropertyCommand", "ChangeMetadataInPrimsCommand",
    "ChangeMetadataCommand", "ChangeAttributesColorSpaceCommand", "CreateMdlMaterialPrimCommand",
    "CreateMtlxMaterialPrimCommand",
    "CreateShaderPrimFromSdrCommand", "CreatePreviewSurfaceMaterialPrimCommand",
    "CreatePreviewSurfaceTextureMaterialPrimCommand", "ClearCurvesSplitsOverridesCommand",
    "ClearRefinementOverridesCommand", "RelationshipTargetBase", "AddRelationshipTargetCommand",
    "RemoveRelationshipTargetCommand", "SetRelationshipTargetsCommand", "ReferenceCommandBase",
    "AddReferenceCommand", "RemoveReferenceCommand", "ReplaceReferenceCommand", "PayloadCommandBase",
    "AddPayloadCommand", "RemovePayloadCommand", "ReplacePayloadCommand", "CreatePrimCommandBase",
    "CreateReferenceCommand", "CreatePayloadCommand", "CreateAudioPrimFromAssetPathCommand", "post_notification",
    "active_edit_context", "remove_prim_spec", "prim_can_be_removed_without_destruction",
    "write_refinement_override_enabled_hint", "get_default_rotation_order_str", "get_default_camera_rotation_order_str",
    "get_default_rotation_order_type", "ensure_parents_are_active", "ToggleActivePrimsCommand", "UsdStageHelper",
    "TogglePayLoadLoadSelectedPrimsCommand", "SetPayLoadLoadSelectedPrimsCommand", "ParentPrimsCommand", "UnparentPrimsCommand",
    "AppendAPIToPrimsCommand", "RemoveAPIFromPrimsCommand"
]

import sys
from .usd_commands import *
from .stage_helper import *

# For backward compatibility. To be removed.
sys.modules["omni.kit.builtin.commands.usd_commands"] = sys.modules["omni.usd.commands"]
