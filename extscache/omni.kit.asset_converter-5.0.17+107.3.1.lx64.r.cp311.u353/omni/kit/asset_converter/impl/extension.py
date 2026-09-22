# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import weakref

import omni.ext
import omni.mdl.neuraylib

try:
    import omni.mdl.neuraylib.utils

    ENABLE_NEURAYLIB_UTILS = True
except:
    ENABLE_NEURAYLIB_UTILS = False

from typing import Callable

from ..native_bindings import *
from .context import AssetConverterContext
from .task_manager import AssetConverterTaskManager

__all__ = ["AssetImporterExtension", "get_instance"]


def get_instance():
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()

    return None


class AssetImporterExtension(omni.ext.IExt):
    def on_startup(self):
        global _global_instance
        _global_instance = weakref.ref(self)
        self._manager_startup = False

        self._mdl_modules = dict()
        OmniAssetConverter.set_neuraylib_callback(
            lambda: omni.mdl.neuraylib.get_neuraylib().getNeurayAPI(),
            lambda usd_identifier, db_scope_name: self._create_mdl_module(usd_identifier, db_scope_name),
            lambda db_name: self._destroy_mdl_module(db_name),
            lambda: self._create_temporary_db_scope(),
            lambda db_scope_name: self._destroy_temporary_db_scope(db_scope_name),
            lambda db_scope_name: omni.mdl.neuraylib.get_neuraylib().createReadingTransaction(db_scope_name),
            lambda mdl_module_path, path_separator: omni.mdl.neuraylib.get_neuraylib()._unmangleUri(
                mdl_module_path, path_separator
            ),
            lambda filename_mask: omni.mdl.neuraylib.get_neuraylib().ResolveTiledResourceUri(filename_mask),
        )

    def on_shutdown(self):  # pragma: no cover
        global _global_instance
        _global_instance = None

        # Must clean up neuraylib callback otherwise there will be crash when shutdown
        OmniAssetConverter.set_neuraylib_callback(None, None, None, None, None, None, None, None)

        if self._mdl_modules:
            neuraylib = omni.mdl.neuraylib.get_neuraylib()
            for _, mdl_module in self._mdl_modules:
                neuraylib.destroyMdlModule(mdl_module)
            self._mdl_modules.clear()
        AssetConverterTaskManager.on_shutdown()

    def create_converter_task(
        self,
        import_path: str,
        output_path: str,
        progress_callback: Callable[[int], int] = None,
        asset_converter_context: AssetConverterContext = AssetConverterContext(),
        material_loader=None,
        close_stage_and_reopen_if_opened: bool = False,
    ):
        """
        Creates task to convert import_path to output_path. Currently, it supports
        to convert fbx/obj/glTF to USD, or USD to fbx/obj/glTF.

        Snippet to use it:
        >>> import asyncio
        >>> importer omni.kit.asset_converter as converter
        >>>
        >>> async def convert(...):
        >>>     task_manger = converter.get_instance()
        >>>     task = task_manger.create_converter_task(...)
        >>>     success = await task.wait_until_finished()
        >>>     if not success:
        >>>         detailed_status_code = task.get_status()
        >>>         detailed_status_error_string = task.get_error_message()

        NOTE: It uses FBX SDK for FBX convert and Assimp as fallback backend, so it should support
        all assets that Assimp supports. But only obj/glTF are fully verified.

        Args:
            import_path (str): The source asset to be converted. It could also be stage id that's
                               cached in UsdUtils.StageCache since it supports to export loaded stage.

            output_path (str): The target asset. Asset format is decided by its extension.

            progress_callback(Callable[[int], int]): Progress callback to monitor the progress of
                                                   conversion. The first param is the progress, and
                                                   the second one is the total steps.
            asset_converter_context (omni.kit.asset_converter.AssetConverterContext): Context.

            material_loader (Callable[[omni.kit.asset_conerter.native_bindings.MaterialDescription], None]): You
                                                   can set this to intercept the material loading.

            close_stage_and_reopen_if_opened (bool): If the output path has already been opened in the
                                                     current UsdContext, it will close the current stage, then import
                                                     and re-open it after import successfully if this flag is true. Otherwise,
                                                     it will return False and report errors.
        """
        if not self._manager_startup:
            AssetConverterTaskManager.on_startup()
            self._manager_startup = True
        return AssetConverterTaskManager.create_converter_task(
            import_path,
            output_path,
            progress_callback,
            asset_converter_context,
            material_loader,
            close_stage_and_reopen_if_opened,
        )

    def _create_mdl_module(self, usd_identifier, db_scope_name):
        neuraylib = omni.mdl.neuraylib.get_neuraylib()
        mdl_module = neuraylib.createMdlModule(usd_identifier, db_scope_name)
        self._mdl_modules[mdl_module.dbName] = mdl_module
        return mdl_module.dbName

    def _destroy_mdl_module(self, db_name):  # pragma: no cover
        neuraylib = omni.mdl.neuraylib.get_neuraylib()
        neuraylib.destroyMdlModule(self._mdl_modules[db_name])
        self._mdl_modules.pop(db_name)

    def _create_temporary_db_scope(self):
        if ENABLE_NEURAYLIB_UTILS:
            return omni.mdl.neuraylib.utils.create_temporary_db_scope(resolveResources=False)
        else:
            return omni.mdl.neuraylib.get_neuraylib().getCurrentDefaultScope()

    def _destroy_temporary_db_scope(self, db_scope_name):  # pragma: no cover
        if ENABLE_NEURAYLIB_UTILS:
            return omni.mdl.neuraylib.utils.destroy_temporary_db_scope(db_scope_name)
