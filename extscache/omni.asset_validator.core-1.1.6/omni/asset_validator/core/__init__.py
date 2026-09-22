# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

# For backwards compatibility
from omni.asset_validator._impl import (
    AssetLocatedCallback,
    AssetProgress,
    AssetProgressCallback,
    AssetType,
    AssetValidatedCallback,
    AttributeId,
    AtType,
    AuthoringLayers,
    BaseRuleChecker,
    Capability,
    CapabilityRegistry,
    Feature,
    FeatureRegistry,
    FixResult,
    FixStatus,
    Identifier,
    Issue,
    IssueCSVData,
    IssueFixer,
    IssueGroupBy,
    IssueGroupsBy,
    IssueJSONEncoder,
    IssuePredicate,
    IssuePredicates,
    IssueSeverity,
    IssuesList,
    LayerId,
    PrimId,
    Profile,
    ProfileRegistry,
    PropertyId,
    RepeatedValuesSet,
    Requirement,
    RequirementsRegistry,
    Results,
    ResultsList,
    SchemaBaseId,
    SpecId,
    SpecIdList,
    StageId,
    Suggestion,
    ValidationArgsExec,
    ValidationStats,
    VariantIdMixin,
    create_validation_parser,
    export_json_file,
    get_version,
    normalize_url,
    register_requirements,
    to_identifier,
    to_identifiers,
)

from ._atomic_asset_rules import (
    AnchoredAssetPathsChecker,
    SupportedFileTypesChecker,
    UsdzUdimLimitationChecker,
)
from ._base_rules import (
    ByteAlignmentChecker,
    CompressionChecker,
    MissingReferenceChecker,
    NormalMapTextureChecker,
    PrimEncapsulationChecker,
    StageMetadataChecker,
    TextureChecker,
)
from ._basic_rules import ExtentsChecker, KindChecker, TypeChecker
from ._compliance_checker import OmniComplianceChecker, is_omni_path
from ._engine import ValidationEngine, ValidationRulesRegistry, add_registry_rule_callback, registerRule
from ._misc_checkers import (
    AlmostExtremeExtentChecker,
    PointsPrecisionErrorChecker,
    PointsPrecisionWarningChecker,
    SkelBindingAPIAppliedChecker,
    UsdAsciiPerformanceChecker,
    UsdDanglingMaterialBinding,
    UsdGeomSubsetChecker,
    UsdLuxSchemaChecker,
    UsdMaterialBindingApi,
)
from ._omni_geometry import (
    IndexedPrimvarChecker,
    ManifoldChecker,
    SubdivisionSchemeChecker,
    UnusedMeshTopologyChecker,
    UnusedPrimvarChecker,
    ValidateTopologyChecker,
    WeldChecker,
    ZeroAreaFaceChecker,
)
from ._omni_layout import OmniDefaultPrimChecker, OmniOrphanedPrimChecker
from ._omni_material import (
    MaterialOldMdlSchemaChecker,
    MaterialOutOfScopeChecker,
    MaterialPathChecker,
    ShaderImplementationSourceChecker,
)
from ._omni_material_2211 import OmniMaterialUsdPreviewSurfaceChecker
from ._sdf_layer_checker import LayerSpecChecker
from ._usd_physics import (
    ArticulationChecker,
    ColliderChecker,
    PhysicsJointChecker,
    RigidBodyChecker,
)
from ._usd_skel import OmniSkelUpgradeChecker, is_omni_skel_upgrade_disabled
from ._utf8_checkers import UnicodeNameChecker

__all__ = [
    # Base types
    "AssetType",
    "AssetProgress",
    "AssetLocatedCallback",
    "AssetValidatedCallback",
    "AssetProgressCallback",
    "Results",
    "ResultsList",
    "RepeatedValuesSet",
    "ValidationStats",
    "Issue",
    "IssueSeverity",
    "AtType",
    "AttributeId",
    "Identifier",
    "LayerId",
    "PrimId",
    "PropertyId",
    "SpecId",
    "SpecIdList",
    "StageId",
    "SchemaBaseId",
    "Suggestion",
    "VariantIdMixin",
    "to_identifier",
    "to_identifiers",
    "BaseRuleChecker",
    "IssueCSVData",
    "IssueJSONEncoder",
    "IssuesList",
    "IssueGroupBy",
    "IssuePredicate",
    "IssueGroupsBy",
    "IssuePredicates",
    "AuthoringLayers",
    "FixResult",
    "FixStatus",
    "IssueFixer",
    "get_version",
    "export_json_file",
    "Requirement",
    "RequirementsRegistry",
    "register_requirements",
    "CapabilityRegistry",
    "Capability",
    "ProfileRegistry",
    "Profile",
    "Feature",
    "FeatureRegistry",
    # Compliance checker
    "OmniComplianceChecker",
    "is_omni_path",
    # Parser
    "create_validation_parser",
    "ValidationArgsExec",
    # Engine
    "ValidationEngine",
    "ValidationRulesRegistry",
    "registerRule",
    "add_registry_rule_callback",
    # Base rules
    "ByteAlignmentChecker",
    "CompressionChecker",
    "MissingReferenceChecker",
    "NormalMapTextureChecker",
    "PrimEncapsulationChecker",
    "StageMetadataChecker",
    "TextureChecker",
    # Atomic Asset Checker
    "AnchoredAssetPathsChecker",
    "SupportedFileTypesChecker",
    "UsdzUdimLimitationChecker",
    # Geometry rules
    "IndexedPrimvarChecker",
    "ManifoldChecker",
    "SubdivisionSchemeChecker",
    "UnusedMeshTopologyChecker",
    "UnusedPrimvarChecker",
    "ValidateTopologyChecker",
    "WeldChecker",
    "ZeroAreaFaceChecker",
    # Misc checkers
    "AlmostExtremeExtentChecker",
    "PointsPrecisionErrorChecker",
    "PointsPrecisionWarningChecker",
    "SkelBindingAPIAppliedChecker",
    "UsdAsciiPerformanceChecker",
    "UsdDanglingMaterialBinding",
    "UsdGeomSubsetChecker",
    "UsdLuxSchemaChecker",
    "UsdMaterialBindingApi",
    # Basic rules
    "ExtentsChecker",
    "KindChecker",
    "TypeChecker",
    # Layout rules
    "OmniDefaultPrimChecker",
    "OmniOrphanedPrimChecker",
    # Material rules
    "MaterialPathChecker",
    "MaterialOutOfScopeChecker",
    "MaterialOldMdlSchemaChecker",
    "ShaderImplementationSourceChecker",
    # Layer checker
    "LayerSpecChecker",
    # Skeleton rules
    "OmniSkelUpgradeChecker",
    "is_omni_skel_upgrade_disabled",
    # UTF8 checkers
    "UnicodeNameChecker",
    # Material 2211 rules
    "OmniMaterialUsdPreviewSurfaceChecker",
    # Physics rules
    "RigidBodyChecker",
    "ColliderChecker",
    "PhysicsJointChecker",
    "ArticulationChecker",
    # URL Utils
    "normalize_url",
]
