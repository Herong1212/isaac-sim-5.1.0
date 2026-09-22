# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import operator
import re
import sys
from collections import OrderedDict
from typing import Any, Dict, List, Optional

import carb
import numpy as np
import omni.client
import omni.client.utils
import omni.kit.app
import omni.mdl.neuraylib as neuraylib
import omni.mdl.pymdl as pymdl
import omni.mdl.pymdlsdk as pymdlsdk
from pxr import Sdf, UsdShade

from .singleton import Singleton

__all__ = [
    "MdlPropertyType",
    "MdlRegistry",
    "MdlShadingNode",
    "MdlShadingNodeProperty",
]


def get_annotation_value(annotation, key, default):
    arg = annotation.arguments.get(key, None)
    if not arg or not isinstance(arg, pymdl.ArgumentConstant):
        return default

    return arg.value


class MdlPropertyType:
    def __init__(self, renderType, usdType):
        # the mdl types are prefixed with '::'
        # e.g. ::base::texture_return or ::material
        # for the "::material" type only, we remove the leading '::'
        self._render = renderType

        if self._render == "::material":
            self._render = "material"

        self._usd = usdType

    @property
    def usd(self):
        return self._usd

    @property
    def render(self):
        return self._render

    @staticmethod
    def mdl_type_to_usd_type(mdlType):
        name = mdlType.name

        if name == "bool":
            return Sdf.ValueTypeNames.Bool

        elif name == "color":
            return Sdf.ValueTypeNames.Color3f

        elif name == "float":
            return Sdf.ValueTypeNames.Float

        elif name == "float2":
            return Sdf.ValueTypeNames.Float2

        elif name == "float3":
            return Sdf.ValueTypeNames.Float3

        elif name == "float4":
            return Sdf.ValueTypeNames.Float4

        elif (name == "int") or (mdlType.kind == pymdlsdk.IType.Kind.TK_ENUM):
            return Sdf.ValueTypeNames.Int

        elif name == "int2":
            return Sdf.ValueTypeNames.Int2

        elif name == "int3":
            return Sdf.ValueTypeNames.Int3

        elif name == "int4":
            return Sdf.ValueTypeNames.Int4

        elif name == "string":
            return Sdf.ValueTypeNames.String

        elif name == "texture_2d":
            return Sdf.ValueTypeNames.Asset

        return Sdf.ValueTypeNames.Token


class MdlShadingNodeProperty:
    def __init__(self, name, parameter: dict):
        self._name = name

        usdType = MdlPropertyType.mdl_type_to_usd_type(parameter.type)
        self._type = MdlPropertyType(parameter.type.name, usdType)

        self._label = None
        self._description = None
        self._page = None
        self._uiOrder = sys.maxsize
        self._customData = {}

        for annotation in parameter.annotations:
            simpleName = annotation.simpleName

            if simpleName == "ui_order":
                self._uiOrder = get_annotation_value(annotation, "order", self._uiOrder)

            elif simpleName == "description":
                self._description = get_annotation_value(annotation, "description", self._description)

            elif simpleName == "display_name":
                self._label = get_annotation_value(annotation, "name", self._label)

            elif simpleName == "in_group":
                self._page = get_annotation_value(annotation, "group", self._page)

            elif simpleName == "hard_range":
                arguments = annotation.arguments
                if len(arguments) == 2:
                    min = arguments.get("min", None)
                    max = arguments.get("max", None)

                    if (min is not None) and (max is not None):
                        if isinstance(min.value, (np.ndarray)):
                            min.value = min.value.flatten().tolist()

                        if isinstance(max.value, (np.ndarray)):
                            max.value = max.value.flatten().tolist()

                        self._customData["range"] = {"min": min.value, "max": max.value}

        self._defaultValue = parameter.value
        if (self._defaultValue is not None) and (not isinstance(self._defaultValue, str)):
            if self._type.render == "float":
                self._defaultValue = float(self._defaultValue)

            elif self._type.render == "int":
                self._defaultValue = int(self._defaultValue)

            elif self._type.render == "float2":
                self.default = (float(self._defaultValue[0]), float(self._defaultValue[1]))

            elif self._type.render in ["color", "float3"]:
                self._defaultValue = (
                    float(self._defaultValue[0]),
                    float(self._defaultValue[1]),
                    float(self._defaultValue[2]),
                )

        self._colorSpace = None
        if self._type.render == "texture_2d":
            self._colorSpace = "sRGB"

        self._sdrMetaData = {}

        # Enums
        if parameter.type.enumValues:
            options_str = []
            for name, value in parameter.type.enumValues:
                options_str.append(name + ":" + str(value))

            self._sdrMetaData["options"] = "|".join(options_str)

            if self._defaultValue:
                self._sdrMetaData["__SDR__enum_value"] = self._defaultValue[0].split(":")[-1]
                self._defaultValue = self._defaultValue[1]

    @property
    def customData(self):
        return self._customData

    @property
    def colorSpace(self):
        return self._colorSpace

    @property
    def sdrMetaData(self):
        return self._sdrMetaData

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def label(self):
        return self._label

    @property
    def description(self) -> str:
        return self._description

    @property
    def page(self) -> str:
        return self._page

    @property
    def defaultValue(self):
        return self._defaultValue

    @property
    def uiOrder(self):
        return self._uiOrder


class MdlShadingNode:
    def __init__(self, mdl_func, sourceAsset, subIdentifier, is_overloaded, isUserModule, overrideCategory: str = ""):
        ADVANCED_TYPES = ["::base::texture_return"]

        self._subIdentifier = subIdentifier
        self._sourceAsset = sourceAsset

        self._name = mdl_func.mdlSimpleName

        usdType = MdlPropertyType.mdl_type_to_usd_type(mdl_func.returnValue.type)
        self._outputs = {"out": MdlPropertyType(mdl_func.returnValue.type.name, usdType)}
        outRenderType = self._outputs["out"].render

        self._uiOrder = sys.maxsize
        self._tags = None
        self._description = ""
        self._displayName = self._name
        self._category = None

        for annotation in mdl_func.annotations:
            simpleName = annotation.simpleName

            if simpleName == "ui_order":
                self._uiOrder = get_annotation_value(annotation, "order", self._uiOrder)

            elif simpleName == "key_words":
                self._tags = get_annotation_value(annotation, "words", self._uiOrder)

            elif simpleName == "description":
                self._description = get_annotation_value(annotation, "description", self._description)

            elif simpleName == "display_name":
                self._displayName = get_annotation_value(annotation, "name", self._displayName)

            elif simpleName == "in_group":
                self._category = get_annotation_value(annotation, "group", self._category)

        if is_overloaded:
            self._displayName += f" {outRenderType}"

        if outRenderType in ADVANCED_TYPES and not isUserModule:
            self._category = "Advanced"

        # hack for OmniPBR
        if self._category == "Base":
            self._category = "Materials"

        module_name = neuraylib.get_neuraylib()._unmangleMdlModulePath(mdl_func.mdlModuleName)

        if not self._category:
            if mdl_func.isMaterial:
                self._category = "Materials"
            else:
                qualified_module_name = module_name.split("/")[-1]

                if qualified_module_name.endswith(".mdl"):
                    qualified_module_name = qualified_module_name.split(".")[0]

                self._category = qualified_module_name

        # special case for data_lookup functions
        # this can be removed once the data_lookup const string issue has been fixed
        if "support_definitions" in module_name and self._name.startswith("data_lookup"):
            self._category = "Constants, State and Primvars"
            self._description = "Returns scene specific data."
            self._displayName = "Primvar lookup, " + outRenderType

        self._parameters = []
        for parameter_name, parameter in mdl_func.parameters.items():
            self._parameters.append(MdlShadingNodeProperty(parameter_name, parameter))

        self._parameters = list(sorted(self._parameters, key=lambda k: k.uiOrder))

        if overrideCategory:
            self._category = overrideCategory

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return self._parameters

    @property
    def category(self):
        return self._category

    @property
    def description(self):
        return self._description

    @property
    def sourceAsset(self):
        return self._sourceAsset

    @property
    def subIdentifier(self):
        return self._subIdentifier

    @property
    def uiOrder(self):
        return self._uiOrder

    @property
    def tags(self):
        return self._tags

    @property
    def outputs(self):
        return self._outputs

    @property
    def displayName(self):
        return self._displayName

    @property
    def thumbnail(self):
        return None

    def __str__(self):
        return f"@{self._sourceAsset}@ {self._subIdentifier} [{self._category}]"


@Singleton
class MdlRegistry:

    def __init__(self):
        self._modules = {}
        self._reload_callbacks = set()
        self._registered_nodes = {}

    def register_reload_callback(self, cb):
        self._reload_callbacks.add(cb)

    def deregister_reload_callback(self, cb):
        self._reload_callbacks.remove(cb)

    @property
    def nodes(self):
        nodes = []
        for moduleDict in self._modules.values():
            nodes.extend(list(moduleDict.values()))
        return nodes

    @property
    def context(self):
        return "mdl"

    def get_node_by_asset_and_id(self, source_asset, subIdentifier):
        module = self._modules.get(source_asset, None)
        if not module:
            return None
        return module.get(subIdentifier, None)

    def register_node_by_asset_and_id(self, sourceAsset: str, subIdentifier: str, category: str = "") -> bool:
        """Add a node to the material graph node list."""
        key: tuple[str, str] = (sourceAsset, subIdentifier)
        if key in self._registered_nodes:
            return False
        self._registered_nodes[key] = {"category": category}
        return True

    def deregister_node_by_asset_and_id(self, sourceAsset: str, subIdentifier: str) -> bool:
        """Remove a node from the material graph node list."""
        key: tuple[str, str] = (sourceAsset, subIdentifier)
        if not key in self._registered_nodes:
            return False
        self._registered_nodes.pop(key)
        return True

    def register_node_by_sdr_info(self, sdr_info, category: str = "") -> bool:
        """Add a node to the material graph node list."""
        import omni.UsdMdl as UsdMdl

        sdr_info: UsdMdl.OmniSdrShaderNode = sdr_info
        source_asset_path: Sdf.AssetPath = sdr_info.GetAssetPath()
        return self.register_node_by_asset_and_id(source_asset_path.path, sdr_info.GetSubIdentifier(), category)

    def deregister_node_by_sdr_info(self, sdr_info) -> bool:
        """Remove a node from the material graph node list."""
        import omni.UsdMdl as UsdMdl

        sdr_info: UsdMdl.OmniSdrShaderNode = sdr_info
        source_asset_path: Sdf.AssetPath = sdr_info.GetAssetPath()
        return self.deregister_node_by_asset_and_id(source_asset_path.path, sdr_info.GetSubIdentifier())

    async def reload(self):
        def gather_search_paths():
            nonlocal search_paths
            nonlocal modules_to_allow
            nonlocal modules_to_block
            nonlocal user_search_paths
            nonlocal user_modules_to_allow
            nonlocal user_modules_to_block

            carb_settings = carb.settings.get_settings()

            materialConfig = carb_settings.get("/materialConfig")
            if not materialConfig:
                materialConfig = {}

            materialGraphConfig = materialConfig.get("materialGraph", {})

            neuray = pymdlsdk.attach_ineuray(neuraylib.get_neuraylib().getNeurayAPI())
            config_api = neuray.get_api_component(pymdlsdk.IMdl_configuration)

            for i in range(0, config_api.get_mdl_paths_length()):
                path = config_api.get_mdl_path(i).get_c_str()
                if path:
                    url = omni.client.utils.make_file_url_if_possible(path)
                    url = omni.client.normalize_url(url)
                    search_paths.append(url.rstrip("/"))

            for i in range(0, config_api.get_mdl_user_paths_length()):
                path = config_api.get_mdl_user_path(i)
                if path:
                    url = omni.client.utils.make_file_url_if_possible(path)
                    url = omni.client.normalize_url(url)
                    user_search_paths.append(url.rstrip("/"))

            custom_paths = materialConfig.get("searchPaths", {}).get("custom", [])

            if not custom_paths:  # for backward compatibility
                custom_paths = materialConfig.get("searchPaths", {}).get("local", [])

            for custom_path in custom_paths:
                path = custom_path.strip()
                if path:
                    url = omni.client.utils.make_file_url_if_possible(path)
                    url = omni.client.normalize_url(url)
                    user_search_paths.append(url.rstrip("/"))

            # remove user paths from built-in paths
            for user_path in user_search_paths:
                for search_path in search_paths:
                    if omni.client.utils.equal_urls(user_path, search_path):
                        search_paths.remove(search_path)
                        break

            if search_paths:
                modules_to_allow = {
                    "aux_definitions",
                    "core_definitions",
                    "support_definitions",
                    "OmniHair.mdl",
                    "OmniHairBase",
                    "OmniPBR.mdl",
                    "OmniPBRBase",
                    "OmniSurface.mdl",
                    "OmniSurfaceBase",
                    "OmniSurfaceBlend.mdl",
                    "OmniSurfaceBlendBase",
                    "OmniSurfaceLite.mdl",
                    "OmniSurfaceLiteBase",
                    "color_correct",
                    "random_value",
                }

                allow_list = materialGraphConfig.get("builtInAllowList", None)
                if allow_list:
                    modules_to_allow = set(allow_list)

                block_list = materialGraphConfig.get("builtInBlockList", None)
                if block_list:
                    modules_to_block = set(block_list)

            if user_search_paths:
                allow_list = materialGraphConfig.get("userAllowList", None)
                if allow_list:
                    user_modules_to_allow = set(allow_list)
                    # if the user has set the allow list, clear user_modules_to_block
                    # as it has been initialized above to block all user modules by default.
                    user_modules_to_block = ()

                block_list = materialGraphConfig.get("userBlockList", None)
                if block_list:
                    user_modules_to_block = set(block_list)

        async def get_modules_in_path(path, modules, prefix=""):
            (result, entries) = await omni.client.list_async(path)
            if result != omni.client.Result.OK:
                return

            files = [
                e.relative_path
                for e in entries
                if (not e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) and e.relative_path.endswith(".mdl")
            ]
            for file in files:
                url = omni.client.utils.make_file_url_if_possible(path + "/" + file)
                url = omni.client.normalize_url(url)
                if url not in modules:
                    modules[url] = prefix + file

            folders = [e.relative_path for e in entries if e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN]

            for folder in folders:
                url = omni.client.utils.make_file_url_if_possible(path + "/" + folder)
                url = omni.client.normalize_url(url)
                await get_modules_in_path(url, modules, prefix + folder + "/")

        async def find_modules(search_paths, modulues_to_allow, modules_to_block):
            def build_re_list(modules):
                if not modules:
                    return []

                regexes = []

                for i in modules:
                    try:
                        regexes.append(re.compile(i))
                    except Exception as e:
                        carb.log_warn(
                            f"{i} in MDL module [allow|block]_list is an invalid regex and will be ignored: {str(e)}"
                        )

                return regexes

            modules = OrderedDict()
            modules_to_load = []

            for path in search_paths:
                await get_modules_in_path(path, modules)

            if modules:
                allow = build_re_list(modulues_to_allow)
                block = build_re_list(modules_to_block)

                for name in modules.values():
                    module_name = name.split("/")[-1]

                    if allow and not any(regex.match(module_name) for regex in allow):
                        continue

                    if block and any(regex.match(module_name) for regex in block):
                        continue

                    modules_to_load.append(name)

            return modules_to_load

        async def load_mdl_function(
            module_name: str, func, is_overloaded, isUserModule, attributes: dict[str, str] = {}
        ):
            app = omni.kit.app.acquire_app_interface()

            if float(app.get_kit_version_short()) > 104:
                unknown = pymdlsdk.IFunction_definition.Semantics.DS_UNKNOWN
            else:
                unknown = 0

            # only load the built-in data_lookup functions
            if (func.semantics != unknown) and (not func.mdlSimpleName.startswith("data_lookup")):
                return

            # don't load hidden functions or functions that have been deprecated
            for annotation in func.annotations:
                simpleName = annotation.simpleName

                if simpleName == "hidden":
                    return

                if simpleName == "display_name":
                    name = get_annotation_value(annotation, "name", "")
                    if "deprecated" in name:
                        return

            mdl_name = func.mdlName

            subIdentifier = func.mdlSimpleName

            # e.g. add(int,int)
            if is_overloaded:
                subIdentifier += mdl_name[mdl_name.rfind("(") :]

            if not module_name in self._modules:
                self._modules[module_name] = {}

            category: str = attributes["category"] if "category" in attributes else ""
            self._modules[module_name][subIdentifier] = MdlShadingNode(
                func, module_name, subIdentifier, is_overloaded, isUserModule, category
            )

        self._modules = {}
        search_paths = []
        modules_to_allow = set()
        modules_to_block = set()

        user_search_paths = []
        user_modules_to_allow = set()
        # by default all modules in MDL_USER_PATH are blocked from being loaded.
        user_modules_to_block = {".*"}

        gather_search_paths()

        if not search_paths and not user_search_paths:
            carb.log_warn("The MDL search paths are empty, no modules will be loaded into the material-graph")
            return

        modules = []
        if search_paths:
            found_modules = await find_modules(search_paths, modules_to_allow, modules_to_block)
            for module in found_modules:
                modules.append((module, False))

        if user_search_paths:
            found_modules = await find_modules(user_search_paths, user_modules_to_allow, user_modules_to_block)
            for module in found_modules:
                modules.append((module, True))

        if not modules:
            carb.log_warn(
                "No MDL modules can be located in the specified search paths, no modules will be loaded into the material-graph"
            )
            return

        # load all nodes
        mdl_functions = {}
        neuray_lib = neuraylib.get_neuraylib()

        # iterate over found modules, loading only those that have been white listed
        for module_name, isUserModule in modules:
            mdl_module = neuray_lib.createMdlModule(module_name)
            if not mdl_module:
                carb.log_warn(f"Neuray could not create MDL module: {module_name}")
                continue

            transaction_handle = neuray_lib.createReadingTransaction()
            transaction = pymdlsdk.attach_itransaction(transaction_handle)

            module = pymdl.Module._fetchFromDb(transaction, mdl_module.dbName)
            neuray_lib.destroyMdlModule(mdl_module)
            transaction.abort()

            if not module:
                carb.log_warn(f"Pymdl could not fetch module: {module_name} from database")
                continue

            for mdlSimpleName, mdlFuncsList in module.functions.items():

                if not mdlSimpleName in mdl_functions:
                    mdl_functions[mdlSimpleName] = []

                for mdlFunc in mdlFuncsList:
                    mdl_functions[mdlSimpleName].append((module_name, mdlFunc, isUserModule))

        for mdlSimpleName, mdlFuncsList in mdl_functions.items():
            is_overloaded = len(mdlFuncsList) > 1

            for module_name, func, isUserModule in mdlFuncsList:
                if func.isExported:
                    await load_mdl_function(module_name, func, is_overloaded, isUserModule)

        # load the nodes registered using source_asset and sub-identifier
        db_scope: str = neuray_lib.getCurrentDefaultScope()
        for node_key, node_attributes in self._registered_nodes.items():
            # load the module using the USD source asset name
            mdl_module = neuray_lib.createMdlModule(node_key[0], db_scope)
            if not mdl_module:
                carb.log_warn(f"Neuray could not create MDL module: {node_key[0]}")
                continue

            # fetch the module
            transaction = pymdlsdk.attach_itransaction(neuray_lib.createReadingTransaction(db_scope))
            module = pymdl.Module._fetchFromDb(transaction, mdl_module.dbName)
            neuray_lib.destroyMdlModule(mdl_module)
            transaction.abort()

            if not module:
                carb.log_warn(f"Neuray could access MDL module: {node_key[0]}")
                continue

            node_simple_name = node_key[1]
            if "(" in node_key[1]:
                node_simple_name = node_key[1].split("(")[0]

            if not node_simple_name in module.functions.keys():
                carb.log_warn(f"MDL Module '{node_key[0]}' does not contain a function '{node_key[1]}'")
                continue

            overloads: list[pymdl.FunctionDefinition] = module.functions[node_simple_name]
            is_overloaded = len(overloads) > 1
            for func in overloads:
                if func.isExported:
                    await load_mdl_function(node_key[0], func, is_overloaded, True, node_attributes)

        for callback in self._reload_callbacks:
            callback()

    @staticmethod
    def createPropertyType(renderType, usdType):
        return MdlPropertyType(renderType, usdType)
