# Public API for module omni.mdl.usd_converter:

## Classes

- class DiscoveryExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class OutputType(Enum)
  - SHADER: int
  - MATERIAL: int
  - MATERIAL_AND_GEOMETRY: int

## Functions

- def is_material_bound_to_prim(stage: Usd.Stage, materialPrim: Usd.Prim)
- def is_shader_resolved(stage: Usd.Stage, materialPrim: Usd.Prim)
- def mdl_to_usd(moduleName: str, searchPath: str = None, targetFolder: str = MDL_AUTOGEN_PATH, targetFilename: str = None, output: mdl_usd.OutputType = mdl_usd.OutputType.SHADER, nestedShaders: bool = False)
- def build_shader_node_for_material(prim: mdl_usd.Usd.Prim, merge_identical_subgraphs_after_expand: bool = False)
- async def usd_to_mdl(path: str, prim: mdl_usd.Usd.Prim, forceNotOV: bool = False)
- async def expand_mdl_material_parameters(moduleName, stage: Usd.Stage, materialPrim: Usd.Prim)
- def merge_identical_subgraphs(stage, start_prim_path: str = '/', dry_run: bool = False)

## Variables

- MDL_AUTOGEN_PATH: str
