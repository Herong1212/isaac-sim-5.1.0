# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TestCollect"]

import os
import asyncio
import sys
import carb
import random
import omni.kit.app
import omni.kit.test
import omni.usd
import omni.client
import omni.client.utils as clientutils

from pathlib import Path
from unittest.mock import patch
from ..collector import (
    Collector,
    CollectorException,
    CollectorFailureOptions,
    FlatCollectionTextureOptions,
    DefaultPrimOnlyOptions,
    COLLECT_MAPPING_FILE_NAME,
    CollectorStatus
)
from ..utils import Utils
from pxr import Usd, Sdf, UsdUtils


def _mock_copy_access_denied(source_url, target_url, behavior, **kwargs):
    return omni.client.Result.ERROR_ACCESS_DENIED

class TestCollect(omni.kit.test.AsyncTestCase):
    def list_folder(self, folder_path):
        all_file_names = []
        all_file_paths = []
        result, entry = omni.client.stat(folder_path)
        if result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
            is_folder = True
        else:
            is_folder = False

        if not is_folder:
            all_file_names = [os.path.basename(folder_path)]
        else:
            folder_queue = [folder_path]
            while len(folder_queue) > 0:
                folder = folder_queue.pop(0)
                (result, entries) = omni.client.list(folder)
                if result != omni.client.Result.OK:
                    break
                folders = set((e.relative_path for e in entries if e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN))
                for f in folders:
                    folder_queue.append(f"{folder}/{f}")
                files = set((e.relative_path for e in entries if not e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN))
                for file_path in files:
                    all_file_names.append(os.path.basename(file_path))
                    all_file_paths.append(clientutils.make_absolute_url_if_possible(f"{folder}/", file_path))

        return all_file_names, all_file_paths

    def get_test_dir(self):
        token = carb.tokens.get_tokens_interface()
        data_dir = token.resolve("${data}")
        if not data_dir.endswith("/"):
            data_dir += "/"

        data_dir = Utils.normalize_path(data_dir)

        return f"{data_dir}collect_tool_tests"

    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()
        await omni.client.delete_async(self.get_test_dir())
        omni.client.set_retries(*self.previous_retry_values)

    @staticmethod
    def __get_test_dir():
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        extension_path = Path(extension_path)
        return extension_path.joinpath("data")

    async def __test_internal(
        self,
        stage_name,
        root_usd,
        usd_only,
        material_only,
        flat_collection,
        texture_option=FlatCollectionTextureOptions.FLAT,
        exclusion_rules={},
        default_prim_only=False,
        anonymous_root=False,
        default_prim_option=DefaultPrimOnlyOptions.ROOT_LAYER_ONLY,
        convert_usda_to_usdc=False,
        with_reference=False
    ):
        test_data_path = self.__get_test_dir()
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath(stage_name))
        test_root_usd = test_stage_dir + "/" + root_usd
        collected_stage_dir = self.get_test_dir() + f"/collected_{stage_name}/"

        if anonymous_root:
            stage = omni.usd.get_context().get_stage()
            prim = stage.DefinePrim("/root", "Xform")
            prim.GetReferences().AddReference(test_root_usd)
            test_root_usd = stage.GetRootLayer().identifier
            stage = None

        collector = Collector(
            test_root_usd, collected_stage_dir, usd_only, flat_collection,
            material_only, texture_option=texture_option,
            exclusion_rules=exclusion_rules, default_prim_only=default_prim_only,
            default_prim_option=default_prim_option,
            convert_usda_to_usdc=convert_usda_to_usdc
        )
        self.assertEqual(collector.source_stage_url, clientutils.normalize_url(test_root_usd))
        self.assertEqual(collector.target_folder, clientutils.normalize_url(collected_stage_dir))
        self.assertEqual(collector.get_status(), CollectorStatus.NOT_STARTED)
        # Cannot cancel it as it's not started.
        collector.cancel()
        self.assertEqual(collector.get_status(), CollectorStatus.NOT_STARTED)

        # Test status change and task cancel and restart.
        future = asyncio.ensure_future(collector.collect(None, None))
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(collector.get_status(), CollectorStatus.IN_PROGRESS)
        collector.cancel()
        self.assertEqual(collector.get_status(), CollectorStatus.CANCELLED)
        await asyncio.wait([future])
        # It still keeps cancel status even after the job is done.
        self.assertEqual(collector.get_status(), CollectorStatus.CANCELLED)

        success, root_usd = await collector.collect(None, None)
        self.assertEqual(collector.get_status(), CollectorStatus.FINISHED)
        self.assertTrue(success)
        if material_only:
            self.assertIsNone(root_usd)
        else:
            root_usd = clientutils.normalize_url(root_usd)
            expected_root = clientutils.make_absolute_url_if_possible(collected_stage_dir, root_usd)
            self.assertEqual(root_usd, expected_root)

        _, before = self.list_folder(test_stage_dir)
        _, after = self.list_folder(collected_stage_dir)
        self.assertTrue(len(after) > 0)

        if usd_only:
            before_filtered = []
            for f in before:
                if omni.usd.is_usd_writable_filetype(f):
                    before_filtered.append(f)
            before = before_filtered

        if material_only:
            before_filtered = []
            for f in before:
                if not omni.usd.is_usd_writable_filetype(f):
                    before_filtered.append(f)
            before = before_filtered

        # for this test file, it should only collect the usd file
        # when default prim only is true
        if default_prim_only:
            before_filtered = []
            for f in before:
                if omni.usd.is_usd_writable_filetype(f):
                    before_filtered.append(f)

            before = before_filtered

            if default_prim_option == DefaultPrimOnlyOptions.ALL_LAYERS:
                for file_path in after:
                    if omni.usd.is_usd_writable_filetype(file_path):
                        layer = Sdf.Layer.FindOrOpen(file_path)
                        self.assertTrue(len(layer.rootPrims) == 1)
                        self.assertTrue(layer.rootPrims[layer.defaultPrim])
                        layer = None

        if exclusion_rules:
            before_filtered = []
            for file_path in before:
                path = clientutils.make_file_url_if_possible(file_path)
                excluded = False
                for key, _ in exclusion_rules.items():
                    key = clientutils.make_file_url_if_possible(key)
                    if path.startswith(key):
                        excluded = True
                        break

                if not excluded:
                    before_filtered.append(file_path)

            before = before_filtered

        if convert_usda_to_usdc:
            for file_path in after:
                if omni.usd.is_usd_writable_filetype(file_path):
                    layer = Sdf.Layer.FindOrOpen(file_path)
                    file_format = Usd.UsdFileFormat.GetUnderlyingFormatForLayer(layer)
                    self.assertEqual(file_format, "usdc")

                    _, ext = os.path.splitext(file_path)
                    self.assertEqual(ext, ".usd")

                    layer = None

        self.assertTrue(collector.collect_mapping_file_url in after)
        after.remove(collector.collect_mapping_file_url)

        if anonymous_root:
            self.assertTrue(root_usd in after)
            after.remove(root_usd)

        if not with_reference:
            self.assertEqual(len(before), len(after))
        for file_path in before:
            target_path = collector.get_target_url(file_path)
            self.assertTrue(target_path in after, file_path)

        source_target_mapping = collector.get_source_target_url_mapping()
        for file_path in before:
            self.assertTrue(file_path in source_target_mapping)

        return root_usd, before, after, collector

    async def test_collect_with_cache(self):
        _, before, _, collector = await self.__test_internal("normal", "FullScene.usd", False, False, False)
        for file_path in before:
            self.assertFalse(collector.is_copy_skipped(file_path))

        # Files are cached already
        _, before, after, collector = await self.__test_internal("normal", "FullScene.usd", False, False, False)
        for file_path in before:
            self.assertTrue(collector.is_copy_skipped(file_path))

        # Change target files to ensure modification to files will trigger re-collect.
        def modify_files(file_paths):
            files_to_modify = random.sample(range(0, len(file_paths)), min(len(file_paths), 5))
            modified_files = []
            for index in files_to_modify:
                path = file_paths[index]
                _, ext = os.path.splitext(path)
                modified_files.append(path)

                # Modify file to refresh its modified time or size.
                if ext in [".usd", "usda", ".usdc"]:
                    layer = Sdf.Layer.FindOrOpen(path)
                    Sdf.CreatePrimInLayer(layer, "/__test__")
                    layer.Save()
                    layer = None
                else:
                    with open(path, "w") as f:
                        f.write("invalid_content")

            return modified_files

        modified_files = modify_files(after)

        # Collect it again. Those modified files should be re-collected again.
        _, before, after, collector = await self.__test_internal("normal", "FullScene.usd", False, False, False)
        for file_path in before:
            target_path = collector.get_target_url(file_path)
            if target_path in modified_files:
                self.assertFalse(collector.is_copy_skipped(file_path), file_path)
            else:
                self.assertTrue(collector.is_copy_skipped(file_path), file_path)

        # Re-collect all files again to see if they all cached.
        _, before, after, collector = await self.__test_internal("normal", "FullScene.usd", False, False, False)
        for file_path in before:
            self.assertTrue(collector.is_copy_skipped(file_path))

        # Remove them will re-collect those files again
        for file_path in modified_files:
            await omni.client.delete_async(file_path)

        root_usd, before, after, collector = await self.__test_internal("normal", "FullScene.usd", False, False, False)
        for file_path in before:
            target_path = collector.get_target_url(file_path)
            if target_path in modified_files:
                self.assertFalse(collector.is_copy_skipped(file_path), file_path)
            else:
                self.assertTrue(collector.is_copy_skipped(file_path), file_path)

        # Test modifications to source files to ensure it will trigger re-collect to source files.
        target_folder = omni.client.combine_urls(root_usd, "collected_temp_folder/")
        collector = Collector(root_usd, target_folder)
        success, _ = await collector.collect()
        self.assertTrue(success)

        # Change source files to ensure modification to files will trigger re-collect.
        modified_files = modify_files(after)
        collector = Collector(root_usd, target_folder)
        success, _ = await collector.collect()
        self.assertTrue(success)
        for file_path in after:
            if file_path in modified_files:
                self.assertFalse(collector.is_copy_skipped(file_path), file_path)

    async def test_collect_with_bsdf_measurements(self):
        await self.__test_internal("bsdf_measurements", "scene.usda", False, False, False)

    async def test_collect_with_usd_and_material(self):
        await self.__test_internal("normal", "FullScene.usd", False, False, False)

    async def test_collect_with_anonymous_root(self):
        await self.__test_internal("normal", "FullScene.usd", False, False, False, anonymous_root=True)

    async def test_collect_with_udim_textures(self):
        await self.__test_internal("udim", "SM_Hood_A1_1.usd", False, False, False)
        await self.__test_internal("udim_in_mdl", "main.usd", False, False, False)

    async def test_collect_without_material(self):
        await self.__test_internal("normal", "FullScene.usd", False, True, False)

    async def test_collect_without_usd(self):
        await self.__test_internal("normal", "FullScene.usd", True, False, False)

    async def test_collect_with_default_prim_only(self):
        await self.__test_internal("default_prim", "has_enviroment.usd", False, False, False, default_prim_only=True)

    async def test_collect_with_default_prim_only_for_all_layers(self):
        await self.__test_internal(
            "default_prim", "has_enviroment.usd", False, False, False, default_prim_only=True,
            default_prim_option=DefaultPrimOnlyOptions.ALL_LAYERS
        )

    async def test_collect_with_usda_to_usdc(self):
        await self.__test_internal(
            "usda_to_usdc", "main.usda", False,
            False, False, default_prim_only=False,
            convert_usda_to_usdc=True
        )

    async def test_collect_without_default_prim_only(self):
        await self.__test_internal("default_prim", "has_enviroment.usd", False, False, False, default_prim_only=False)

    async def test_flatten_collection(self):
        await self.__test_internal("normal", "FullScene.usd", False, False, True)
        await self.__test_internal("layer_offsets", "root.usd", False, False, True)

    async def test_flatten_collection_texture_options(self):
        stage_name = "texture_options"
        texture_dir = self.get_test_dir() + f"/collected_{stage_name}/SubUSDs/textures/"
        mdl_name = "Contour1_Surface_0"
        mdl_texture_name = "Contour1_Surface_1.bmp"
        usd_preview_texture_name = "another_texture.bmp"

        # test group textures by MDL
        await self.__test_internal(
            stage_name, "test_scene.usd", False, False, True, texture_option=FlatCollectionTextureOptions.BY_MDL
        )
        # mdl texture should be under the mdl named folder, while the usd preview texture should be directly under
        #  textures dir
        self.assertTrue(os.path.exists(os.path.join(texture_dir, mdl_name, mdl_texture_name)))
        self.assertTrue(os.path.exists(os.path.join(texture_dir, usd_preview_texture_name)))
        await omni.client.delete_async(self.get_test_dir())

        # test group textures by USD
        await self.__test_internal(
            stage_name, "test_scene.usd", False, False, True, texture_option=FlatCollectionTextureOptions.BY_USD
        )
        # usd preview texture should be under the usd asset named folder, while the mdl texture should be directly under
        #  textures dir
        self.assertTrue(os.path.exists(os.path.join(texture_dir, "assetB", usd_preview_texture_name)))
        self.assertTrue(os.path.exists(os.path.join(texture_dir, mdl_texture_name)))
        await omni.client.delete_async(self.get_test_dir())

        # test flat
        await self.__test_internal(
            stage_name, "test_scene.usd", False, False, True, texture_option=FlatCollectionTextureOptions.FLAT
        )
        # all textures should be directly under textures dir
        self.assertEqual(set([mdl_texture_name, usd_preview_texture_name]), set(os.listdir(texture_dir)))

    async def test_layer_offsets_collect(self):
        current_path = Path(__file__).parent
        test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath("layer_offsets"))
        test_root_usd = test_stage_dir + "/root.usd"
        collected_stage_dir = self.get_test_dir() + f"/collected_layer_offfsets"
        collector = Collector(test_root_usd, collected_stage_dir, False, False, False)
        await collector.collect(None, None)

        before, _ = self.list_folder(test_stage_dir)
        after, _ = self.list_folder(collected_stage_dir)
        self.assertTrue(COLLECT_MAPPING_FILE_NAME in after)
        after.remove(COLLECT_MAPPING_FILE_NAME)
        self.assertEqual(set(before), set(after))

        after_stage_usd = collected_stage_dir + "/root.usd"
        before_stage = Usd.Stage.Open(test_root_usd)
        after_stage = Usd.Stage.Open(after_stage_usd)
        before_root = before_stage.GetRootLayer()
        after_root = after_stage.GetRootLayer()
        before_sublayers = before_root.subLayerPaths
        after_sublayers = after_root.subLayerPaths
        self.assertTrue(len(before_sublayers) > 0)
        self.assertEqual(len(before_sublayers), len(after_sublayers))
        self.assertEqual(len(before_sublayers), len(after_sublayers))

        for i in range(len(before_sublayers)):
            before_sublayer = before_root.ComputeAbsolutePath(before_sublayers[i])
            after_sublayer = after_root.ComputeAbsolutePath(after_sublayers[i])
            self.assertNotEqual(before_sublayer, after_sublayer)

        self.assertEqual(before_root.subLayerOffsets, after_root.subLayerOffsets)

    async def test_collect_failure_with_exception(self):
        with self.assertRaises(CollectorException):
            collector = Collector("invalid_source.usd", self.get_test_dir(), False, False, False)
            await collector.collect(None, None)

        with self.assertRaises(CollectorException):
            current_path = Path(__file__).parent
            test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
            test_stage_path = str(test_data_path.joinpath("test_stages").joinpath("normal/FullScene.usd"))
            collector = Collector(test_stage_path, "Z:/__unknown_path_that_must_not_exist__", False, False, False)
            await collector.collect(None, None)

        with patch("omni.client.copy_async", side_effect=_mock_copy_access_denied):
            with self.assertRaises(CollectorException) as e:
                current_path = Path(__file__).parent
                test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
                test_stage_path = str(test_data_path.joinpath("test_stages").joinpath("normal/FullScene.usd"))
                collector = Collector(test_stage_path, "Z:/__dummy_access_denied_path__", False, False, False)
                await collector.collect(None, None)

            self.assertTrue(str(e.exception).startswith("Access denied: "))

        usd_error_option = CollectorFailureOptions.EXTERNAL_USD_REFERENCES
        other_error_option = CollectorFailureOptions.OTHER_EXTERNAL_REFERENCES
        all_option = CollectorFailureOptions.EXTERNAL_USD_REFERENCES | CollectorFailureOptions.OTHER_EXTERNAL_REFERENCES
        for option in [usd_error_option, other_error_option, all_option]:
            with self.assertRaises(CollectorException):
                current_path = Path(__file__).parent
                test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
                test_stage_path = str(test_data_path.joinpath("test_stages/normal").joinpath("FullScene.usd"))
                collected_stage_dir = self.get_test_dir() + "/test_collected_normal"
                collector = Collector(test_stage_path, collected_stage_dir, False, False, False, failure_options=option)
                await collector.collect(None, None)

    async def test_utils(self):
        self.assertTrue(Utils.is_udim_texture("test.<UDIM>.png"))
        self.assertTrue(Utils.is_udim_texture("test_<UDIM>_suffix.png"))
        self.assertTrue(Utils.is_udim_texture("test.%3cUDIM%3e.png"))
        self.assertFalse(Utils.is_udim_texture(""))
        self.assertFalse(Utils.is_udim_texture("random"))
        self.assertTrue(Utils.is_udim_wildcard_texture("test_0001_suffix.png", "test_<UDIM>_suffix.png"))
        self.assertFalse(Utils.is_udim_wildcard_texture("test_0001_another_suffix.png", "test_<UDIM>_suffix.png"))
        self.assertTrue(
            Utils.is_udim_wildcard_texture(
                "omniverse://fake-server/base_path/test_0001_suffix.png",
                "omniverse://fake-server/base_path/test_<UDIM>_suffix.png",
            )
        )
        self.assertFalse(
            Utils.is_udim_wildcard_texture(
                "omniverse://fake-server/base_path/test_0001_another_suffix.png",
                "omniverse://fake-server/base_path/test_<UDIM>_suffix.png",
            )
        )

    async def test_path_calculation(self):
        # Tests for https://nvidia-omniverse.atlassian.net/browse/OM-34746

        current_path = Path(__file__).parent
        test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
        test_stage_path = str(test_data_path.joinpath("test_stages").joinpath("normal/FullScene.usd"))
        collector = Collector(test_stage_path, self.get_test_dir(), False, False, False)
        path = collector._calculate_target_path("http://test_server/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/test_server/testfile.png")

        path = collector._calculate_target_path(str(test_data_path) + "/deep_folder/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/deep_folder/testfile.png")

        path = collector._calculate_target_path("omniverse://test_server/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/test_server/testfile.png")

        # Flat collect
        collector._flat_collection = True
        collector._material_only = False
        path = collector._calculate_target_path("omniverse://test_server/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/SubUSDs/textures/testfile.png")

        path = collector._calculate_target_path("http://test_server/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/SubUSDs/textures/testfile.png")

        path = collector._calculate_target_path("http://test_server/testfile.usd")
        self.assertEqual(path, self.get_test_dir() + "/SubUSDs/testfile.usd")

        # OMPE-38777: Test target path caculation for path with spaces
        path = collector._calculate_target_path("omniverse://test_server/test file.png")
        self.assertEqual(path, self.get_test_dir() + "/SubUSDs/textures/test file.png")

        # Materials only with flat collect
        collector._flat_collection = True
        collector._material_only = True
        path = collector._calculate_target_path("omniverse://test_server/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/textures/testfile.png")

        path = collector._calculate_target_path("http://test_server/testfile.png")
        self.assertEqual(path, self.get_test_dir() + "/textures/testfile.png")

        # Master USD with flat collect
        collector._flat_collection = True
        collector._material_only = False
        path = collector._calculate_target_path(test_stage_path)
        self.assertEqual(path, self.get_test_dir() + "/FullScene.usd")

        if sys.platform == "win32":
            collector = Collector("d:/test_folder/test.usd", "z:/test", False, False, False)
            path = collector._calculate_target_path("c:/test_folder/testfile.png")
            self.assertEqual(path, "Z:/test/C/test_folder/testfile.png")

    async def test_exclusion_rules(self):
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        extension_path = Path(extension_path)
        test_data_path = extension_path.joinpath("data")
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath("normal"))
        await self.__test_internal(
            "normal", "FullScene.usd", False, False, False, exclusion_rules={f"{test_stage_dir}/ov-sandbox": "/mount"}
        )

    async def test_collect_with_absolute_paths(self):
        root_usd, _, _, _ = await self.__test_internal("absolute_paths", "environments.usda", False, False, False)
        self.assertTrue(root_usd is not None)

        def modifiy_paths_cb(path):
            url = omni.client.break_url(path)

            # Ensure all paths are converted to relative paths.
            self.assertTrue(url.scheme is None)

            return path

        layer = Sdf.Layer.FindOrOpen(root_usd)
        self.assertTrue(layer)
        UsdUtils.ModifyAssetPaths(layer, modifiy_paths_cb)

    async def test_collect_usd_only_with_reference(self):
        """Test that when collecting with USD only option with a stage with reference, it doesn't modify the original asset being referenced."""
        test_data_path = self.__get_test_dir()
        asset_path = test_data_path.joinpath("test_stages").joinpath("assets").joinpath("box_with_material.usd")
        mtime = os.path.getmtime(asset_path)
        root_usd, _, _, _ = await self.__test_internal("stage_with_reference", "stage_with_ref.usd", True, False, False, with_reference=True)
        stage = Usd.Stage.Open(root_usd)
        asset_prim = stage.GetPrimAtPath("/box_with_material/Cube")
        self.assertTrue(asset_prim.IsValid())
        # Make sure there's no material binding left
        from pxr import UsdShade
        material_binding_api = UsdShade.MaterialBindingAPI(asset_prim)
        self.assertFalse(material_binding_api.GetDirectBinding().GetMaterial())
        # Make sure the original asset is not modified
        self.assertEqual(mtime, os.path.getmtime(asset_path))

    async def test_collect_with_spaces_in_path(self):
        await self.__test_internal("test path with space", "test file.usda", False, False, False)
