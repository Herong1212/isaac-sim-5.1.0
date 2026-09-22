# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import posixpath
import shutil
import tempfile
import toml
import os
import omni.kit.test
import carb
import omni.usd
import omni.kit.app
import omni.kit.material.library.material_config_utils as mc_utils
from omni.kit.test.async_unittest import AsyncTestCase
from pathlib import Path

TEST_PATH_STRS = [
    "C:/some/project/materials",
    "omniverse://another/project/materials",
    "/my/own/materials"
]


def _compare_toml_files(file1, file2):
    # the toml module does not preserve the item order in files so can't use
    # simple line comparison. needs to compare them as dicts
    toml1 = toml.load(file1)
    toml2 = toml.load(file2)
    return (toml1 == toml2)


class PreferencesTestMaterialConfigUtilsAPI(AsyncTestCase):
    # run only once at the beginning
    @classmethod
    def setUpClass(cls):
        # test config file path
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        data_tests_dir = Path(ext_path) / "data/tests"
        test_config_file_path = data_tests_dir / "material.config.toml"
        test_config_carb_file_path = data_tests_dir / "material.config.carb.toml"

        # create temp home dir
        cls._temp_home = Path(tempfile.mkdtemp())
        cls._temp_home = cls._temp_home.as_posix()

        # copy test config files to the temp home
        cls._temp_kit_shared_dir = posixpath.join(cls._temp_home, "Documents/Kit/shared")
        if not os.path.exists(cls._temp_kit_shared_dir):
            os.makedirs(cls._temp_kit_shared_dir)
        shutil.copy(test_config_file_path, cls._temp_kit_shared_dir)
        shutil.copy(test_config_carb_file_path, cls._temp_kit_shared_dir)

        # temporary wipe out material config in settings
        settings = carb.settings.get_settings()
        cls._curr_material_config = settings.get("/materialConfig")
        settings.set("/materialConfig", {})


    # run only once at the end
    @classmethod
    def tearDownClass(cls):
        # remove settings used in tests
        settings = carb.settings.get_settings()
        settings.destroy_item("/materialConfigTests")

        # restore material config in settings
        settings.set("/materialConfig", {})
        settings.set("/materialConfig", cls._curr_material_config)

        # delete temp home dir
        if os.path.exists(cls._temp_home):
            shutil.rmtree(cls._temp_home)


    # before running each test
    async def setUp(self):
        # temporary set ${shared_documents} path
        carb_tokens = carb.tokens.get_tokens_interface()
        self._original_shared_dir = carb_tokens.resolve("${shared_documents}")
        carb_tokens.set_value("shared_documents", self._temp_kit_shared_dir)


    # after running each test
    async def tearDown(self): # pragma: no cover
        carb.tokens.get_tokens_interface().set_value("shared_documents", self._original_shared_dir)


    async def test_key_value_to_dict(self):
        key = "/path/to/float_key"
        value = 2.3
        expect = {"path": {"to": {"float_key": 2.3}}}
        self.assertEqual(expect, mc_utils._key_value_to_dict(key, value))

        key = "/path/to/string_key"
        value = "coffee"
        expect = {"path": {"to": {"string_key": "coffee"}}}
        self.assertEqual(expect, mc_utils._key_value_to_dict(key, value))

        key = "/path/to/list_key"
        value = [2, 3, 5, 7, 11]
        expect = {"path": {"to": {"list_key": [2, 3, 5, 7, 11]}}}
        self.assertEqual(expect, mc_utils._key_value_to_dict(key, value))


    async def test_merge_dict(self):
        dict1 = {"searchPaths": {"custom": ["/my/path/one", "/my/path/two"]},
                 "materialGraph": {"userAllowList": ["myMDL1.mdl", "myMDL2.mdl"]}}
        dict2 = {"searchPaths": {"custom": ["/my/another/path"]},
                 "materialGraph": {"userAllowList": ["myMDL1.mdl", "myMDL3.mdl"],
                                   "userBlockList": ["hiddenMDL1.mdl", "hiddenMDL2.mdl"]}}
        expect = {"searchPaths": {"custom": ["/my/path/one", "/my/path/two", "/my/another/path"]},
                  "materialGraph": {"userAllowList": ["myMDL1.mdl", "myMDL2.mdl", "myMDL3.mdl"],
                                    "userBlockList": ["hiddenMDL1.mdl", "hiddenMDL2.mdl"]}}
        self.assertEqual(expect, mc_utils._merge_dict(dict1, dict2))


    async def test_get_config_file_path(self):
        expect = Path(self._temp_home) / "Documents/Kit/shared" / "material.config.toml"
        expect = expect.as_posix()
        self.assertEqual(expect, mc_utils.get_config_file_path())


    async def test_get_config_from_carb_settings(self):
        test_settings = (
            ["materialGraph/userAllowList", ["my_materials", "my_maps"]],
            ["materialGraph/userBlockList", ["foo_materials", "bar_maps"]],
            ["options/noStandardPath", False],
            ["searchPaths/custom", TEST_PATH_STRS]
        )

        # assign to /materialConfig carb settings
        settings = carb.settings.get_settings()
        for i in test_settings:
            setting_key = posixpath.join("/materialConfig", i[0])
            settings.set(setting_key, i[1])

        config = mc_utils.get_config_from_carb_settings()

        expect = ["my_materials", "my_maps"]
        self.assertEqual(expect, config["materialGraph"]["userAllowList"])
        expect = ["foo_materials", "bar_maps"]
        self.assertEqual(expect, config["materialGraph"]["userBlockList"])
        expect = False
        self.assertEqual(expect, config["options"]["noStandardPath"])
        expect = TEST_PATH_STRS
        self.assertEqual(expect, config["searchPaths"]["custom"])


    async def test_load_config_file(self):
        config_file_path = mc_utils.get_config_file_path()
        config = mc_utils.load_config_file(config_file_path)

        expect = ["my_materials", "my_maps"]
        self.assertEqual(expect, config["materialGraph"]["userAllowList"])
        expect = ["foo_materials", "bar_maps"]
        self.assertEqual(expect, config["materialGraph"]["userBlockList"])
        expect = False
        self.assertEqual(expect, config["options"]["noStandardPath"])
        expect = TEST_PATH_STRS
        self.assertEqual(expect, config["searchPaths"]["custom"])


    async def test_save_config_file(self):
        config = {}
        config["materialGraph"] = {}
        config["materialGraph"]["userAllowList"] = ["my_materials", "my_maps"]
        config["materialGraph"]["userBlockList"] = ["foo_materials", "bar_maps"]
        config["options"] = {}
        config["options"]["noStandardPath"] = False
        config["searchPaths"] = {}
        config["searchPaths"]["custom"] = TEST_PATH_STRS
        config["configFilePath"] = "/dummy/path/material.config.toml"

        # save new file
        new_config_file_path = posixpath.join(self._temp_kit_shared_dir, "material.config.saved.toml")
        self.assertTrue(mc_utils.save_config_file(config, new_config_file_path))

        # compare to the original file
        orig_config_file_path = mc_utils.get_config_file_path()
        self.assertTrue(_compare_toml_files(new_config_file_path, orig_config_file_path))


    async def test_save_carb_setting_to_config_file(self):
        test_settings = (
            ("string", "coffee", False),
            ("float", 24.0, False),
            ("bool", True, False),
            ("paths", ";".join(TEST_PATH_STRS), True)
        )

        # assign to carb settings
        settings = carb.settings.get_settings()
        for i in test_settings:
            setting_key = posixpath.join("/materialConfigTests", i[0])
            settings.set(setting_key, i[1])

        # save new file
        new_config_carb_file_path = posixpath.join(self._temp_kit_shared_dir, "material.config.carb.saved.toml")
        for i in test_settings:
            carb_key = posixpath.join("/materialConfigTests", i[0])
            config_key = posixpath.join("tests", i[0])
            mc_utils.save_carb_setting_to_config_file(
                carb_key,
                config_key,
                is_paths=i[2],
                non_standard_path=new_config_carb_file_path
            )

        # compare to the original file
        orig_config_carb_file_path = posixpath.join(self._temp_kit_shared_dir, "material.config.carb.toml")
        self.assertTrue(_compare_toml_files(new_config_carb_file_path, orig_config_carb_file_path))


    async def test_save_live_config_to_file(self):
        test_settings = (
            ("materialGraph/userAllowList", ["my_materials", "my_maps"]),
            ("materialGraph/userBlockList", ["foo_materials", "bar_maps"]),
            ("options/noStandardPath", False),
            ("searchPaths/custom", TEST_PATH_STRS)
        )

        # assign to /materialConfig carb settings
        settings = carb.settings.get_settings()
        for i in test_settings:
            setting_key = posixpath.join("/materialConfig", i[0])
            settings.set(setting_key, i[1])

        # save new file
        new_config_file_path = posixpath.join(self._temp_kit_shared_dir, "material.config.saved2.toml")
        mc_utils.save_live_config_to_file(non_standard_path=new_config_file_path)

        # compare to the original file
        orig_config_file_path = mc_utils.get_config_file_path()
        self.assertTrue(_compare_toml_files(new_config_file_path, orig_config_file_path))
