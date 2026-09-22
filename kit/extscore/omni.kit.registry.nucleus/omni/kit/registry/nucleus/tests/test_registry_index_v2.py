import tempfile
import shutil
import os
import omni.kit.test
import omni.kit.registry.nucleus
import json
import carb.dictionary


class TestRegistryIndexV2(omni.kit.test.AsyncTestCase):
    async def test_sync_task(self):
        from omni.kit.registry.nucleus.registry_manager import get_registry_manager_instance
        from omni.kit.registry.nucleus.index_v2.index_sync import IndexSync

        registry_globals = get_registry_manager_instance()._registry_globals

        # simulate local and remote registry and sync
        local_root1 = f"{self._temp_folder}/local1"
        local_root2 = f"{self._temp_folder}/local2"
        remote_root = f"{self._temp_folder}/remote"
        os.makedirs(local_root1, exist_ok=True)
        os.makedirs(local_root2, exist_ok=True)

        def build_ext_dict(name):
            return {
                "package": { "name": name, "foo": "123" },
                "dependencies": {
                    "omni.kit.core": { "version": "1.0.0" },
                }
            }

        sync = IndexSync(local_root1, remote_root, registry_globals)
        sync.wait()
        sync.apply_change("omni.cat-1.2.3", build_ext_dict("omni.cat"), True)
        sync.apply_change("omni.cat-0.0.1", build_ext_dict("omni.cat"), True)
        sync.apply_change("omni.dog-1.2.3", build_ext_dict("omni.dog"), True)
        sync.push_changes()

        sync = IndexSync(local_root2, remote_root, registry_globals)
        sync.wait()
        sync.apply_change("omni.cat-2.0.0", build_ext_dict("omni.cat"), True)
        sync.apply_change("omni.cat-1.2.3", None, False)
        sync.apply_change("omni.parrot-1.0.0", build_ext_dict("omni.parrot"), True)
        sync.push_changes()

        sync = IndexSync(local_root1, remote_root, registry_globals)
        sync.wait()

        def check_package(path, versions_to_check, exist=True):
            self.assertEqual(os.path.exists(f"{local_root1}/{path}"), exist)
            if exist:
                versions = set()
                with open(f"{local_root1}/{path}", "r") as f:
                    for line in f:
                        if line.strip():
                            versions.add(line.split(" ")[0])

            self.assertEqual(versions, versions_to_check)

        check_package("packages/omni.cat.json", {"omni.cat-0.0.1", "omni.cat-2.0.0"})
        check_package("packages/omni.parrot.json", {"omni.parrot-1.0.0"})
        check_package("packages/omni.dog.json", {"omni.dog-1.2.3"})

        def check_summaries(keys_to_check):
            with open(f"{local_root1}/summaries.json", "r") as f:
                data = json.loads(f.read())
            self.assertEqual(set(data.keys()), keys_to_check)

        check_summaries({"omni.cat-2.0.0", "omni.parrot-1.0.0", "omni.dog-1.2.3"})


    async def setUp(self):
        self._temp_folder = tempfile.mkdtemp()

    async def tearDown(self):
        shutil.rmtree(self._temp_folder)
