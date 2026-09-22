
# Public API for module omni.asset_validator.core:

## Classes

- class AssetProgress
  - asset: str
  - progress: float

- class AssetLocatedCallback(Protocol)

- class AssetValidatedCallback(Protocol)

- class AssetProgressCallback(Protocol)

- class Results(Sequence[Issue])
  - asset: str
  - issues: list[Issue] | IssuesList
  - class def create(cls, asset: Usd.Stage | str, issues: Sequence[Issue]) -> Results
  - def filter_by(self, predicate: IssuePredicate) -> Results

- class ResultsList(Sequence[Results])
  - results: list[Results]
  - def issues(self) -> IssuesList

- class RepeatedValuesSet
  - def __init__(self, values: VtArray[ScalarType])

- class ValidationStats(_Stats)
  - def __init__(self)
  - def time_rule(self, rule: _RuleType) -> _TimeStat
  - def count_rule_severity(self, rule: _RuleType, severity: Enum)
  - def count_issues(self, issues)
  - def get_rule_times(self) -> list[tuple[_RuleType, float]]
  - def get_rule_severity_counts(self) -> list[tuple[_RuleType, Enum, int]]
  - def get_severity_count(self, severity: Enum) -> int

- class Issue
  - message: str | None
  - severity: IssueSeverity | None
  - rule: RuleType | None
  - at: Identifier[AtType] | None
  - suggestion: Suggestion | None
  - asset: StageId | None
  - code: str | None
  - requirement: Requirement | None
  - class def from_message(cls, severity: IssueSeverity, message: str) -> Issue
  - class def from_(cls, severity: IssueSeverity, rule: RuleType, message: str) -> Issue
  - class def none(cls)
  - [property] def tags(self) -> tuple[str, ...] | None
  - [property] def all_fix_sites(self) -> list[SpecId]
  - [property] def default_fix_site(self) -> SpecId | None

- class IssueSeverity(Enum)
  - ERROR: int
  - FAILURE: int
  - WARNING: int
  - INFO: int
  - NONE: int

- class AttributeId(PropertyId)
  - class def from_(cls, attr: Usd.Attribute) -> AttributeId

- class Identifier(Generic[AtType])
  - class def from_(cls, obj: AtType) -> Identifier[AtType]
  - def restore(self, stage: Usd.Stage) -> AtType
  - def as_str(self) -> str
  - def get_layer_ids(self) -> list[LayerId]
  - def get_spec_ids(self) -> list[SpecId]

- class LayerId(Identifier[Sdf.Layer])
  - identifier: str
  - class def from_(cls, layer: Sdf.Layer) -> LayerId
  - def restore(self, stage: Usd.Stage) -> Sdf.Layer
  - def get_spec_ids(self) -> list[SpecId]
  - def as_str(self)

- class PrimId(Identifier[Usd.Prim], VariantIdMixin)
  - stage_id: StageId
  - spec_ids: SpecIdList
  - variant_selection_path: Sdf.Path
  - class def from_(cls, prim: Usd.Prim) -> PrimId
  - def restore(self, stage: Usd.Stage) -> Usd.Prim
  - [property] def path(self) -> Sdf.Path
  - def as_str(self) -> str
  - def get_spec_ids(self) -> list[SpecId]

- class PropertyId(Identifier[Usd.Attribute], VariantIdMixin)
  - prim_id: PrimId
  - path: Sdf.Path
  - [property] def variant_selection_path(self)
  - class def from_(cls, prop: Usd.Property) -> PropertyId
  - def restore(self, stage: Usd.Stage) -> Usd.Property
  - [property] def name(self) -> str
  - [property] def stage_id(self) -> StageId
  - def as_str(self) -> str
  - def get_spec_ids(self) -> list[SpecId]

- class SpecId(Identifier[Sdf.Spec])
  - layer_id: LayerId
  - path: Sdf.Path
  - class def from_(cls, spec: Sdf.Spec) -> SpecId
  - def restore(self, stage: Usd.Stage) -> Sdf.Spec
  - def get_spec_ids(self) -> list[SpecId]
  - def as_str(self) -> str

- class SpecIdList
  - root_path: Sdf.Path
  - spec_ids: list[SpecId]
  - class def from_(cls, prim: Usd.Prim) -> SpecIdList

- class StageId(Identifier[Usd.Stage])
  - root_layer: LayerId
  - class def from_(cls, stage: Usd.Stage) -> StageId
  - [property] def identifier(self) -> str
  - [property] def stage_id(self) -> StageId
  - def restore(self, stage: Usd.Stage) -> Usd.Stage
  - def as_str(self) -> str
  - def get_spec_ids(self) -> list[SpecId]

- class SchemaBaseId(Identifier[Usd.SchemaBase], VariantIdMixin)
  - prim_id: PrimId
  - schema_class: Any
  - instance_name: str | None
  - [property] def variant_selection_path(self)
  - class def from_(cls, instance: Usd.SchemaBase) -> SchemaBaseId
  - [property] def path(self) -> Sdf.Path
  - def restore(self, stage: Usd.Stage) -> Any
  - def get_spec_ids(self) -> list[SpecId]
  - def as_str(self) -> str

- class Suggestion
  - callable: Callable[[Usd.Stage, AtType], None]
  - message: str
  - at: list[Identifier[AtType]] | None

- class VariantIdMixin
  - [property] def variant_selection_path(self) -> Sdf.Path
  - static def get_variant_selection_path(prim: Usd.Prim) -> Sdf.Path
  - def restore_variant_selection(self, stage: Usd.Stage)

- class BaseRuleChecker
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def GetIssues(self) -> Sequence[Issue]
  - class def GetDescription(cls)
  - def CheckStage(self, usdStage)
  - def CheckDiagnostics(self, diagnostics)
  - def CheckUnresolvedPaths(self, unresolvedPaths)
  - def CheckDependencies(self, usdStage, layerDeps, assetDeps)
  - def CheckLayer(self, layer)
  - def CheckZipFile(self, zipFile, packagePath)
  - def CheckPrim(self, prim)
  - def ResetCaches(self)

- class IssueCSVData
  - headers: list[str]
  - assets: list[str]
  - rules: list[str]
  - messages: list[str]
  - severities: list[str]
  - suggestions: list[str]
  - ats: list[str]
  - additional_column: dict[str, list[str]]
  - class def from_(cls, value: Issue | list[Issue] | IssuesList | Results | ResultsList)
  - def append_column(self, header: str, values: Sequence[str])
  - def get_csv_as_str(self, headers: list[str] | None = None, delimiter: str = ',') -> str
  - def export_csv(self, file_url: str | pathlib.Path, headers: list[str] | None = None, delimiter: str = ',')

- class IssueJSONEncoder(json.JSONEncoder)
  - def __init__(self, rules: list[BaseRuleChecker] | None = None, *args, **kwargs)
  - def default(self, o: Any) -> Any

- class IssuesList(Sequence[Issue])
  - issues: list[Issue]
  - success: list[Issue]
  - name: Any | None
  - def filter_by(self, predicate: IssuePredicate | None = None) -> IssuesList
  - def group_by(self, group_by: IssueGroupBy | None = None) -> list[IssuesList]
  - def merge(self, other: IssuesList) -> IssuesList

- class IssueGroupBy(Protocol)

- class IssuePredicate(Protocol)

- class IssueGroupsBy
  - class def asset(cls) -> IssueGroupBy
  - class def rule(cls) -> IssueGroupBy
  - class def rule_name(cls) -> IssueGroupBy
  - class def severity(cls) -> IssueGroupBy
  - class def message(cls) -> IssueGroupBy
  - class def code(cls) -> IssueGroupBy
  - class def requirement(cls) -> IssueGroupBy

- class IssuePredicates
  - static def Any() -> IssuePredicate
  - static def IsFailure() -> IssuePredicate
  - static def IsWarning() -> IssuePredicate
  - static def IsError() -> IssuePredicate
  - static def IsInfo() -> IssuePredicate
  - static def IsSuccess() -> IssuePredicate
  - static def ContainsMessage(text: str) -> IssuePredicate
  - static def IsRule(rule: str | RuleType) -> IssuePredicate
  - static def HasLocation() -> IssuePredicate
  - static def HasFix() -> IssuePredicate
  - static def HasRootLayer() -> IssuePredicate
  - static def And(*predicates) -> IssuePredicate
  - static def Or(*predicates) -> IssuePredicate
  - static def Not(predicate: IssuePredicate) -> IssuePredicate
  - static def HasCode() -> IssuePredicate
  - static def MatchesCode(code: str) -> IssuePredicate
  - static def MatchesAnyCode(codes: Sequence[str]) -> IssuePredicate
  - static def MatchesToken(token: str) -> IssuePredicate
  - static def HasTag(tag: str) -> IssuePredicate

- class FixResult
  - issue: Issue
  - status: FixStatus
  - exception: Exception | None

- class FixStatus(Enum)
  - NO_LOCATION: int
  - NO_SUGGESTION: int
  - FAILURE: int
  - SUCCESS: int
  - NO_LAYER: int
  - INVALID_LOCATION: int

- class IssueFixer
  - asset: AssetType
  - layers: set[Sdf.Layer]
  - def apply(self, issue: Issue, at: Identifier[AtType] | None = None) -> FixResult
  - def fix(self, issues: list[Issue]) -> Sequence[FixResult]
  - def fix_at(self, issues: list[Issue], layer: Sdf.Layer) -> Sequence[FixResult]
  - [property] def fixed_layers(self) -> list[Sdf.Layer]
  - def save(self)

- class Requirement(Protocol)
  - code: str
  - display_name: str | None
  - message: str | None
  - path: str | None
  - tags: tuple[str, Ellipsis]

- class RequirementsRegistry
  - [property] def requirements(self) -> list[Requirement]
  - [property] def rules(self)
  - def get_requirements(self, rule: type[BaseRuleChecker]) -> list[Requirement]
  - def get_validator(self, requirement: Requirement) -> type[BaseRuleChecker] | None
  - def get_validators(self, requirements: list[Requirement]) -> list[type[BaseRuleChecker]]
  - def is_implemented(self, requirement: Requirement) -> bool
  - def all_implemented(self, requirements: list[Requirement]) -> bool
  - def is_registered(self, rule: type[BaseRuleChecker], requirement: Requirement) -> bool
  - def get_requirement_from_code(self, requirement_code: str) -> Requirement | None

- class CapabilityRegistry(VersionedRegistry[Capability])
  - def __init__(self)
  - def create_key(self, value: Capability) -> IdVersion
  - [property] def capabilities(self) -> list[Capability]
  - [property] def latest_capabilities(self) -> list[Capability]
  - def get_capability_ids(self) -> list[str]
  - def add_capability(self, capability: Capability)
  - def find_capability(self, id: str, version: str | None = None) -> Capability | None

- class Capability(Protocol)
  - id: str
  - version: str
  - path: str
  - requirements: list[Requirement]

- class ProfileRegistry(VersionedRegistry[Profile])
  - def __init__(self)
  - def create_key(self, value: Profile) -> IdVersion
  - [property] def profiles(self) -> list[Profile]
  - def add_profile(self, profile: Profile)
  - def find_profile(self, id: str, version: str | None = None) -> Profile | None

- class Profile(Protocol)
  - id: str
  - version: str
  - path: str
  - capabilities: list[Capability]

- class Feature(Protocol)
  - id: str
  - version: str
  - path: str
  - requirements: list[Requirement]

- class FeatureRegistry(VersionedRegistry[Feature])
  - def __init__(self)
  - def create_key(self, value: Feature) -> IdVersion

- class OmniComplianceChecker(ComplianceChecker)

- class ValidationEngine(_ValidationEngine)
  - def __init__(self)
  - [property] def initialized_rules(self) -> list[type[BaseRuleChecker]]

- class ValidationRulesRegistry
  - static def init()
  - static def categories(enabledOnly: bool = False) -> tuple[str, Ellipsis]
  - static def rules(category: str, enabledOnly: bool = False) -> tuple[type[BaseRuleChecker], Ellipsis]
  - static def registerRule(rule: type[BaseRuleChecker], category: str)
  - static def deregisterRule(rule: type[BaseRuleChecker])
  - static def rule(name: str) -> type[BaseRuleChecker] | None
  - static def category(rule: type[BaseRuleChecker]) -> str
  - static def add_registry_rule_callback(callback: Callable[[], None])

- class ByteAlignmentChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckZipFile(self, zipFile, packagePath)

- class CompressionChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckZipFile(self, zipFile, packagePath)

- class MissingReferenceChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, stage: Usd.Stage)
  - def CheckDiagnostics(self, diagnostics)
  - def CheckUnresolvedPaths(self, unresolvedPaths)

- class NormalMapTextureChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckPrim(self, prim)

- class PrimEncapsulationChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckPrim(self, prim)
  - def ResetCaches(self)

- class StageMetadataChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, usdStage)

- class TextureChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, usdStage)
  - def CheckPrim(self, prim)

- class AnchoredAssetPathsChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def CheckStage(self, stage)
  - def CheckLayer(self, layer)

- class SupportedFileTypesChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def CheckZipFile(self, zip_file: Usd.ZipFile, package_path: str)
  - def CheckUnresolvedPaths(self, unresolvedPaths: list[str])
  - def CheckDependencies(self, _, layer_deps: list[Sdf.Layer], asset_deps: list[str])

- class UsdzUdimLimitationChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def CheckZipFile(self, _: Usd.ZipFile, package_path: str)

- class IndexedPrimvarChecker(BaseRuleChecker)
  - def CheckPrim(self, prim: Usd.Prim)

- class ManifoldChecker(BaseRuleChecker)
  - def CheckPrim(self, prim: Usd.Prim)

- class SubdivisionSchemeChecker(BaseRuleChecker)
  - class def set_to_none(cls, _: Usd.Stage, mesh: UsdGeom.Mesh)
  - class def set_to_catmull_clark(cls, _: Usd.Stage, mesh: UsdGeom.Mesh)
  - def CheckPrim(self, prim: Usd.Prim)

- class UnusedMeshTopologyChecker(BaseRuleChecker)
  - class def remove_unreferenced_points(cls, _: Usd.Stage, prim: Usd.Prim)
  - def CheckPrim(self, prim: Usd.Prim)

- class UnusedPrimvarChecker(BaseRuleChecker)
  - def CheckPrim(self, prim: Usd.Prim)
  - static def remove_unreferenced_values(_: Usd.Stage, attr: Usd.Attribute)

- class ValidateTopologyChecker(BaseRuleChecker)
  - def validate(self, mesh: UsdGeom.Mesh)
  - def CheckPrim(self, prim: Usd.Prim)

- class WeldChecker(BaseRuleChecker)
  - def validate_mesh(self, mesh: UsdGeom.Mesh)
  - def CheckPrim(self, prim: Usd.Prim)

- class ZeroAreaFaceChecker(BaseRuleChecker)
  - def validate_mesh(self, mesh: UsdGeom.Mesh)
  - def CheckPrim(self, prim: Usd.Prim)

- class AlmostExtremeExtentChecker(BaseBoundsChecker)
  - BOUNDS_LIMIT: BoundsLimit

- class PointsPrecisionErrorChecker(PointsPrecisionChecker)
  - PRECISION_LIMIT: PrecisionLimit
  - SEVERITY: IssueSeverity

- class PointsPrecisionWarningChecker(PointsPrecisionChecker)
  - PRECISION_LIMIT: PrecisionLimit
  - SEVERITY: IssueSeverity

- class SkelBindingAPIAppliedChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - class def apply_api(cls, _: Usd.Stage, prim: Usd.Prim)
  - def CheckPrim(self, prim: Usd.Prim)

- class UsdAsciiPerformanceChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def CheckLayer(self, layer: Sdf.Layer)

- class UsdDanglingMaterialBinding(BaseRuleChecker)
  - class def apply_dangling_material_binding_fix(cls, _: Usd.Stage, prim)
  - def CheckPrim(self, prim)

- class UsdGeomSubsetChecker(BaseRuleChecker)
  - class def apply_family_name_fix(cls, _: Usd.Stage, subset: UsdGeom.Subset)
  - def CheckPrim(self, prim)

- class UsdLuxSchemaChecker(BaseRuleChecker)
  - LUX_ATTRIBUTES: set[str]
  - class def fix_attribute_name(cls, _: Usd.Stage, attribute: Usd.Attribute)
  - def CheckPrim(self, prim)

- class UsdMaterialBindingApi(BaseRuleChecker)
  - class def apply_material_binding_api_fix(cls, _: Usd.Stage, prim)
  - def CheckPrim(self, prim)

- class ExtentsChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def CheckPrim(self, prim: Usd.Prim)
  - def ResetCaches(self)

- class KindChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckPrim(self, prim)
  - def fix_ancestors_kind_with_components(self, _: Usd.Stage, prim: Usd.Prim)
  - def fix_ancestors_empty_kind(self, _: Usd.Stage, prim: Usd.Prim)
  - def ResetCaches(self)

- class TypeChecker(BaseRuleChecker)
  - def CheckPrim(self, prim)

- class OmniDefaultPrimChecker(DefaultPrimChecker)

- class OmniOrphanedPrimChecker(DanglingOverPrimChecker)

- class MaterialPathChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - def CheckUnresolvedPaths(self, unresolvedPaths)
  - def CheckDependencies(self, usdStage, layerDeps, assetDeps)
  - class def fix_path_callback(cls, stage: Usd.Stage, attribute: Usd.Attribute)
  - def CheckPrim(self, prim)

- class MaterialOutOfScopeChecker(BaseRuleChecker)
  - def CheckPrim(self, prim: Usd.Prim)

- class MaterialOldMdlSchemaChecker(BaseRuleChecker)
  - def update_deprecated_mdl_schema(self, _: Usd.Stage, prim: Usd.Prim) -> bool
  - def CheckPrim(self, prim)

- class ShaderImplementationSourceChecker(BaseRuleChecker)
  - def CheckPrim(self, prim)

- class LayerSpecChecker(BaseRuleChecker)
  - def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool)
  - static def fix_unsupported_field_callback(stage: Usd.Stage, spec: Sdf.Spec, field)
  - static def fix_time_varying_relationship_callback(stage: Usd.Stage, spec: Sdf.AttributeSpec)
  - def CheckLayer(self, layer: Sdf.Layer)

- class OmniSkelUpgradeChecker(BaseRuleChecker)
  - NV_SKINNING_METHOD: str
  - NV_SKINNING_BLEND_WEIGHTS: str
  - STOCK_SKINNING_METHOD: str
  - NV_STOCK_SKINNING_METHOD_MAP: Dict
  - OMNI_SKINNING_BLEND_WEIGHT_SCHEMA: str
  - OMNI_SKINNING_BLEND_WEIGHT_ATTR: str
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def migrate_skinning_method(self, stage: Usd.Stage, prim: Usd.Prim)
  - def migrate_weighted_blend_schema(self, stage: Usd.Stage, prim: Usd.Prim)
  - def remove_nv_skinning_method(self, stage: Usd.Stage, prim: Usd.Prim)
  - def CheckPrim(self, prim: Usd.Prim)

- class UnicodeNameChecker(BaseRuleChecker)
  - def CheckStage(self, usdStage: Usd.Stage)
  - def CheckPrim(self, prim: Usd.Prim)
  - def CheckLayer(self, layer)

- class OmniMaterialUsdPreviewSurfaceChecker(MaterialUsdPreviewSurfaceChecker)
  - INPUTS_TO_SKIP: List

- class RigidBodyChecker(BaseRuleCheckerWCache)
  - def CheckPrim(self, usd_prim: Usd.Prim)

- class ColliderChecker(BaseRuleCheckerWCache)
  - def CheckPrim(self, usd_prim: Usd.Prim)

- class PhysicsJointChecker(BaseRuleChecker)
  - def CheckPrim(self, usd_prim: Usd.Prim)

- class ArticulationChecker(BaseRuleCheckerWCache)
  - def CheckPrim(self, usd_prim: Usd.Prim)

## Functions

- def to_identifier(value: AtType | None) -> Identifier[AtType] | None
- def to_identifiers(value: list[AtType] | None) -> list[Identifier[AtType]] | None
- def AuthoringLayers(at: AtType | list[AtType]) -> list[Sdf.Layer]
- def get_version()
- def export_json_file(json_output_path: str | pathlib.Path, entry: Results | ResultsList | IssuesList | Issue | Suggestion)
- def register_requirements(*requirements: Requirement) -> Callable[[type[BaseRuleChecker]], type[BaseRuleChecker]]
- def is_omni_path(path: Sdf.Path) -> bool
- def create_validation_parser() -> argparse.ArgumentParser
- def registerRule(category: str, skip: bool = False) -> Callable[[type[BaseRuleChecker]], type[BaseRuleChecker]]
- def add_registry_rule_callback(callback: Callable[[], None])
- def is_omni_skel_upgrade_disabled() -> bool
- def normalize_url(path_or_url: str) -> str

## Variables

- AssetType: Unknown
- AtType: Unknown
- ValidationArgsExec: ValidationNamespaceExec

# Public API for module omni.asset_validator.simready:

## Classes

- class EnvironmentCapabilityChecker(BaseRuleChecker)
  - OPEN_DRIVE_PROP_NAME: str
  - SIGNAL_ID_ATTR_NAME: str
  - def CheckStage(self, usdStage: Usd.Stage)

- class EnvironmentLightCapabilityChecker(BaseRuleChecker)
  - BEHAVIORS_ATTR_NAME: str
  - BEHAVIORS_ATTR_VALUE: List
  - SIM_PBR_SHADERS: List
  - def CheckStage(self, usdStage: Usd.Stage)

- class GroundTruthCapabilityChecker(BaseRuleChecker)
  - QCODE_RE: Unknown
  - SEMANTIC_INSTANCE_NAME: str
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, stage: Usd.Stage)
  - def CheckPrim(self, prim: Usd.Prim)
  - def ResetCaches(self)

- class NonVisualSensorCapabilityChecker(BaseRuleChecker)
  - ATTRIBUTE_RULES: Dict
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, stage: Usd.Stage)
  - def CheckPrim(self, prim: Usd.Prim)
  - def checkMaterial(self, material: UsdShade.Material)
  - def ResetCaches(self)

- class PedestrianCapabilityChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, stage: Usd.Stage)
  - def CheckPrim(self, prim: Usd.Prim)
  - def ResetCaches(self)

- class TrafficLightCapabilityChecker(BaseRuleChecker)
  - SIGNAL_TYPE_ATTR_NAME: str
  - SIGNAL_TYPE_ATTR_VALUE: str
  - SIGNAL_ATTR_NAME: str
  - SIGNAL_ORDER_ATTR_NAME: str
  - SIGNAL_VALUES: List
  - DOMAIN_INTENSITY_ATTR_NAME: str
  - SIM_PBR_SHADERS: List
  - def CheckStage(self, usdStage: Usd.Stage)

- class VehicleCapabilityChecker(BaseRuleChecker)
  - def __init__(self, verbose, consumerLevelChecks, assetLevelChecks)
  - def CheckStage(self, usdStage: Usd.Stage)
  - def CheckPrim(self, prim: Usd.Prim)

- class VisualSensorCapabilityChecker(BaseRuleChecker)
  - def CheckStage(self, stage: Usd.Stage)
  - def CheckPrim(self, prim: Usd.Prim)

- class UpAxisZChecker(BaseRuleChecker)
  - def CheckStage(self, stage: Usd.Stage)

- class MetersPerUnit1Checker(BaseRuleChecker)
  - def CheckStage(self, stage: Usd.Stage)

- class ContainsMeshChecker(BaseRuleChecker)
  - def CheckStage(self, stage: Usd.Stage)
