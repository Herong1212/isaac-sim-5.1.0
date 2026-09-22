import omni.mdl.pymdlsdk as pymdlsdk
from .._neuraylib import NeurayLib, MdlEntitySnapshot
from ..scripts.entrypoints import get_neuraylib
import uuid
import carb
import omni.kit.app


def create_temporary_db_scope(resolveResources: bool) -> str:
    R"""
    Create a temporary scope for processing independent of the renderer scopes.

    :type resolveResources: bool
    :param resolveResources: Resolve MDL resources on module load. The RTX renderer for instance sets this to 'False'.
                             If 'False', resources need to be resolved manually.

    :return: The name of the temporary db scope
    """
    ov_neuraylib: NeurayLib = get_neuraylib()
    scopeName: str = ""
    created: bool = False
    while not created:
        scopeName: str = "tmp_" + str(uuid.uuid4()) + "_scope"
        created = ov_neuraylib.createScope(scopeName)
    if resolveResources:
        if not ov_neuraylib.setScopeOption(scopeName, "ResolveResources", "on"):
            carb.log_error(f"Failed to set 'ResolveResources' option on temporary scope {scopeName}.")
            return ""
    return scopeName


def destroy_temporary_db_scope(scopeName: str) -> bool:
    R"""
    Create a temporary scope for processing independent of the renderer scopes.

    :type scopeName: str
    :param scopeName: Name of the temporary scope to delete.

    :return: True if the scope was deleted. False if it wasn't a temporary scope or it did not exist.
    """
    if not scopeName.startswith('tmp_'):
        return False  # little bit of safety

    ov_neuraylib = get_neuraylib()
    return ov_neuraylib.destroyScope(scopeName)


def recreate_material_in_scope(materialRoot: MdlEntitySnapshot, temporaryScopeName: str) -> str:
    R"""
    Replicated a given material graph in a user-defined scope.
    This is meant to be used for exporting, baking and other tooling tasks.
    Note, the modules and created function calls are not visible to rtx.neuraylib.

    :type materialRoot: MdlEntitySnapshot
    :param materialRoot: The rtx.neuraylib material root node to process.

    :type temporaryScopeName: str
    :param temporaryScopeName: Name of the target scope.

    :return: The DB name of the recreated material in the temporary scope or empty string in case of failure.
             If the scope is not a temporay scope, 'False' is returned as well without attempting to recreate.
    """
    if not temporaryScopeName.startswith('tmp_'):
        return ""  # little bit of safety

    ov_neuraylib: NeurayLib = get_neuraylib()
    _interop = ov_neuraylib._getInterop()
    res: bool = _interop.recreateMaterialInScope(materialRoot, temporaryScopeName, materialRoot.dbName)
    if not res:
        return ""

    tmpTransaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_neuraylib.createReadingTransaction(temporaryScopeName))
    recreatedMaterial: pymdlsdk.IFunction_call = tmpTransaction.access_as(pymdlsdk.IFunction_call, materialRoot.dbName)
    dbName: str = materialRoot.dbName if recreatedMaterial.is_valid_interface() else ""
    recreatedMaterial = None
    tmpTransaction.abort()
    tmpTransaction = None
    return dbName


def get_resource_uri_mask(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource) -> str:
    R"""
    Computes or resolves the URI for a given resource.

    :type transaction: pymdlsdk.ITransaction
    :param transaction: The DB transaction that was used to access the given resource.

    :type resource: pymdlsdk.IValue_resource
    :param resource: The MDL resource, i.e., texture, light profile, or measured bsdf.

    :return: The resolved URI of the resource or the empty string in case of the empty resource or one that can not be resolved.
    """
    from ._inspect import get_resource_uri_mask
    return get_resource_uri_mask(transaction, resource)


def get_resource_uri_list(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource, report_missing: bool = False) -> list[str]:
    R"""
    Computes or resolves the URIs for a given resource set.

    :type transaction: pymdlsdk.ITransaction
    :param transaction: The DB transaction that was used to access the given resource.

    :type resource: pymdlsdk.IValue_resource
    :param resource: The MDL resource, i.e., texture, light profile, or measured bsdf.

    :type report_missing: bool
    :param report_missing: If True, resources that can not be resolved are reported with a leading token "[missing]".

    :return: The resolved URI of the resource or the empty string in case of the empty texture.
             For animated or tiled resources the list can contain more than one element.
    """
    from ._inspect import get_resource_uri_mask
    mask: str = get_resource_uri_mask(transaction, resource)
    if mask == "":
        if report_missing:
            file_path: str = resource.get_file_path()
            value: str = resource.get_value()
            return [ f"[missing] file_path='{file_path}' value='{value}'" ]
        else:
            return []
    if "%3C" in mask:  # marker for animated or tiled textures
        ov_neuraylib: NeurayLib = get_neuraylib()
        return ov_neuraylib.ResolveTiledResourceUri(mask)
    else:
        return [ mask ]


def get_module_uris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[str]:
    R"""
    Lists all the MDL modules file URIs that a given set of graph depends on.

    :type transaction: pymdlsdk.ITransaction
    :param transaction: a DB transaction that is able to see the given graph node

    :type graph_node_db_name: str
    :param graph_node_db_name: the DB of the node to traverse

    :return: A list of all module URIs that the given graph node and its children reference.
    """
    unique_results: dict = {}
    from ._inspect import get_graph_nodes, get_graph_modules
    # get all nodes of our material graph
    node_db_names: list[str] = get_graph_nodes(transaction, graph_node_db_name)
    # get all modules our material graph depends on
    modules: list[str] = get_graph_modules(transaction, node_db_names, True)

    for m in modules:
        mod: pymdlsdk.IModule = transaction.access_as(pymdlsdk.IModule, m)
        if mod.is_valid_interface():
            uri: str = mod.get_filename()
            query: int = uri.rfind('?')
            if query > -1:
                uri = uri[:query]  # drop queries for now, not supported
            unique_results[uri] = ""
        mod = None
    return list(unique_results.keys())


def get_graph_resources(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[pymdlsdk.IValue_resource]:
    R"""
    Traverse the material graph to gather all body/default and parameter resources.

    :type transaction: pymdlsdk.ITransaction
    :param transaction: a DB transaction that is able to see the given graph node

    :type graph_node_db_name: str
    :param graph_node_db_name: the DB of the node to traverse

    :return: A list of all resources that the given graph node and its children reference.
    """
    from ._inspect import get_graph_resources
    return get_graph_resources(transaction, graph_node_db_name)


def get_graph_resources_uri_masks(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]:
    R"""
    Traverse the material graph to gather all body/default and parameter resources.

    :type transaction: pymdlsdk.ITransaction
    :param transaction: a DB transaction that is able to see the given graph node

    :type graph_node_db_name: str
    :param graph_node_db_name: the DB of the node to traverse

    :type report_missing: bool
    :param report_missing: If True, resources that can not be resolved are reported with a leading token "[missing]".

    :return: A list of all resource URI masks that the given graph node and its children reference.
             The empty resource or resources that can not be resolved are not reported unless `report_missing` is set.
    """
    resources: list[pymdlsdk.IValue_resource] = get_graph_resources(transaction, graph_node_db_name)
    uniqueUris: dict = {}
    for r in resources:
        uri: str = get_resource_uri_mask(transaction, r)
        if uri and uri != "":
            uniqueUris[uri] = ""
        elif report_missing:
            file_path: str = r.get_file_path()
            value: str = r.get_value()
            uniqueUris[f"[missing] file_path='{file_path}' value='{value}'"] = ""
        r = None
    resources.clear()
    return list(uniqueUris.keys())


def get_graph_resources_uris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]:
    R"""
    Traverse the material graph to gather all body/default and parameter resources.

    :type transaction: pymdlsdk.ITransaction
    :param transaction: a DB transaction that is able to see the given graph node

    :type graph_node_db_name: str
    :param graph_node_db_name: the DB of the node to traverse

    :type report_missing: bool
    :param report_missing: If True, resources that can not be resolved are reported with a leading token "[missing]".

    :return: A list of all resource URIs that the given graph node and its children reference.
    """
    resources: list[pymdlsdk.IValue_resource] = get_graph_resources(transaction, graph_node_db_name)
    uniqueUris: dict = {}
    for r in resources:
        uris: list[str] = get_resource_uri_list(transaction, r, report_missing)
        for u in uris:
            uniqueUris[u] = ""
        r = None
    resources.clear()
    return list(uniqueUris.keys())


def parse_scene_identifier_texture(sceneIdentifierTexture : str) -> tuple[str|None,str|None,float|None]:
    R"""
    Parse the Scene identifier without checking for existance of the resource.
    When texture parameters are overridden in USD we encode their filepaths and color space in an identifier.
    This is parsed by the renderer to load the actualy data.

    The encoding is done in 'rendering/include/rtx/neuraylib/NeurayLibUtils.h'.

    :type sceneIdentifierTexture: str
    :param sceneIdentifierTexture: encoded scene identier.

    :return: A tuple (uri: str, color_space: str, gamma: float) or (None, None, None) if it's not a valid identifier
    """
    from ._scene_identifier import parse_resource_identifier_texture
    return parse_resource_identifier_texture(sceneIdentifierTexture)


def parse_scene_identifier_bsdf_measurement(sceneIdentifierBsdfMeasurement : str)-> str|None:
    R"""
    Parse the Scene identifier without checking for existance of the resource.
    When texture parameters are overridden in USD we encode their filepaths in an identifier.
    This is parsed by the renderer to load the actualy data.

    The encoding is done in 'rendering/include/rtx/neuraylib/NeurayLibUtils.h'.

    :type sceneIdentifierBsdfMeasurement: str
    :param sceneIdentifierBsdfMeasurement: encoded scene identier.

    :return: The resource URI or None if it's not a valid identifier
    """
    from ._scene_identifier import parse_resource_identifier_mbsdf
    return parse_resource_identifier_mbsdf(sceneIdentifierBsdfMeasurement)


def parse_scene_identifier_light_profile(sceneIdentifierLightProfile : str) -> str|None:
    R"""
    Parse the Scene identifier without checking for existance of the resource.
    When texture parameters are overridden in USD we encode their filepaths in an identifier.
    This is parsed by the renderer to load the actualy data.

    The encoding is done in 'rendering/include/rtx/neuraylib/NeurayLibUtils.h'.

    :type sceneIdentifierBsdfMeasurement: str
    :param sceneIdentifierBsdfMeasurement: encoded scene identier.

    :return: The resource URI or None if it's not a valid identifier
    """
    from ._scene_identifier import parse_resource_identifier_lp
    return parse_resource_identifier_lp(sceneIdentifierLightProfile)


@omni.kit.app.deprecated("use create_temporary_db_scope instead")
def CreateTemporaryDbScope(resolveResources: bool) -> str:
    return create_temporary_db_scope(resolveResources)

@omni.kit.app.deprecated("use destroy_temporary_db_scope instead")
def DestroyTemporaryDbScope(scopeName: str) -> bool:
    return destroy_temporary_db_scope(scopeName)

@omni.kit.app.deprecated("use recreate_material_in_scope instead")
def RecreateMaterialInScope(materialRoot: MdlEntitySnapshot, temporaryScopeName: str) -> str:
    return recreate_material_in_scope(materialRoot, temporaryScopeName)

@omni.kit.app.deprecated("use get_resource_uri_mask instead")
def GetResourceUriMask(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource) -> str:
    return get_resource_uri_mask(transaction, resource)

@omni.kit.app.deprecated("use get_resource_uri_list instead")
def GetResourceUriList(transaction: pymdlsdk.ITransaction, resource: pymdlsdk.IValue_resource, report_missing: bool = False) -> list[str]:
    return get_resource_uri_list(transaction, resource, report_missing)

@omni.kit.app.deprecated("use get_module_uris instead")
def GetModuleUris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[str]:
    return get_module_uris(transaction, graph_node_db_name)

@omni.kit.app.deprecated("use get_graph_resources instead")
def GetGraphResources(transaction: pymdlsdk.ITransaction, graph_node_db_name: str) -> list[pymdlsdk.IValue_resource]:
    return get_graph_resources(transaction, graph_node_db_name)

@omni.kit.app.deprecated("use get_graph_resources_uri_masks instead")
def GetGraphResourcesUriMasks(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]:
    return get_graph_resources_uri_masks(transaction, graph_node_db_name, report_missing)

@omni.kit.app.deprecated("use get_graph_resources_uris instead")
def GetGraphResourcesUris(transaction: pymdlsdk.ITransaction, graph_node_db_name: str, report_missing: bool = False) -> list[str]:
    return get_graph_resources_uris(transaction, graph_node_db_name, report_missing)

@omni.kit.app.deprecated("use parse_scene_identifier_texture instead")
def ParseSceneIdentifierTexture(sceneIdentifierTexture : str) -> tuple[str|None,str|None,float|None]:
    return parse_scene_identifier_texture(sceneIdentifierTexture)

@omni.kit.app.deprecated("use parse_scene_identifier_bsdf_measurement instead")
def ParseSceneIdentifierBsdfMeasurement(sceneIdentifierBsdfMeasurement : str) -> str|None:
    return parse_scene_identifier_bsdf_measurement(sceneIdentifierBsdfMeasurement)

@omni.kit.app.deprecated("use parse_scene_identifier_light_profile instead")
def ParseSceneIdentifierLightProfile(sceneIdentifierLightProfile : str) -> str|None:
    return parse_scene_identifier_light_profile(sceneIdentifierLightProfile)
