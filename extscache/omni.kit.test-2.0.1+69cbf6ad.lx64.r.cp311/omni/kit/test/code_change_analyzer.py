import json
import os

import omni.kit.app

import logging
from typing import List


from .repo_test_context import RepoTestContext
from .utils import sha1_path, sha1_list, get_global_test_output_path


logger = logging.getLogger(__name__)

KNOWN_EXT_SOURCE_PATH = ["kit/source/extensions/", "source/extensions/"]

# We know for sure that this hash changes all the time and used in many many tests, don't want it to mess with our logic for now
STARTUP_SEQUENCE_EXCLUDE = ["omni.rtx.shadercache.d3d12", "omni.rtx.shadercache.vulkan"]


def _get_extension_hash(package_id, path):
    path = os.path.normpath(path)

    hash_cache_file = f"{get_global_test_output_path()}/exts_hashes/{package_id}.txt"

    ext_hash = None

    # cache hash calculation in a file to speed up things (it's slow)
    try:
        with open(hash_cache_file, "r") as f:
            ext_hash = f.read()
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warn(f"Failed to load extension hashes from {hash_cache_file}, error: {e}")

    if ext_hash:
        return ext_hash

    ext_hash = sha1_path(path)

    os.makedirs(os.path.dirname(hash_cache_file), exist_ok=True)
    with open(hash_cache_file, "w") as f:
        f.write(ext_hash)

    return ext_hash


def _get_extension_name_for_file(file):
    for path in KNOWN_EXT_SOURCE_PATH:
        if file.startswith(path):
            ext = file[len(path) :].split("/")[0]
            return ext
    return None


def _print(str, *argv):
    print(f"[omni.kit.test.code_change_analyzer] {str}", *argv)


class ChangeAnalyzerResult:
    def __init__(self):
        self.should_skip_test = False
        self.startup_sequence = []
        self.startup_sequence_hash = ""
        self.tested_ext_hash = ""
        self.kernel_version = ""


class CodeChangeAnalyzer:
    """repo_test can provide (if in MR and on TC) with a list of changed files using env var.
    Check if changed ONLY extensions. If any change is not in `source/extensions` -> run all tests
    If changed ONLY extensions than for each test solve list of ALL enabled extensions and check against that list.
    """

    def __init__(self, repo_test_context: RepoTestContext):
        self._allow_sampling = True
        self._allow_skipping = False
        self._changed_extensions = self._gather_changed_extensions(repo_test_context)

    def _gather_changed_extensions(self, repo_test_context: RepoTestContext):
        data = repo_test_context.get()
        if data:
            changed_files = data.get("changed_files", [])
            if changed_files:
                self._allow_skipping = True
                changed_extensions = set()
                for file in changed_files:
                    ext = _get_extension_name_for_file(file)
                    if ext:
                        logger.info(f"Changed path: {file} is an extension: {ext}")
                        changed_extensions.add(ext)
                    elif self._allow_skipping:
                        _print("All tests will run. At least one changed file is not in an extension:", file)
                        self._allow_skipping = False
                        self._allow_sampling = False

                if self._allow_skipping:
                    ext_list_str = "\n".join(("\t - " + e for e in changed_extensions))
                    _print(f"Only tests that use those extensions will run. Changed extensions:\n{ext_list_str}")
                return changed_extensions

        logger.info("No changed files provided")
        return set()

    def get_changed_extensions(self) -> List[str]:
        return list(self._changed_extensions)

    def allow_sampling(self) -> bool:
        return self._allow_sampling

    def _build_startup_sequence(self, result: ChangeAnalyzerResult, ext_name: str, exts: List):
        result.kernel_version = omni.kit.app.get_app().get_kernel_version()
        result.startup_sequence = [("kernel", result.kernel_version)]
        for ext in exts:
            if ext["name"] in STARTUP_SEQUENCE_EXCLUDE:
                continue
            path = ext.get("path", None)
            package_id = ext["package_id"]
            if path:
                hash = _get_extension_hash(package_id, path)
                result.startup_sequence.append((ext["name"], hash))
                if ext["name"] == ext_name:
                    result.tested_ext_hash = hash

        # Hash whole startup sequence
        result.startup_sequence_hash = sha1_list([hash for ext, hash in result.startup_sequence])

    def analyze(self, test_id: str, ext_name: str, exts_to_enable: List[str]) -> ChangeAnalyzerResult:
        result = ChangeAnalyzerResult()
        result.should_skip_test = False

        # Ask manager for extension startup sequence
        manager = omni.kit.app.get_app().get_extension_manager()
        solve_result, exts, err = manager.solve_extensions(
            exts_to_enable, add_enabled=False, return_only_disabled=False
        )
        if not solve_result:
            logger.warn(f"Failed to solve dependencies for extension(s): {exts_to_enable}, error: {err}")
            return result

        # Build hashes for a startup sequence
        self._build_startup_sequence(result, ext_name, exts)

        if not self._allow_skipping:
            return result

        if not self._changed_extensions:
            return result

        for ext in exts:
            if ext["name"] in self._changed_extensions:
                _print(f"{test_id} test will run because it uses the changed extension:", ext["name"])
                self._allow_sampling = False
                return result

        _print(
            f"{test_id} skipped by code change analyzer. Extensions enabled in this tests were not changed in this MR."
        )
        result.should_skip_test = True
        return result
