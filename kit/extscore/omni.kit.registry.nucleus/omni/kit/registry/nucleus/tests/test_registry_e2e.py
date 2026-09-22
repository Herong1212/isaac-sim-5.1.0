import inspect
import shutil
import os
import glob
import sys
import gzip
import json

import carb.tokens
import omni.client
import omni.kit.test
import omni.kit.core.tests

from omni.kit.core.tests import run_process


def _get_source(fn):
    # remove def
    lines = inspect.getsourcelines(fn)[0][1:]

    # remove extra indentation
    max_indent = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    lines = [l[max_indent:] for l in lines]

    return "\n".join(lines)


def build_dir(path):
    os.makedirs(path, exist_ok=True)
    return path.replace("\\", "/")


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def build_extension(exts_dir: str, ext_id: str, config_content: str = ""):
    ext_path = build_dir(f"{exts_dir}/{ext_id}")
    ext_config_dir = build_dir(f"{ext_path}/config")
    write_file(f"{ext_config_dir}/extension.toml", config_content)
    return ext_path

def read_gz_json(path):
    with gzip.open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))

def write_gz_json(path, data):
    with gzip.open(path, "wb") as f:
        f.write(json.dumps(data).encode("utf-8"))

_registry_url_override = None

def set_registry_url_override(url):
    global _registry_url_override
    _registry_url_override = url


class RegistryTestBoilerplate:
    def __init__(self, root, extra_args=None):
        self.root = root
        self.exts_dir = build_dir(f"{self.root}/exts")
        self.registry_dir = _registry_url_override or build_dir(f"{self.root}/registry")
        self.cache_dir = build_dir(f"{self.root}/cache")
        self.install_dir = build_dir(f"{self.root}/install")
        self.extra_args = extra_args

    def get_common_kit_args(self):
        args = []
        args += ["--/app/enableStdoutOutput=0"]
        if self.extra_args:
            args += self.extra_args
        return args

    def get_common_registry_args(self, registry_enabled=True):
        args = self.get_common_kit_args()
        args += [f"--/app/extensions/registryEnabled={registry_enabled}"]
        args += ["--/app/extensions/skipPublishVerification=1"]
        args += [f'--/app/extensions/registryCacheFull="{self.install_dir}"']
        args += [f"--/exts/omni.kit.registry.nucleus/usePackmanToUploadArchives=0"]
        args += [f'--/exts/omni.kit.registry.nucleus/cachePath="{self.cache_dir}"']
        args += [f'--/exts/omni.kit.registry.nucleus/cacheVersionSubdir=""']
        args += [f'--/exts/omni.kit.registry.nucleus/registries/0/url="{self.registry_dir}"']
        args += [f'--/exts/omni.kit.registry.nucleus/registries/1/url=""']
        args += [f'--/exts/omni.kit.registry.nucleus/registries/2/url=""']
        args += [f'--/exts/omni.kit.registry.nucleus/registries/3/url=""']
        return args

    def build_repo_tools_boileplate(self):
        tokens = carb.tokens.get_tokens_interface()
        self.repo_dir = build_dir(f"{self.root}/repo")

        # reuse deps file from kit
        shutil.copy(tokens.resolve("${kit}/dev/deps/repo-deps.packman.xml"), build_dir(f"{self.repo_dir}/deps"))

        # version is required for some tools
        write_file(f"{self.repo_dir}/VERSION.md", "1.2.3")

        # build repoman.py
        self.repoman_py = f"{self.repo_dir}/repoman.py"
        write_file(
            self.repoman_py,
            f"""
import packmanapi
import os, sys
REPO_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)))
REPO_DEPS_FILE = os.path.join(REPO_ROOT, "deps/repo-deps.packman.xml")
deps = packmanapi.pull(REPO_DEPS_FILE)
sys.path.extend(deps.values())
sys.path.append("{tokens.resolve("${kit}/dev")}")

if __name__ == "__main__":
    import omni.repo.man
    omni.repo.man.main(REPO_ROOT)
""",
        )

        # path to packman's python script we use to run repoman
        self.packman_python = tokens.resolve("${kit}/dev/tools/packman/python${shell_ext}")


class TestRegistryE2E(omni.kit.core.tests.KitLaunchTest):
    async def _run_process_and_check(self, args, timeout=60):
        code, err_messages, stdout = await run_process(args, timeout)
        if len(err_messages) > 0:
            print(err_messages)
        self.assertEqual(len(err_messages), 0, msg=err_messages)
        self.assertEqual(code, 0)

    async def _test_ext_can_be_pulled(self, ext_ids, test: RegistryTestBoilerplate):
        """Shared function to reuse testing that extension can be pulled from the registry"""

        if isinstance(ext_ids, str):
            ext_ids = [ext_ids]

        # script to pull and check
        def script():
            import omni.kit.app

            app = omni.kit.app.get_app()
            m = app.get_extension_manager()
            m.sync_registry()
            for ext_id in EXT_IDS:
                data = m.get_registry_extension_dict(ext_id)
                assert data != None
                assert data.get_dict()["package"]["packageId"] == ext_id
                m.pull_extension(ext_id)
                data = m.get_extension_dict(ext_id)
                assert data != None
                assert data.get_dict()["package"]["packageId"] == ext_id
            app.post_quit(0)

        script_source = _get_source(script).replace("EXT_IDS", str(ext_ids))

        # run kit with script
        await self._run_kit_with_script(
            script_source,
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--/app/quitAfter=10", "--/crashreporter/gatherUserStory=0"],
        )

    async def _run_kit_to_batch_publish(self, ext_ids, test: RegistryTestBoilerplate):
        # run kit to batch publish in one go
        def script():
            import omni.kit.app

            app = omni.kit.app.get_app()
            m = app.get_extension_manager()
            m.sync_registry()
            import omni.kit.registry.nucleus

            # split list in 2 batches, to test that we can publish in multiple batches

            def split_list(a_list):
                half = len(a_list) // 2
                return a_list[:half], a_list[half:]

            batch_1, batch_2 = split_list(EXT_IDS)

            omni.kit.registry.nucleus.start_index_changes_batching()
            for ext_id in batch_1:
                m.publish_extension(ext_id)
            omni.kit.registry.nucleus.apply_index_changes_batch()

            omni.kit.registry.nucleus.start_index_changes_batching()
            for ext_id in batch_2:
                m.publish_extension(ext_id)
            omni.kit.registry.nucleus.apply_index_changes_batch()

            app.post_quit(0)

        await self._run_kit_with_script(
            _get_source(script).replace("EXT_IDS", str(ext_ids)),
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--ext-folder", test.exts_dir],
        )

    async def _run_kit_publish_ext(self, ext_id: str, test: RegistryTestBoilerplate):
        await self._run_kit_and_check(
            args=[*test.get_common_registry_args(), "--publish", ext_id, "--ext-folder", test.exts_dir]
        )

    async def test_simple_publish_pull_unpublish(self):
        """
        Publish extension, pull it, unpublish, verify
        """

        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_ID = "omni.blob-1.2.3"

        build_extension(test.exts_dir, EXT_ID)

        # publish
        await self._run_kit_publish_ext(EXT_ID, test)

        # pull extension
        await self._test_ext_can_be_pulled(EXT_ID, test)

        # unpublish
        await self._run_kit_and_check(args=[*test.get_common_registry_args(), "--unpublish", EXT_ID])

        # run kit with script to check it is marked as yanked now
        def script():
            import omni.kit.app

            app = omni.kit.app.get_app()
            m = omni.kit.app.get_app().get_extension_manager()
            m.sync_registry()
            assert m.get_extension_dict("EXT_ID") == None
            d = m.get_registry_extension_dict("EXT_ID")
            assert d != None
            assert d.get_dict()["package"]["yanked"] == True
            app.post_quit(0)

        script_source = _get_source(script).replace("EXT_ID", EXT_ID)

        await self._run_kit_with_script(
            script_source,
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--/app/quitAfter=10", "--/crashreporter/gatherUserStory=0"],
        )

    async def test_full_unpublish(self):
        """
        Test old-school unpublishing (not yanking)
        """

        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_ID_TO_UNPUBLISH = "omni.bleep-1.2.4"
        EXT_IDS = [
            EXT_ID_TO_UNPUBLISH,
            "omni.bleep-1.2.5"
        ]
        for ext_id in EXT_IDS:
            build_extension(test.exts_dir, ext_id)

        # publish
        await self._run_kit_to_batch_publish(EXT_IDS, test)

        # unpublish latest to make it tricier with summaries.json
        await self._run_kit_and_check(args=[*test.get_common_registry_args(), "--unpublish", EXT_ID_TO_UNPUBLISH, "--/exts/omni.kit.registry.nucleus/yankWhenUnpublishing=0",])

        # run kit with script to check it doesn't exist anymore
        def script():
            import omni.kit.app

            app = omni.kit.app.get_app()
            m = app.get_extension_manager()
            m.sync_registry()
            assert len(m.get_registry_extensions()) == 1
            assert m.get_extension_dict("EXT_ID") == None
            assert m.get_registry_extension_dict("EXT_ID") == None
            app.post_quit(0)

        script_source = _get_source(script).replace("EXT_ID", EXT_ID_TO_UNPUBLISH)

        await self._run_kit_with_script(
            script_source,
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--/app/quitAfter=10", "--/crashreporter/gatherUserStory=0"],
        )

        # Other one still can be pulled
        # await self._test_ext_can_be_pulled("omni.bleep-1.2.3", test)


    async def test_publish_images_and_metadata(self):
        """
        Publish extension images and metadata
        """

        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_ID = "omni.fancy-1.2.3"

        # Build extension with icon and image
        config_content = """
[package]
icon = "data/icon.png"
preview_image = "data/preview.png"
"""
        ext_path = build_extension(test.exts_dir, EXT_ID, config_content=config_content)
        os.makedirs(f"{ext_path}/data", exist_ok=True)
        open(f"{ext_path}/data/icon.png", "w").write("icon")
        open(f"{ext_path}/data/preview.png", "w").write("preview")

        # publish
        await self._run_kit_publish_ext(EXT_ID, test)

        # run kit with script to check images and metadata are published
        def script():
            import omni.kit.app
            import json

            app = omni.kit.app.get_app()
            m = omni.kit.app.get_app().get_extension_manager()
            m.sync_registry()
            ext_data = m.get_registry_extension_dict("EXT_ID")
            import omni.kit.registry.nucleus
            url = omni.kit.registry.nucleus.get_extension_metadata_url(ext_data)
            assert url is not None

            def read_file(url_or_path):
                _, _, content = omni.client.read_file(url_or_path)
                return memoryview(content).tobytes().decode("utf-8")

            # read full metadata json, it has more field, like kit version it was published with
            data = json.loads(read_file(url))
            assert data["package"]["publish"]["kitVersion"]
            # check that images are published and the same
            preview_image_url = omni.kit.registry.nucleus.get_preview_image_url(ext_data)
            assert read_file(preview_image_url) == "preview"
            icon_url = omni.kit.registry.nucleus.get_icon_url(ext_data)
            assert read_file(icon_url) == "icon"
            app.post_quit(0)

        script_source = _get_source(script).replace("EXT_ID", EXT_ID)

        await self._run_kit_with_script(
            script_source,
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--/app/quitAfter=10"],
        )

    async def test_publish_dict_filters(self):
        """
        Check that extension filters (filter:key) are preserved and used in the registry
        """

        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_ID = "omni.dict_filters-1.2.3"

        # Build extension with os and setting filter to control dependenncy
        config_content = """
[dependencies."filter:os"."windows"]
"filter:setting".app.yesMode."value:true"."omni.win_yes" = {}
"filter:setting".app.yesMode."value:false"."omni.win_no" = {}

[dependencies."filter:os"."linux"]
"filter:setting".app.yesMode."value:true"."omni.lin_yes" = {}
"filter:setting".app.yesMode."value:false"."omni.lin_no" = {}
"""
        build_extension(test.exts_dir, EXT_ID, config_content=config_content)

        # publish
        await self._run_kit_publish_ext(EXT_ID, test)

        # run kit with script to check images and metadata are published
        def script():
            import omni.kit.app

            import carb.settings

            # expect depenendecy based on passed setting and current platform
            app = omni.kit.app.get_app()
            yes_mode = carb.settings.get_settings().get("/app/yesMode")
            is_win = app.get_platform_info()['platform'] == "windows-x86_64"
            expected_dep = "omni.{}_{}".format("win" if is_win else "lin", "yes" if yes_mode else "no")

            m = omni.kit.app.get_app().get_extension_manager()
            m.sync_registry()

            data = m.get_registry_extension_dict("EXT_ID")
            print(data)
            assert data != None
            deps = data.get_dict()["dependencies"]
            assert deps.keys() == {expected_dep}

            app.post_quit(0)

        script_source = _get_source(script).replace("EXT_ID", EXT_ID)

        # run with both yesMode setting values to check that filter is used correctly
        for i in range(2):
            yes_mode = str(i == 0).lower()
            await self._run_kit_with_script(
                script_source,
                args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--/app/quitAfter=10", f"--/app/yesMode={yes_mode}"],
            )


    async def test_refresh_index(self):
        """Test refresh_index API, where registry can be synced without blocking."""
        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_ID = "omni.blob-1.2.3"

        build_extension(test.exts_dir, EXT_ID)

        # publish
        await self._run_kit_publish_ext(EXT_ID, test)

        # script to refresh registry and wait until it updates
        def script():
            import omni.kit.app
            import omni.kit.async_engine
            import asyncio

            async def _task():
                app = omni.kit.app.get_app()
                m = app.get_extension_manager()
                m.refresh_registry()
                for i in range(100):
                    await app.next_update_async()
                    if len(m.get_registry_extensions()) > 0:
                        assert i > 0  # it takes more than 1 frame to refresh
                        assert m.get_registry_extension_dict("EXT_ID") != None
                        app.post_quit(0)
                        return

                assert False

            omni.kit.async_engine.run_coroutine(_task())

        script_source = _get_source(script).replace("EXT_ID", EXT_ID)

        # run kit with script
        await self._run_kit_with_script(
            script_source,
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.async_engine", "--enable", "omni.kit.loop"],
        )

    async def test_incremental_fetch(self):
        """
        Publish multiple versions of an extension and verify that only the latest version is seen at first. But when
        solving dependencies others can be found (fetched).
        """

        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_IDS = [
            "omni.blob-1.2.3",
            "omni.blob-2.1.0",  # highest one preferred, not the latest
            "omni.blob-2.0.0",
            "omni.play-1.2.3",
            "omni.play-1.5.3",
            "omni.play-2.0.0",
        ]

        for ext_id in EXT_IDS:
            build_extension(test.exts_dir, ext_id)

        # run kit to batch publish in one go
        await self._run_kit_to_batch_publish(EXT_IDS, test)

        # run kit with script to check incremental fetching
        def script():
            import omni.kit.app

            app = omni.kit.app.get_app()
            m = omni.kit.app.get_app().get_extension_manager()
            def get_ids():
                return {ext["id"] for ext in m.get_registry_extensions()}

            m.sync_registry()
            assert get_ids() == {"omni.blob-2.1.0", "omni.play-2.0.0"}

            # solver will trigger fetching more packages for "blob", but not for "play"
            result, exts, err = m.solve_extensions(["omni.blob-1.2.3"])
            assert result == True
            assert get_ids() == {"omni.blob-2.1.0", "omni.blob-1.2.3", "omni.blob-2.0.0", "omni.play-2.0.0"}

            # asking explicitly will get it fetched (all versions)
            assert m.get_registry_extension_dict("omni.play-1.2.3") != None
            assert get_ids() == {"omni.blob-2.1.0", "omni.blob-1.2.3", "omni.blob-2.0.0", "omni.play-2.0.0", "omni.play-1.2.3", "omni.play-1.5.3"}

            app.post_quit(0)

        await self._run_kit_with_script(
            _get_source(script),
            args=[*test.get_common_registry_args(), "--enable", "omni.kit.loop", "--/app/quitAfter=10"],
        )

    async def test_version_lock(self):
        """Basic test of generating and updating version lock on a kit file.
        """

        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_IDS = [
            "omni.mystery-1.2.0",
            "omni.mystery-1.3.0",
            "omni.mystery-2.0.0",
        ]

        for ext_id in EXT_IDS:
            build_extension(test.exts_dir, ext_id)

        # publish all
        await self._run_kit_to_batch_publish(EXT_IDS, test)

        # helper to generate version lock on a new kit file
        async def gen_version_lock_and_check(expect_lock_list=None, expect_errors=None):
            kit_file_path = f"{test.root}/foo.kit"
            write_file(kit_file_path,
            f"""
[dependencies]
"omni.mystery" = {{ version = "1.0.0" }}
"""
            )
            version_lock_args = [kit_file_path, *test.get_common_registry_args(), "--/app/extensions/generateVersionLock=1", "--/app/extensions/supportedTargets/verify=1"]
            shutil.rmtree(test.install_dir)
            if expect_lock_list:
                await self._run_kit_and_check(args=version_lock_args)
                kit_file_dict = carb.dictionary.get_toml_serializer().create_dictionary_from_file(kit_file_path)
                lock_list = kit_file_dict.get("settings/app/exts/enabled", [])
                self.assertEqual(lock_list, expect_lock_list)
            else:
                await self._run_kit_and_capture_stdout(
                    args=version_lock_args,
                    expect_errors=expect_errors,
                    expect_success=False,
                )

        # Start fresh, only having registry, check that locks to latest 1.X.X version
        shutil.rmtree(test.cache_dir)
        shutil.rmtree(test.exts_dir)
        await gen_version_lock_and_check(("omni.mystery-1.3.0",))

        # Platform check, only publish release version of a new 1.4. Version lock should fail on platform check.
        # Then publish debug version of 1.4. Version lock should succeed.
        config_content = """
[package]
target.config = ["release"]
"""
        build_extension(test.exts_dir, "omni.mystery-1.4.0", config_content=config_content)
        await self._run_kit_publish_ext("omni.mystery-1.4.0", test)
        await gen_version_lock_and_check(expect_errors=["Supported targets check failed"])

        config_content = """
[package]
target.config = ["debug"]
"""
        build_extension(test.exts_dir, "omni.mystery-1.4.0", config_content=config_content)
        shutil.rmtree(test.install_dir)
        await self._run_kit_publish_ext("omni.mystery-1.4.0", test)
        await gen_version_lock_and_check(("omni.mystery-1.4.0",))

    async def test_corrupted_cache(self):
        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_ID = "omni.blob-1.2.3"

        build_extension(test.exts_dir, EXT_ID)

        # publish
        await self._run_kit_publish_ext(EXT_ID, test)

        # pull by enabling
        await self._run_kit_and_check(args=[*test.get_common_registry_args(), "--enable", EXT_ID])

        # corrupt cache with broken toml
        with open(f"{test.cache_dir}/{EXT_ID}/config/extension.gen.toml", "w") as f:
            f.write("[broken_toml\n")

        # enabling will fail now. Capture all output not to fail main test and replace errors
        # make sure NOT to use registry to fix the cache
        await self._run_kit_and_capture_stdout(
            args=[*test.get_common_registry_args(registry_enabled=False), "--enable", EXT_ID],
            expect_errors=["Failed to parse generated config"],
            expect_success=False,
        )

        # run again, but with registry. It should clean the cache, try again and succeed
        await self._run_kit_and_capture_stdout(
            args=[*test.get_common_registry_args(registry_enabled=True), "--enable", EXT_ID],
            expect_errors=["Failed to parse generated config"],
            expect_success=True,
        )

    async def test_summaries_and_packages_desync(self):
        """There is a pretty rare situation when summaries can desync from packages. When mulitple clients modify the registry.
        Even rarer that it could be that the latest version in summary file is not available anymore in the packages file.
        Extension manager might ask to pull this extension, say if we just `--enable omni.prawn`. Not much can we do, but to error out.
        """
        test = RegistryTestBoilerplate(self._temp_folder)

        # publish 2 exts
        EXT_IDS = [
            "omni.prawn-1.2.0",
            "omni.prawn-1.3.0",
        ]
        for ext_id in EXT_IDS:
            build_extension(test.exts_dir, ext_id)
        await self._run_kit_to_batch_publish(EXT_IDS, test)

        summary_file = f"{test.registry_dir}/v2/summaries.gz"
        registry_file = f"{test.registry_dir}/v2/registry.gz"
        summary_file_bak = summary_file + ".bak"

        # copy summaries and remembe sha1:
        shutil.copy(summary_file, summary_file_bak)
        summary_sha = read_gz_json(registry_file)["files"]["summaries.json"]

        # unpublish latest
        await self._run_kit_and_check(args=[*test.get_common_registry_args(), "--unpublish", EXT_IDS[1], "--/exts/omni.kit.registry.nucleus/yankWhenUnpublishing=0",])

        # copy back summaries back and update sha1:
        shutil.copy(summary_file_bak, summary_file)
        # update sha:
        data = read_gz_json(registry_file)
        data["files"]["summaries.json"] = summary_sha
        write_gz_json(registry_file, data)

        await self._run_kit_and_capture_stdout(
            args=[*test.get_common_registry_args(), "--enable", "omni.prawn"],
            expect_errors=["Likely the registry summary file desynced from the package file for this extension"],
            expect_success=False,
        )


    async def test_reuse_same_package_for_different_targets(self):
        test = RegistryTestBoilerplate(self._temp_folder)

        # Set to write kit hash (lock to it)
        EXT_ID = "omni.blob-1.2.3"
        config_content = """
[package]
writeTarget.kitHash = true
repository=123
"""
        build_extension(test.exts_dir, EXT_ID, config_content=config_content)

        # Set to use content hash as archive name. This makes package not match package id in the registry 1 to 1.
        registry_args = [
            *test.get_common_registry_args(),
            "--/exts/omni.kit.registry.nucleus/useContentHashAsArchiveName=1",
        ]

        # publish with 2 different kit hash
        publish_args = [*registry_args, "--publish", EXT_ID, "--ext-folder", test.exts_dir]
        await self._run_kit_and_check(args=[*publish_args, "--/app/extensions/target/kitHash='aaaaaaaa'"])
        await self._run_kit_and_check(args=[*publish_args, "--/app/extensions/target/kitHash='bbbbbbbb'"])

        # install by different kit hash kit runs
        install_args = [*test.get_common_registry_args(), "--enable", EXT_ID]
        await self._run_kit_and_check(args=[*install_args, "--/app/extensions/target/kitHash='aaaaaaaa'"])
        await self._run_kit_and_check(args=[*install_args, "--/app/extensions/target/kitHash='bbbbbbbb'"])

        # We should have 2 separate installations, but one packaeg in the cache. This package will have both kit hash written
        # to the generated config to be able to be reused.
        self.assertEqual(len(os.listdir(test.install_dir)), 2)
        self.assertEqual(len(glob.glob(f"{test.registry_dir}/**/omni.blob*.zip", recursive=True)), 1)
        configs = list(glob.glob(f"{test.cache_dir}/**/extension.gen.toml", recursive=True))
        self.assertEqual(len(configs), 1)
        config_content = open(configs[0], "r").read()
        self.assertIn("aaaaaaaa", config_content)
        self.assertIn("bbbbbbbb", config_content)

    async def test_simple_publish_with_a_tool(self):
        """
        Test publishing with a public_exts tool
        """

        test = RegistryTestBoilerplate(self._temp_folder)
        tokens = carb.tokens.get_tokens_interface()

        EXT_NAME = "omni.cherry"
        EXT_ID = f"{EXT_NAME}-1.2.3"

        build_extension(test.exts_dir, EXT_ID)

        # prepare repo man basic setup
        test.build_repo_tools_boileplate()

        # setup publish tool in repo.toml:
        write_file(
            f"{test.repo_dir}/repo.toml",
            f"""
[repo_publish_exts]
enabled = true

ext_folders = ["{test.exts_dir}"]
exts.include = ["{EXT_NAME}"]
registries = [
    {{ name = 'kit/default', url = '{test.registry_dir}' }},
]
kit_root = "{tokens.resolve("${kit}")}"
publish_verification = false
use_packman_to_upload_archive = false
""",
        )

        # run publish tool
        await self._run_process_and_check([test.packman_python, test.repoman_py, "publish_exts", "-c", "release"])

        # pull extension
        await self._test_ext_can_be_pulled(EXT_ID, test)

    async def test_precache_tool(self):
        """
        Test precache tool
        """

        test = RegistryTestBoilerplate(self._temp_folder)
        tokens = carb.tokens.get_tokens_interface()

        EXT_IDS = {
            "omni.eel-1.2.3": "",
            "omni.eel-2.1.0": "",
            "omni.salmon-2.0.0": "",
            "omni.trout-0.1.0": "",
            "omni.tuna-0.1.0": '[dependencies]\n"omni.salmon" = {}',
        }

        for ext_id, cfg in EXT_IDS.items():
            build_extension(test.exts_dir, ext_id, config_content=cfg)

        # run kit to batch publish in one go
        await self._run_kit_to_batch_publish(list(EXT_IDS.keys()), test)

        # prepare repo man basic setup
        test.build_repo_tools_boileplate()

        # kit file
        kit_file_path = f"{test.exts_dir}/omni.app.river.kit"
        write_file(
            kit_file_path,"""
[dependencies]
"omni.eel" = {}
"omni.tuna" = {}
"omni.trout" = {}

""")
        
        EXPECTED_EXTS = (
            "omni.eel-2.1.0",
            "omni.salmon-2.0.0",
            "omni.trout-0.1.0",
            "omni.tuna-0.1.0",
        )

        # setup publish tool in repo.toml:
        write_file(
            f"{test.repo_dir}/repo.toml",
            f"""
[repo_precache_exts]
enabled = true

apps = [
    "{kit_file_path}"
]
cache_path = "{test.install_dir}"
registries = [
    {{ name = 'kit/default', url = '{test.registry_dir}' }},
]
kit_path = "{tokens.resolve("${kit}")}/kit${{exe_ext}}"
""",
        )

        async def run_precache_tool_and_check(expected_lock, extra_args):
            # run publish tool
            await self._run_process_and_check([test.packman_python, test.repoman_py, "precache_exts", "-c", "release"] + extra_args)

            # check install dir:
            for ext_id in expected_lock:
                ext_path = f"{test.install_dir}/{ext_id}"
                self.assertTrue(os.path.exists(ext_path), f"Extension {ext_id} not found in install dir")

            # read version lock from a kit file:
            kit_file_dict = carb.dictionary.get_toml_serializer().create_dictionary_from_file(kit_file_path)
            lock_list = kit_file_dict.get("settings/app/exts/enabled", [])
            self.assertEqual(lock_list, expected_lock)

        await run_precache_tool_and_check(EXPECTED_EXTS, extra_args=[])

        # backup kit file:
        kit_file_bak = kit_file_path + ".bak"
        shutil.copy(kit_file_path, kit_file_bak)

        # publish new versions of some extensions
        NEW_EXTS = ["omni.eel-3.0.0", "omni.salmon-3.0.0", "omni.trout-0.2.0"]
        for ext_id in NEW_EXTS:
            build_extension(test.exts_dir, ext_id)
        await self._run_kit_to_batch_publish(NEW_EXTS, test)

        # only update 1 ext explicitly
        await run_precache_tool_and_check((
            "omni.eel-3.0.0",
            "omni.salmon-2.0.0",
            "omni.trout-0.1.0",
            "omni.tuna-0.1.0",
        ), extra_args=["-u", "omni.eel"])

        # restore backup
        shutil.copy(kit_file_bak, kit_file_path)

        # update 2 exts explicitly
        await run_precache_tool_and_check((
            "omni.eel-3.0.0",
            "omni.salmon-3.0.0",
            "omni.trout-0.1.0",
            "omni.tuna-0.1.0",
        ), extra_args=["-u", "omni.eel", "omni.salmon"])

        # restore backup
        shutil.copy(kit_file_bak, kit_file_path)

        # update all exts
        await run_precache_tool_and_check((
            "omni.eel-3.0.0",
            "omni.salmon-3.0.0",
            "omni.trout-0.2.0",
            "omni.tuna-0.1.0",
        ), extra_args=["-u"])


    async def test_migrations(self):
        test = RegistryTestBoilerplate(self._temp_folder)

        EXT_IDS = [
            "omni.blob-1.2.3",
            "omni.blob-2.1.0",  # highest one preferred, not the latest
            "omni.blob-2.0.0",
            "omni.play-1.2.3",
            "omni.play-2.0.0",
        ]

        for ext_id in EXT_IDS:
            build_extension(test.exts_dir, ext_id)

        # run kit to batch publish in one go
        await self._run_kit_to_batch_publish(EXT_IDS, test)

        # run migration v2 -> v1
        await self._run_kit_and_check(
            args=[
                *test.get_common_registry_args(),
                "--/app/extensions/syncRegistryOnStartup=1",
                "--/exts/omni.kit.registry.nucleus/runMigration=1",
                "--/exts/omni.kit.registry.nucleus/defautIndexVersion='v1'",
            ]
        )

        self.assertEqual(len(glob.glob(f"{test.registry_dir}/3/index.zip", recursive=True)), 1)
        os.remove(f"{test.registry_dir}/v2/registry.gz")

        # pull extension
        await self._test_ext_can_be_pulled("omni.blob-2.0.0", test)

        # run migration v1 -> v2
        await self._run_kit_and_check(
            args=[
                *test.get_common_registry_args(),
                "--/app/extensions/syncRegistryOnStartup=1",
                "--/exts/omni.kit.registry.nucleus/runMigration=1",
                "--/exts/omni.kit.registry.nucleus/resetLocalIndexCache=1", # we cached previous version locally, need to reset to the clean state
                "--/exts/omni.kit.registry.nucleus/defautIndexVersion='v2'",
            ]
        )

        self.assertEqual(len(glob.glob(f"{test.registry_dir}/v2/registry.gz", recursive=True)), 1)
        os.remove(f"{test.registry_dir}/3/index.zip")

        # pull extension
        shutil.rmtree(test.install_dir)
        await self._test_ext_can_be_pulled("omni.blob-2.0.0", test)


    async def test_parallel_publish(self):
        extra_args = [
            "--/exts/omni.kit.registry.nucleus/parallelPublish=1",
            "--/app/extensions/removeGeneratedConfigAfterPublish=0",
        ]
        test = RegistryTestBoilerplate(self._temp_folder, extra_args=extra_args)

        EXT_IDS = [
            "omni.wide-3.2.3",
            "omni.wide-0.1.0",
            "omni.wide-2.0.0",
            "omni.narrow-1.0.3",
            "omni.narrow-2.0.0",
        ]

        for ext_id in EXT_IDS:
            build_extension(test.exts_dir, ext_id)

        # run kit to batch publish in one go
        await self._run_kit_to_batch_publish(EXT_IDS, test)

        # pull extension
        await self._test_ext_can_be_pulled(EXT_IDS, test)
