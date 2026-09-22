# Public API for module omni.mdl.neuraylib:

## Classes

- class NeurayLib
  - def ResolveTiledResourceUri(self, arg0: str) -> typing.List[str]
  - def createEditingTransaction(self, dbScopeName: str = '') -> int
  - def createMdlEntity(self, uniquePrimPath: str, dbScopeName: str = '') -> MdlEntity
  - def createMdlEntitySnapshot(self, arg0: MdlEntity) -> MdlEntitySnapshot
  - def createMdlModule(self, usdIdentifier: str, dbScopeName: str = '') -> MdlModule
  - def createMdlModuleFromDbName(self, usdIdentifier: str, dbScopeName: str = '') -> MdlModule
  - def createReadingTransaction(self, dbScopeName: str = '') -> int
  - def createScope(self, arg0: str) -> bool
  - def destroyMdlEntity(self, arg0: MdlEntity)
  - def destroyMdlEntitySnapshot(self, arg0: MdlEntitySnapshot)
  - def destroyMdlModule(self, arg0: MdlModule)
  - def destroyScope(self, arg0: str) -> bool
  - def getCurrentDefaultScope(self) -> str
  - def getNeurayAPI(self) -> int
  - def setScopeOption(self, arg0: str, arg1: str, arg2: str) -> bool

- class MdlModule
  - def valid(self) -> bool
  - [property] def dbName(self) -> str
  - [property] def dbScopeName(self) -> str
  - [property] def qualifiedName(self) -> str

- class MdlEntity
  - def getMdlModule(self) -> MdlModule
  - def valid(self) -> bool
  - [property] def dbScopeName(self) -> str
  - [property] def simpleNameWithSignature(self) -> str
  - [property] def uniquePrimPath(self) -> str

- class MdlEntitySnapshot
  - def getMdlModule(self) -> MdlModule
  - [property] def dbName(self) -> str
  - [property] def dbScopeName(self) -> str
  - [property] def simpleNameWithSignature(self) -> str

- class Interop
  - def recreateMaterialInScope(self, arg0: MdlEntitySnapshot, arg1: str, arg2: str) -> bool

## Functions

- async def create_mdl_module_async(usdIdentifier: str, dbScopeName: str = '')
- def get_neuraylib() -> NeurayLib
- def ensure_running()
- def register_extension_content(extensionName: str, contentPath: str) -> list[str]
- def deregister_extension_content(extensionName: str, registeredFiles: list[str]) -> bool
- [deprecated] def EnsureRunning()
- [deprecated] def RegisterExtensionContent(extensionName: str, contentPath: str) -> list[str]
- [deprecated] def UnregisterExtensionContent(extensionName: str, registeredFiles: list[str]) -> bool
- def create_temporary_db_scope(resolveResources: bool) -> str
- def destroy_temporary_db_scope(scopeName: str) -> bool
- def recreate_material_in_scope(materialRoot: MdlEntitySnapshot, temporaryScopeName: str) -> str
- def parse_scene_identifier_texture(sceneIdentifierTexture: str) -> tuple[str | None, str | None, float | None]
- def parse_scene_identifier_bsdf_measurement(sceneIdentifierBsdfMeasurement: str) -> str | None
- def parse_scene_identifier_light_profile(sceneIdentifierLightProfile: str) -> str | None
- def get_graph_resources(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[pymdlsdk.IValue_resource]
- def get_graph_resources_uri_masks(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]
- def get_graph_resources_uris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]
- def get_module_uris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[str]
- def get_resource_uri_mask(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource) -> str
- def get_resource_uri_list(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource, report_missing: bool = False) -> list[str]
- [deprecated] def CreateTemporaryDbScope(resolveResources: bool) -> str
- [deprecated] def DestroyTemporaryDbScope(scopeName: str) -> bool
- [deprecated] def RecreateMaterialInScope(materialRoot: MdlEntitySnapshot, temporaryScopeName: str) -> str
- [deprecated] def ParseSceneIdentifierTexture(sceneIdentifierTexture: str) -> tuple[str | None, str | None, float | None]
- [deprecated] def ParseSceneIdentifierBsdfMeasurement(sceneIdentifierBsdfMeasurement: str) -> str | None
- [deprecated] def ParseSceneIdentifierLightProfile(sceneIdentifierLightProfile: str) -> str | None
- [deprecated] def GetGraphResources(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[pymdlsdk.IValue_resource]
- [deprecated] def GetGraphResourcesUriMasks(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]
- [deprecated] def GetGraphResourcesUris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]
- [deprecated] def GetModuleUris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[str]
- [deprecated] def GetResourceUriMask(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource) -> str
- [deprecated] def GetResourceUriList(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource, report_missing: bool = False) -> list[str]
