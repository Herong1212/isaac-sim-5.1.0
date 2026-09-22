from functools import lru_cache
import re
import time
import logging
import fnmatch
import argparse
import asyncio
import json
import sys

import carb
import carb.settings
import omni.kit.app
import omni.kit.registry.nucleus
import omni.ext

from omni.kit.registry.nucleus import PublishResult

logger = logging.getLogger(__name__)


class DumpStats:
    def __init__(self, path):
        self.exts = {}
        self.path = path

    def save(self):
        if self.path:
            with open(self.path, "w") as f:
                json.dump(self.exts, f)
            logger.info(f"Saved dump to: {self.path}")

    def add_result(self, ext):
        ext_name = ext["name"]
        ext_id = ext["id"]
        ext_version = ext["version"][:3]
        ext_version = ".".join(str(v) for v in ext_version)
        self.exts[ext_name] = {"id": ext_id, "version": ext_version}


class PublishStats:
    def __init__(self):
        self._exts = {}

    @staticmethod
    def load(path: str):
        s = PublishStats()
        try:
            if path:
                with open(path, "r") as f:
                    d = json.load(f)
                    print(f"Loaded stats from: {path}")
                    s._exts = d["_exts"]
        except:
            pass
        return s

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.__dict__, f)
            logger.info(f"Saved stats to: {path}")

    def add_result(self, ext_id, res: PublishResult):
        if ext_id in self._exts and res == PublishResult.SKIP:
            return
        self._exts[ext_id] = res

    def fail_all(self):
        for ext_id in self._exts:
            if not self._exts[ext_id] == PublishResult.SKIP:
                self._exts[ext_id] = PublishResult.FAIL


@lru_cache()
def get_default_publish_registry_url():
    settings = carb.settings.get_settings()
    registry_default = settings.get("app/extensions/registryPublishDefault")
    settings_dict = carb.settings.get_settings().get_settings_dictionary("")
    registries = settings_dict.get("exts/omni.kit.registry.nucleus/registries", [])
    for r in registries:
        if registry_default == r.get("name", ""):
            return r.get("url", None)


def publish_exts(options) -> bool:
    logger.info(f"publish_exts options: {options}")

    def matches(ext_id: str):
        return any(fnmatch.fnmatch(ext_id, p) for p in options.include) and not any(
            fnmatch.fnmatch(ext_id, p) for p in options.exclude
        )

    # We sync registry once here, then do all the changes and sync index again in the end. (Uploading index is slow)
    manager = omni.kit.app.get_app().get_extension_manager()
    if not options.verify:
        manager.sync_registry()
    omni.kit.registry.nucleus.start_index_changes_batching()

    # stats
    all_good = True
    stats = PublishStats.load(options.stats_file)
    dump = DumpStats(options.dump)

    # verification
    settings = carb.settings.get_settings()
    publish_verification = not bool(settings.get("/app/extensions/skipPublishVerification"))

    is_parallel_publish = bool(settings.get("/exts/omni.kit.registry.nucleus/parallelPublish"))

    for ext in manager.get_extensions():
        ext_id = ext["id"]

        if not matches(ext_id) and not matches(ext["name"]):
            continue

        logger.info(f"publish ext: '{ext_id}'")

        # Skip core extensions
        info = manager.get_extension_dict(ext_id)
        if info.get("isCore", False):
            print(f"skip ext: '{ext_id}' because it is core extension")
            continue

        if options.exclude_apps and info.get("isKitFile", False):
            print(f"skip ext: '{ext_id}' because it is app and --exclude-apps is set")
            continue

        if options.dump:
            dump.add_result(ext)
            continue

        info = manager.get_extension_dict(ext_id)
        package_id = info["package/packageId"]

        ext_remote = manager.get_registry_extension_dict(package_id)
        res = True
        is_skip = ext_remote and ext_remote["package/packageId"] == package_id
        if is_skip:
            print(f"ext: '{ext_id}' package: '{package_id}' is already on remote, skipping..")
            stats.add_result(package_id, PublishResult.SKIP)
        else:
            # Do verification early to allow for --verify option (it works without syncing with registry)
            if publish_verification:
                res, changelog = omni.kit.registry.nucleus.verify_extension_for_publishing(info)
                res_message = "OK" if res else "FAIL"
                print(f"ext: '{ext_id}' verification result: {res_message}")

            if not res or options.verify:
                # Either verification failed or we are in verify only mode, we are done here, add result
                stats.add_result(package_id, PublishResult.OK if res else PublishResult.FAIL)
            else:
                # Verification passed (or disabled), we can publish
                if options.dry_run:
                    print(f"pretending to publish ext: '{ext_id}' in dry run...")
                    res = True
                else:
                    print(f"publishing ext: '{ext_id}'...")
                    time_start = time.monotonic()
                    res = manager.publish_extension(ext_id)
                    print("publish_extension returned: {}, took: {:.2f}".format(res, time.monotonic() - time_start))

                    if not res:
                        logger.error(f"failed to publish ext: '{ext_id}'")
                        stats.add_result(package_id, PublishResult.FAIL)
                    else:
                        if not is_parallel_publish:
                            print(f"ext: '{ext_id}' was published successfully.")
                        stats.add_result(package_id, PublishResult.OK)

        all_good &= res

    # Stop batching index change and apply all of them
    index_change_res = omni.kit.registry.nucleus.apply_index_changes_batch()

    # Get publish results from registry through API (parallel publish should be done at this point)
    publish_results = omni.kit.registry.nucleus.get_publish_results()
    for ext_id, result in publish_results.items():
        stats.add_result(ext_id, result)

    if not index_change_res:
        all_good = False
        stats.fail_all()

    if options.stats_file:
        stats.save(options.stats_file)
    if options.dump:
        dump.save()

    omni.kit.app.get_app().post_quit(0 if all_good else -3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--include",
        action="append",
        dest="include",
        default=[],
        help="Only write stub files for python modules in those path wilcards.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        dest="exclude",
        default=[],
        help="Exclude those path wildcards from generating stubs.",
    )
    parser.add_argument(
        "-n",
        "--dry",
        dest="dry_run",
        required=False,
        action="store_true",
        help="Dry run.",
    )
    parser.add_argument(
        "--stats-file",
        dest="stats_file",
        default=[],
        help="File to load and save stats too.",
    )
    parser.add_argument(
        "--exclude-apps",
        dest="exclude_apps",
        required=False,
        action="store_true",
        help="Do not publish apps (kit files).",
    )
    parser.add_argument(
        "--verify",
        dest="verify",
        required=False,
        action="store_true",
        help="Only do publishing verification, without actually publishing.",
    )
    parser.add_argument(
        "--dump",
        dest="dump",
        nargs="?",
        const="_PUBLISH_EXTS.json",
        help="Dump extension versions into a file",
    )

    options = parser.parse_args()
    publish_exts(options)
