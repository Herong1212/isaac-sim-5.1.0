# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import shutil
import threading
from datetime import datetime

import carb.tokens
import omni.ext

from .utils.threadsafe_open import ThreadsafeOpen
from .utils.common import _error, _get_setting, _info, _print, _print_mt, _warn, sha1_str, rmpath, dir_has_any_files

CACHE_DB_KEY_LAST_PRUNE_DATE = "last_prune_date"
CACHE_DB_KEY_LINKS_SINCE_LAST_PRUNE = "links_since_last_prune"
CACHE_DB_KEY_LINKS = "links"


def dir_has_extension_config(path: str) -> bool:
    """Check if the folder has extension.toml file in expected locations."""
    for p in ["extension.toml", "config/extension.toml"]:
        if os.path.exists(os.path.join(path, p)):
            return True
    return False


def is_cached_extension_valid(ext_path):
    # In the future we can add some proper hash verification.
    # For now at least check that there are any files in the folder. (not just empty folders, which can happen)
    if not dir_has_any_files(ext_path):
        return False

    # Another sanity check if the extension config exist. There can be situation when during the remove, one of binary
    # files was locked by other process. While extenson config would be removed (no lock). That would catch that case.
    if not dir_has_extension_config(ext_path):
        return False

    return True


class GlobalExtCache:
    def __init__(self):
        # Build cache path with registry version
        self._cache_path = _get_setting("/exts/omni.kit.registry.nucleus/cachePath", None)
        self._cache_path = carb.tokens.get_tokens_interface().resolve(self._cache_path)
        self._make_sure_cache_json_does_not_exist(self._cache_path)
        versionSubdir = _get_setting("/exts/omni.kit.registry.nucleus/cacheVersionSubdir", "")
        if versionSubdir:
            self._cache_path += f"/{versionSubdir}"
        os.makedirs(self._cache_path, exist_ok=True)

        # cache db to store created folder links to be able to cleanup the cache
        self.cache_db_file = self._cache_path + "/cache_db.json"
        self.cache_db_lock = threading.Lock()

        # generic files cache (urls)
        self._urls_cache_path = self._cache_path + "/urls"
        os.makedirs(self._urls_cache_path, exist_ok=True)
        self._urls_cache_enabled = _get_setting("/exts/omni.kit.registry.nucleus/cacheFiles", True)

        # index (v2) cache dir
        self._index_cache_path = self._cache_path + "/index"
        os.makedirs(self._index_cache_path, exist_ok=True)

        self._create_links = _get_setting("/exts/omni.kit.registry.nucleus/cacheCreateLinks", True)
        self._prune_enabled = _get_setting("/exts/omni.kit.registry.nucleus/cachePrune/enabled", True)
        self._prune_every_n_installs = _get_setting(
            "/exts/omni.kit.registry.nucleus/cachePrune/runEveryNInstalls", 1000
        )
        self._prune_every_n_days = _get_setting("/exts/omni.kit.registry.nucleus/cachePrune/runEveryNDays", 7)
        self._remove_older_than_n_days = _get_setting(
            "/exts/omni.kit.registry.nucleus/cachePrune/removeOlderThanNDays", 7
        )
        self._pruned_this_run = False

        self._omit_ext_version = _get_setting("/exts/omni.kit.registry.nucleus/omitExtVersion", False)

        _info(f"global cache path: {self._cache_path}")

        # a way to explicitly run prunning if we want to make a tool (shell script)
        if _get_setting("/exts/omni.kit.registry.nucleus/cachePrune/runOnStartup", False):
            self._prune_cache()

    def _make_sure_cache_json_does_not_exist(self, path):
        # Do not 'Announce' this path to the Omniverse Cache Cleaner (OM-78048). We will make our own smarter cache cleaner in the future.
        cache_json = path + "/_cache.json"
        if os.path.exists(cache_json):
            os.remove(cache_json)

    def get_cache_path(self):
        return self._cache_path

    def get_ext_cache_path(self, archive_name: str):
        # Folder or kit file?
        path = f"{self._cache_path}/{archive_name}"
        if os.path.exists(path):
            if not is_cached_extension_valid(path):
                _warn(f"Folder is in the cache, but empty or corrupted: '{path}'. Invalidating cache...")
                rmpath(path)
                return None
            return path
        path += ".kit"
        if os.path.exists(path):
            return path
        return None

    def _get_url_path_in_cache(self, url: str) -> str:
        return f"{self._urls_cache_path}/{sha1_str(url)}"

    def get_file_cache_path(self, url: str) -> str:
        if not self._urls_cache_enabled:
            return None
        path = self._get_url_path_in_cache(url)
        if os.path.exists(path):
            return path
        return None

    def get_index_cache_path(self) -> str:
        return self._index_cache_path

    def cache_file(self, filepath, url: str):
        if not self._urls_cache_enabled:
            return
        cache_path = self._get_url_path_in_cache(url)
        shutil.copy(filepath, cache_path)

    def install(self, exts_cache_path: str, ext_folder: str, ext_id: str):
        if os.path.isdir(exts_cache_path):
            ext_basename = omni.ext.get_extension_name(ext_id) if self._omit_ext_version else ext_id
            ext_path = f"{ext_folder}/{ext_basename}"

            if os.path.exists(ext_path) and self._omit_ext_version:
                link_dst = os.path.realpath(ext_path)
                _error(
                    f"Extension installation failed: '{ext_path}' (link to: {link_dst}) already exists and omitExtVersion is set to True. Can't have different versions installed at the same location. Please remove the old version first."
                )
                return False

            if self._create_links:
                _print_mt(f"creating a link: {ext_path} -> {exts_cache_path}")
                omni.ext.create_link(ext_path, exts_cache_path)
            else:
                _print_mt(f"copy extension from cache: {exts_cache_path} -> {ext_path}")
                shutil.copytree(exts_cache_path, ext_path)
            self._add_link_to_cache_db(exts_cache_path, ext_path)
        else:
            _print_mt(f"copying single file extension: {exts_cache_path} -> {ext_folder}")
            shutil.copy2(exts_cache_path, ext_folder)
            ext_path = f"{ext_folder}/{os.path.basename(exts_cache_path)}"
            self._add_link_to_cache_db(exts_cache_path, ext_path)

        return True

    def invalidate(self, ext_id: str):
        _info(f"global cache invalidate: {ext_id}")
        exts_cache_path = self.get_ext_cache_path(ext_id)
        if exts_cache_path and os.path.exists(exts_cache_path):
            rmpath(exts_cache_path)

    def destroy(self):
        pass

    def _add_link_to_cache_db(self, cache_path: str, ext_path: str):
        """Add a link to the cache db. This is used to cleanup the cache later on.

        We store each link from the cached extension to the installation. Once in awhile we run prunning to remove the
          cached extensions that are not linked anymore.
        """
        import json

        # We have file lock for multiprocesses, but if we are inside of the same process it is faster to just use a lock
        # It happens when we are installing multiple extensions at the same time
        with self.cache_db_lock:
            ext_id = os.path.basename(cache_path)
            ext_path = os.path.normpath(ext_path)

            links_since_last_prune = 0
            last_prune_date = datetime.min

            # init with empty db
            if not os.path.exists(self.cache_db_file):
                with ThreadsafeOpen(self.cache_db_file, "w") as f:
                    f.seek(0)
                    f.write(json.dumps({}, indent=4))
                    f.truncate()

            # read and write at one go
            with ThreadsafeOpen(self.cache_db_file, "r+") as f:
                content = f.read()
                try:
                    data = json.loads(content) if content else {}
                except json.JSONDecodeError as e:
                    _error(f"Resetting cache db. Failed to parse it: {e}.")
                    data = {}

                # increment counter
                links_since_last_prune = data.get(CACHE_DB_KEY_LINKS_SINCE_LAST_PRUNE, 0)
                links_since_last_prune += 1
                data[CACHE_DB_KEY_LINKS_SINCE_LAST_PRUNE] = links_since_last_prune

                # last prune date
                last_prune_date_str = data.get(CACHE_DB_KEY_LAST_PRUNE_DATE, "")
                if last_prune_date_str:
                    last_prune_date = datetime.fromisoformat(last_prune_date_str)

                # add link
                links = data.setdefault(CACHE_DB_KEY_LINKS, {})
                paths = links.setdefault(ext_id, [])
                if ext_path not in paths:
                    paths.append(ext_path)
                f.seek(0)
                f.write(json.dumps(data, indent=4))
                f.truncate()

            # run prune every N installs or N days
            if self._prune_enabled:
                if links_since_last_prune > self._prune_every_n_installs:
                    self._prune_cache()
                elif (datetime.now() - last_prune_date).days >= self._prune_every_n_days:
                    self._prune_cache()

    def _prune_cache(self):
        import json

        # Allow only once per run (process), just in case. That should not usually happen, unlikely to have more than
        # 1000 extensions installed in one run.
        if self._pruned_this_run:
            return
        self._pruned_this_run = True

        cache_root = os.path.dirname(self.cache_db_file)
        _print(f"pruning global extensions cache: {cache_root}")

        if not os.path.exists(self.cache_db_file):
            _warn(f"cache db file does not exist: {self.cache_db_file}")
            return

        links_removed = 0
        exts_removed = 0

        date_now = datetime.now()

        # read and write at one go
        with ThreadsafeOpen(self.cache_db_file, "r+") as f:
            data = json.loads(f.read())

            links = data.get(CACHE_DB_KEY_LINKS, {})
            ext_id_to_remove = []
            for ext_id, paths in links.items():
                cache_path = f"{cache_root}/{ext_id}"

                # Remove all links that doesn't exist anymore
                for i in range(len(paths) - 1, -1, -1):
                    if not os.path.exists(paths[i]):
                        _info(f"link does not exist: {paths[i]} -> {cache_path}")
                        del paths[i]
                        links_removed += 1

                # If no links left, remove the extension from cache
                if len(paths) == 0:
                    if os.path.exists(cache_path):
                        mtime = os.stat(cache_path).st_mtime
                        if (date_now - datetime.fromtimestamp(mtime)).days >= self._remove_older_than_n_days:
                            _info(
                                f"removing cached extension (older than {self._remove_older_than_n_days} days and no links pointing to it): {cache_path}"
                            )
                            if rmpath(cache_path, log_errors=False):
                                ext_id_to_remove.append(ext_id)
                        else:
                            _info(
                                f"cached extension is not used, but not older than {self._remove_older_than_n_days} days, keeping: {cache_path}"
                            )
                    else:
                        _info(f"cached extension not found, skipping: {cache_path}")
                        ext_id_to_remove.append(ext_id)

            # Remove keys separately to avoid changing the dict while iterating
            for ext_id in ext_id_to_remove:
                del links[ext_id]
                exts_removed += 1

            # reset counter and date
            data[CACHE_DB_KEY_LINKS_SINCE_LAST_PRUNE] = 0
            data[CACHE_DB_KEY_LAST_PRUNE_DATE] = date_now.isoformat()

            # update db
            f.seek(0)
            f.write(json.dumps(data, indent=4))
            f.truncate()

        _print(f"global extensions cache pruned: {links_removed} links removed, {exts_removed} extensions removed")
