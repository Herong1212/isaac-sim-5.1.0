# Public API for module omni.simready.explorer:

## Classes

- class AssetType(Enum)
  - PROP: int
  - VEHICLE: int
  - CHARACTER: int
  - SCENE: int
  - SIGN: int
  - ROADMARK: int
  - GENERIC: int
  - UNKNOWN: int

- class AssetFactory
  - registry: Dict[AssetType, SimreadyAsset]
  - class def register(cls, asset_type: AssetType) -> Callable
  - class def create_asset(cls, raw_asset_data: Dict) -> Optional[SimreadyAsset]
  - class def num_asset_types(cls) -> int
  - class def dump_asset_types(cls)

- class SimreadyAsset(BrowserFile, abc.ABC)
  - def __init__(self, raw_asset_data: Dict)
  - class def is_asset_data(cls, raw_asset_data: Dict) -> bool
  - [property] def name(self) -> str
  - [property] def asset_type(self) -> AssetType
  - [property] def main_url(self) -> str
  - [property] def thumbnail_url(self) -> Optional[str]
  - [property] def tags(self) -> List[str]
  - [property] def labels(self) -> List[str]
  - [property] def labels_as_str(self) -> List[str]
  - [property] def tags_as_str(self) -> str
  - [property] def extent_as_str(self) -> str
  - [property] def qcode(self) -> str
  - [property] def hierarchy(self) -> str
  - [property] def hierarchy_as_str(self)
  - [property] def physics_variant(self) -> Optional[Dict]
  - [property] def behaviors(self) -> Dict[str, List[str]]

- class PropAsset(SimreadyAsset)
  - def __init__(self, raw_asset_data: Dict)
  - class def is_asset_data(cls, raw_asset_data: Dict) -> bool

## Functions

- async def find_assets(search_words: Optional[List[str]] = None) -> List[SimreadyAsset]
- def add_asset_to_stage(url: str, parent_path: Sdf.Path = Sdf.Path.emptyPath, position: Gf.Vec3d = Gf.Vec3d(0, 0, 0), variants: Optional[Dict[str, str]] = None, payload: bool = False, instanceable: bool = False) -> Tuple[bool, Sdf.Path]
- def add_asset_to_stage_using_prims(usd_context: omni.usd.UsdContext, stage: Usd.Stage, url: str, variants: Optional[Dict[str, str]] = None, replace_prims: bool = False, prim_paths: List[Sdf.Path] = []) -> Tuple[bool, Sdf.Path]
- def get_average_position_of_prims(prims: List[Usd.Prim]) -> Gf.Vec3d
- def get_selected_xformable_prim_paths(usd_context: omni.usd.UsdContext, stage: Usd.Stage) -> List[Sdf.Path]
- def refresh_browser()
