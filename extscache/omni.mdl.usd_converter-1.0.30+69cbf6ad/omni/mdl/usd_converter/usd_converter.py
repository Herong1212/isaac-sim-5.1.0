# *****************************************************************************
# Copyright 2021 NVIDIA Corporation. All rights reserved.
# *****************************************************************************

import omni.ext
import carb
import os
import shutil
import tempfile
import carb.settings
import carb
import omni.kit.app

from omni.mdl import pymdlsdk
from omni.mdl import pymdl
import omni.mdl.neuraylib
import omni.client
from . import mdl_usd
import asyncio
from pxr import Usd
from pxr import UsdShade

MDL_AUTOGEN_PATH = "${data}/shadergraphs/mdl_usd"

class TemporaryDirectory:
    def __init__(self):
        self.path = None

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, type, value, traceback):
        # Remove temporary data created
        shutil.rmtree(self.path)


def add_search_path_to_system_path(searchPath: str):
    if not searchPath == None and not searchPath == "":
        MDL_SYSTEM_PATH = "/app/mdl/additionalSystemPaths"
        settings = carb.settings.get_settings()
        mdl_custom_paths: List[str] = settings.get(MDL_SYSTEM_PATH) or []
        mdl_custom_paths.append(searchPath)
        mdl_custom_paths = list(set(mdl_custom_paths))
        settings.set_string_array(MDL_SYSTEM_PATH, mdl_custom_paths)


# Is the input material prim bound to a 'imageable' UsdPrim
#
def is_material_bound_to_prim(stage:Usd.Stage, materialPrim:Usd.Prim):
    # Sanity checks
    if not stage:
        carb.log_error('Invalid stage')
        return False
    if not materialPrim:
        carb.log_error('Invalid prim')
        return False
    if not UsdShade.Material(materialPrim):
        carb.log_error(f'Not a material prim {materialPrim}')
        return False
    for prim in stage.Traverse():
        if omni.usd.is_prim_material_supported(prim):
            mat, rel = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            if mat and mat.GetPrim().GetPath() == materialPrim.GetPath():
                return True
    return False


# Check to see if the shaders are all resolved.
# If not, error and inform User which shaders have invalid sourceAsset and subIdentifiers.
#
def is_shader_resolved(stage:Usd.Stage, materialPrim:Usd.Prim):
    status = True
    message = ''

    prim_path = materialPrim.GetPath()
    # Get the shader prim from Material
    shader_prim_path = omni.mdl.usd_converter.mdl_usd.get_shader_prim(stage, prim_path)

    if shader_prim_path is None:
        status = False
        message = f"Can not access prim: '{prim_path}'"
    else:
        ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()
        dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()
        mdl_entity = ovNeurayLib.createMdlEntity(shader_prim_path.GetPath().pathString, dbScopeName)
        source_asset = ''
        sub_id = ''
        mdl_entity_snapshot = None
        module = mdl_entity.getMdlModule()
        if module is None:
            shaderPrim = omni.mdl.usd_converter.mdl_usd.get_shader_prim(stage, prim_path)
            if shaderPrim:
                shader = UsdShade.Shader(shaderPrim)
                imp_source = shader.GetImplementationSourceAttr().Get()
                if imp_source == "sourceAsset":
                    # Retrieve module name
                    source_asset = shader.GetSourceAsset("mdl")
                    sub_id = shaderPrim.GetAttribute("info:mdl:sourceAsset:subIdentifier").Get()

            status = False
            message = f"Can not access entity: '{prim_path}' \nInvalid sourceAsset and/or subIdentifier\n\
sourceAsset: '{source_asset}'\nsubIdentifier: '{sub_id}'"

    if not mdl_entity_snapshot == None:
        ovNeurayLib.destroyMdlEntitySnapshot(mdl_entity_snapshot)
    if not mdl_entity == None:
        ovNeurayLib.destroyMdlEntity(mdl_entity)

    return(status, message)


# Functions and vars are available to other extension as usual in python: `omni.mdl.usd_converter.mdl_to_usd(x)`
#
# mdl_to_usd(moduleName, targetFolder, targetFilename)
#   moduleName: module to convert (example: "nvidia/core_definitions.mdl")
#   searchPath: MDL search path to be able to load MDL modules referenced by moduleName
#   targetFolder: Destination folder for USD stage (default = "${data}/shadergraphs/mdl_usd")
#   targetFilename: Destination stage filename (default is module name, example: "core_definitions.usda")
#   output: What to output:
#       a shader: omni.mdl.usd_converter.mdl_usd.OutputType.SHADER
#       a material: omni.mdl.usd_converter.mdl_usd.OutputType.MATERIAL
#       geometry and material: omni.mdl.usd_converter.mdl_usd.OutputType.MATERIAL_AND_GEOMETRY
#   nestedShaders: Do we want nested shaders or flat (default = False)
#
def mdl_to_usd(
        moduleName: str,
        searchPath: str = None,
        targetFolder: str = MDL_AUTOGEN_PATH,
        targetFilename: str = None,
        output: mdl_usd.OutputType = mdl_usd.OutputType.SHADER,
        nestedShaders: bool = False):
    carb.log_info(f"[omni.mdl.usd_converter] mdl_to_usd was called with {moduleName}")
    # acquire neuray instance from OV
    ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()
    ovNeurayLibHandle = ovNeurayLib.getNeurayAPI()
    # Select a view on the database used for the active renderer.
    # Hydra will deal with applying the changes to the other renderer.
    # It would be possible to use an own space entirely but this would double module loading.
    # In the long, we want to load modules only into one scope.
    dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()
    carb.log_info(f"Active Renderer DB Scope Name: {dbScopeName}")

    # feed the neuray instance into the python binding
    neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ovNeurayLibHandle)
    neurayStatus: pymdlsdk.INeuray.Status = neuray.get_status()
    carb.log_info(f"Neuray Status: {neurayStatus}")

    # Set carb.settings with new MDL search path
    add_search_path_to_system_path(searchPath)

    # we need to load modules to OV using the omni.mdl.neuraylib
    # on the c++ side this is async, here it is blocking!
    carb.log_info(f"createMdlModule called with: {moduleName}")
    ovModule = ovNeurayLib.createMdlModule(moduleName, dbScopeName)
    carb.log_info(f"CoreDefinitions: {ovModule.valid()}")
    if ovModule.valid():
        carb.log_info(f" dbScopeName: {ovModule.dbScopeName}")
        carb.log_info(f" dbName: {ovModule.dbName}")
        carb.log_info(f" qualifiedName: {ovModule.qualifiedName}")
    else:
        carb.log_error(f" createMdlModule failed : {moduleName}")

    # after the module is loaded we create a new transaction that can see the loaded module
    ovTransactionReadHandle = ovNeurayLib.createReadingTransaction(dbScopeName)

    trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ovTransactionReadHandle)
    carb.log_info(f"Transaction Open: {trans.is_open()}")

    # try out the high level binding
    module : pymdl.Module = None
    module = pymdl.Module._fetchFromDb(trans, ovModule.dbName)
    with trans.access_as(pymdlsdk.IModule, ovModule.dbName) as m:
        if m.is_valid_interface():
            carb.log_info("OK")

    if module:
        carb.log_info(f"MDL Qualified Name: {module.mdlName}")
        carb.log_info(f"MDL Simple Name: {module.mdlSimpleName}")
        carb.log_info(f"MDL DB Name: {module.dbName}")
        carb.log_info(f"MDL Module filename: {module.filename}")
    else:
        carb.log_error("MDL Module: None")
        carb.log_error(f"Failed to convert: {moduleName}")
        trans.abort()
        trans = None
        return False

    try:
        stage = mdl_usd.Usd.Stage.CreateInMemory()
    except:
        trans.abort()
        trans = None
        return False

    stage.SetMetadata('comment', 'MDL to USD conversion')

    # create context for the conversion of the scene
    context = mdl_usd.ConverterContext()
    context.set_neuray(neuray)
    context.set_transaction(trans)
    context.set_stage(stage)
    context.mdl_to_usd_output = output
    context.mdl_to_usd_output_material_nested_shaders = nestedShaders
    context.ov_neuray = ovNeurayLib

    mdl_usd.module_to_stage(context, module)
    # Workaround the issue creating stage under "${data}/shadergraphs/mdl_usd"
    # by creating the stage in a temp folder and copying it to dest folder
    with TemporaryDirectory() as temp_dir:
        unmangle_helper = mdl_usd.Unmangle(context)
        # Demangle instance name
        (unmangled_flag, simple_name) = unmangle_helper.unmangle_mdl_identifier(module.dbName)
        simple_name = simple_name.replace(":", "_")
        filename = os.path.join(temp_dir, simple_name + ".usda")
        if targetFilename is not None:
            if targetFilename[-4:] == ".usd" or targetFilename[-5:] == ".usda":
                filename = os.path.join(temp_dir, targetFilename)
            else:
                filename = os.path.join(temp_dir, targetFilename + ".usda")

        try:
            stage.GetRootLayer().Export(filename)
        except:
            carb.log_error(f"Failed to export stage as: {filename}")

        # Copy file to destination folder
        path = targetFolder
        if not omni.client.is_local_url(path):
            # add a trailing slash for the client library
            # Can not use os.sep (at least on Windows) instead of harcoded '/'
            if(path[-1] != '/'):
                path = path + '/'
            targetFilename = omni.client.combine_urls(path, os.path.basename(filename))
            result = omni.client.copy(filename, targetFilename)
            if result == omni.client.Result.OK:
                carb.log_info(f"Stage saved as: {targetFilename}")
            else:
                carb.log_error(f"Failed to save stage")
                carb.log_error(f"Source: {filename}")
                carb.log_error(f"Destination: {targetFilename}")
                carb.log_error(f"Error: {result}")
        else:
            token = carb.tokens.get_tokens_interface()
            mdlUSDPath = token.resolve(path)
            dest = os.path.abspath(mdlUSDPath)
            # Create folder if it does not exist
            if not os.path.exists(dest):
                os.makedirs(dest)
            try:
                shutil.copy2(filename, dest)
                carb.log_info(f"Stage saved as: {os.path.join(dest, os.path.basename(filename))}")
            except:
                carb.log_error(f"Failed to save stage as: {os.path.join(dest, os.path.basename(filename))}")
                pass

    try:
        omni.kit.window.material_graph.GraphExtension.refresh_compounds()
    except:
        pass

    ovNeurayLib.destroyMdlModule(ovModule)

    # since we have been reading only, abort
    trans.abort()
    trans = None

    return True


# Help to delete prim which are dangling in the shader node graph
class CleanupPrimHelper:
    def __list_nodes(self, prim):
        if prim == None:
            return
        self.prims.append(prim)
        properties = prim.GetProperties()
        for prop in properties:
            if isinstance(prop, Usd.Attribute):
                connections = prop.GetConnections()
                for c in connections:
                    parent = c.GetParentPath()
                    p = self.stage.GetPrimAtPath(parent)
                    if p not in self.prims:
                        self.__list_nodes(p)

    def __init__(self, stage, prim):
        try:
            self.stage = stage
            # Need a prim
            self.topprim = prim
            if not isinstance(self.topprim, Usd.Prim):
                self.topprim = prim.GetPrim()
            self.prims = []
            self.__list_nodes(self.topprim)
        except Exception as e:
            carb.log_error(f"CleanupPrimHelper init failed.\n{e}")

    def cleanup(self):
        try:
            # take a new snapshot and only delete the nodes which are not connected to any node
            prim_to_delete = self.prims
            self.prims = []
            self.__list_nodes(self.topprim)
            for prim in prim_to_delete:
                if prim not in self.prims:
                    self.stage.RemovePrim(prim.GetPath())
        except Exception as e:
            carb.log_error(f"CleanupPrimHelper cleanup failed.\n{e}")


def build_shader_node_for_material(prim: mdl_usd.Usd.Prim, merge_identical_subgraphs_after_expand : bool = False):
    if not prim.IsValid():
        carb.log_error(f"Invalid prim")
        return False

    USDmaterial = UsdShade.Material(prim)
    if USDmaterial is None:
        carb.log_error(f"Prim is not a Material")
        return False

    prim_path = prim.GetPath()
    carb.log_info(f"Build shader node for material {prim_path}")

    stage = prim.GetStage()
    shader = UsdShade.Shader(mdl_usd.get_shader_prim(stage, prim_path))
    if shader is None:
        carb.log_error(f"Invalid shader for Prim")
        return False

    cleanup_prim = CleanupPrimHelper(stage, USDmaterial)

    # acquire neuray instance from OV
    ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()
    ovNeurayLibHandle = ovNeurayLib.getNeurayAPI()
    dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()

    # feed the neuray instance into the python binding
    neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ovNeurayLibHandle)

    # after the module is loaded we create a new transaction that can see the loaded module
    ovTransactionReadHandle = ovNeurayLib.createReadingTransaction(dbScopeName)
    trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ovTransactionReadHandle)

    mdl_entity = ovNeurayLib.createMdlEntity(shader.GetPath().pathString, dbScopeName)
    mdl_entity_snapshot = None
    if not mdl_entity.getMdlModule() == None:
        mdl_entity_snapshot = ovNeurayLib.createMdlEntitySnapshot(mdl_entity)
        inst_name = mdl_entity_snapshot.dbName
    else:
        carb.log_error(f"Error: can not access entity: '{prim_path}'")
        return False

    # create context for the conversion of the scene
    context = mdl_usd.ConverterContext()
    context.set_neuray(neuray)
    context.set_transaction(trans)
    context.set_stage(stage)
    context.mdl_to_usd_output = mdl_usd.OutputType.MATERIAL
    context.mdl_to_usd_output_material_nested_shaders = False
    context.ov_neuray = ovNeurayLib

    fctCall = pymdl.FunctionCall._fetchFromDb(trans, inst_name)
    fdef_db_name = fctCall.functionDefinition
    material = pymdl.FunctionDefinition._fetchFromDb(context.transaction, fdef_db_name)
    if not material:
        return False

    module = pymdl.Module._fetchFromDb(context.transaction, material.moduleDbName)
    context.push_module(module)
    context.push_usd_material(USDmaterial)
    rtn = mdl_usd.material_to_stage(context, material)
    context.pop_usd_material()
    context.pop_module()

    if not mdl_entity_snapshot == None:
        context.ov_neuray.destroyMdlEntitySnapshot(mdl_entity_snapshot)
    if not mdl_entity == None:
        context.ov_neuray.destroyMdlEntity(mdl_entity)

    trans.abort()

    if rtn:
        carb.log_info(f"Shader node built with success")
        # Cleanup dangling shaders
        cleanup_prim.cleanup()

        if merge_identical_subgraphs_after_expand == True:
            omni.mdl.usd_converter.merge_identical_subgraphs(stage, prim_path)
    else:
        carb.log_error(f"Failed to build shader nodes")

    return rtn



# usd_to_mdl(path, prim)
#   path: Output file name
#   prim: Prim to convert
#
#   Note: The MDL modules referenced by the prim must be in the MDL searchPath
#
async def usd_to_mdl(path: str, prim: mdl_usd.Usd.Prim, forceNotOV: bool = False):

    if prim == None:
        carb.log_error(f"[omni.mdl.usd_converter] error: No prim specified and no default prim in stage")
        return False

    stage = prim.GetStage()
    if not is_material_bound_to_prim(stage, prim):
        carb.log_error(f"Material is not bound to any prim, export failed")
        return False

    # acquire neuray instance from OV
    ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()

    # Select a view on the database used for the active renderer.
    # Hydra will deal with applying the changes to the other renderer.
    # It would be possible to use an own space entirely but this would double module loading.
    # In the long, we want to load modules only into one scope.
    dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()
    carb.log_info(f"Active Renderer DB Scope Name: {dbScopeName}")

    # feed the neuray instance into the python binding
    ovNeurayLibHandle = ovNeurayLib.getNeurayAPI()
    neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ovNeurayLibHandle)
    neurayStatus: pymdlsdk.INeuray.Status = neuray.get_status()
    carb.log_info(f"Neuray Status: {neurayStatus}")

    # create a new transaction
    ovTransactionReadHandle = ovNeurayLib.createReadingTransaction(dbScopeName)

    trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ovTransactionReadHandle)
    carb.log_info(f"Transaction Open: {trans.is_open()}")

    # create context for the conversion of the scene
    context = mdl_usd.ConverterContext()
    context.set_neuray(neuray)
    context.set_dbScopeName(dbScopeName) # todo, use the same scope for the entire task
    context.set_transaction(trans)
    context.set_stage(stage)
    if not forceNotOV:
        context.ov_neuray = ovNeurayLib

    usd_prim = prim.GetPath()

    inst_name = await mdl_usd.convert_usd_to_mdl(context, usd_prim, path)

    rtncode = (inst_name is not None)

    if rtncode:
        carb.log_info(f"[omni.mdl.usd_converter] Export to MDL success")
    else:
        carb.log_error(f"[omni.mdl.usd_converter] Error: Export to MDL failure")

    context.transaction.abort()

    context.set_transaction(None)

    return rtncode

# expand_mdl_material_parameters(moduleName, stage, materialPrim)
#   moduleName: module to convert (example: "nvidia/core_definitions.mdl")
#   stage: USD stage to write material parameters to
#   materialPrim: Usd prim for material parameters should be written too
async def expand_mdl_material_parameters(moduleName, stage: Usd.Stage, materialPrim: Usd.Prim):
    # Get the shader prim from Material
    material_path = materialPrim.GetPath()
    shader_prim_path = omni.mdl.usd_converter.mdl_usd.get_shader_prim(stage, material_path)
    shader = UsdShade.Shader(shader_prim_path)
    if shader is None:
        carb.log_error(f"Invalid shader for materialPrim")
        return False

    # acquire neuray instance from OV
    ov_neuray_lib = omni.mdl.neuraylib.get_neuraylib()
    ov_neuray_lib_handle = ov_neuray_lib.getNeurayAPI()
    db_scope_name: str = ov_neuray_lib.getCurrentDefaultScope()

    # feed the neuray instance into the python binding
    neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ov_neuray_lib_handle)
    ov_module = ov_neuray_lib.createMdlModule(moduleName, db_scope_name)
    if not ov_module.valid():
        return False

    # after the module is loaded we create a new transaction that can see the loaded module
    ov_transaction_read_handle = ov_neuray_lib.createReadingTransaction(db_scope_name)
    trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_transaction_read_handle)

    # try out the high level binding
    module = pymdl.Module._fetchFromDb(trans, ov_module.dbName)  # noqa PLW0212
    ov_neuray_lib.destroyMdlModule(ov_module)
    if not module:
        return False

    # create context for the conversion of the scene
    context = mdl_usd.ConverterContext()
    context.set_neuray(neuray)
    context.set_transaction(trans)
    context.set_stage(stage)
    context.mdl_to_usd_output = omni.mdl.usd_converter.mdl_usd.OutputType.MATERIAL
    context.mdl_to_usd_output_material_nested_shaders = True
    context.ov_neuray = ov_neuray_lib

    context.push_module(module)

    for _, overloads in module.functions.items():
        f: pymdl.FunctionDefinition
        for f in overloads:
            context.push_custom_data({})
            context.push_usd_material(materialPrim)
            context.push_usd_shader(shader)

            mdl_usd.definition_to_stage(context, f)
            # Annotations
            anno_dict = mdl_usd.get_annotations_dict(context, f)
            mdl_usd.add_annotations_to_prim(shader.GetPrim(), anno_dict)
            mdl_usd.add_annotations_to_node(shader, anno_dict)

            context.pop_custom_data()
            context.pop_usd_shader()
            context.pop_usd_material()

    context.transaction.abort()
    context.set_transaction(None)

    return True

def find_tokens(lines, filter_import_lines = False):
    return mdl_usd.find_tokens(lines, filter_import_lines)


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class DiscoveryExtension(omni.ext.IExt): # pragma: no cover
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        carb.log_info("[omni.mdl.usd_converter] MDL to USD converter startup")

    def on_shutdown(self):
        carb.log_info("[omni.mdl.usd_converter]  MDL to USD converter shutdown")
