# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["RegistryProvider"]

import asyncio
import threading
import os
import json
import time
import tempfile
import concurrent.futures
import traceback

from typing import List, Tuple
from urllib import request

import carb.dictionary
import carb.settings
import carb.tokens
import omni.kit.app
import omni.ext
import omni.client

from omni.client import CopyBehavior

from .utils.common import (
    _info,
    _print,
    _print_mt,
    _error,
    _warn,
    _get_setting,
    sha1_folder,
    info_exec_time,
    remove_authors_from_extension,
    zip_extension,
    get_dict_value_by_path,
    md5_file,
    get_ext_fullname_version,
)
from .utils.semver import SemanticVersion
from .utils.omni_client_utils import (
    omni_client_copy,
    omni_client_copy_async,
    omni_client_exists,
    omni_client_try_delete,
    upload_file,
)
from .utils.packman_utils import resolve_packman_url, push_to_packman
from .utils.http_utils import post_publish_extension_request, post_unpublish_extension_request
from .verification import verify_and_get_package_id_for_publishing, verify_extension_for_publishing
from .registry_globals import RegistryGlobals, PublishResult
from .iregistry_index import IRegistryIndex, RegistryURLs
from .index_v1.index import RegistryIndexV1
from .index_v2.index import RegistryIndexV2
from .migration import migrate_v1_to_v2, migrate_v2_to_v1


SERIALIZER_OPTION_MAKE_PRETTY = 1 << 1

INDEX_KEYS_TO_WRITE_TO_GENERATED_CONFIG_ON_DOWNLOAD = [
    "package/trusted",
    "package/archiveSubdir",
    "package/archivePath",
    "package/authors",
    "package/repository",
    "package/githubRelease",
    "package/publish/date",
    "package/publish/buildNumber",
]

# In the future can be changed to be all: "package/target/*". Those matter only when content as a hash package is used
# (and this package shared between different targets on the same host).
INDEX_KEYS_TO_WRITE_TO_GENERATED_CONFIG_ON_INSTALL = [
    "package/target/kitHash",
    "package/target/platform",
    "package/target/config",
    "package/target/python",
]


class CorruptedCacheError(Exception):
    """
    Raise this exception if cache is corrupted and needs to be cleared.
    """


class RegistryProvider(omni.ext.IRegistryProvider):
    """Registry provider implementation.

    There is one instance of this class per registry URL in settings. It registers itself in the extension manager.
    Extension manager will call this class to get the list of extensions and to download extensions, etc.
    """

    def __init__(self, name: str, url: str, trusted: bool, optional: bool, registry_globals: RegistryGlobals):
        omni.ext.IRegistryProvider.__init__(self)

        # Globals
        self._globals = registry_globals

        # Provider name
        self._name = name

        self._index_url = url

        self._optional = optional

        # Nucleus or http registry? Important when doing publishing, if we should use endpoint
        self._is_http = omni.client.break_url(self._index_url).scheme in ("http", "https")

        self._trusted = trusted

        self._post_to_slack = _get_setting("/exts/omni.kit.registry.nucleus/postToSlack", True)

        # Migration
        self._run_migration = _get_setting("/exts/omni.kit.registry.nucleus/runMigration", True)

        self._use_urllib_for_http = _get_setting("/exts/omni.kit.registry.nucleus/useUrllibForHttp", True)
        if self._use_urllib_for_http:
            self._info(f"enabled using request.urlretrieve to download from http")

        # Try both http and https if one fails
        self._try_both_http_and_https = _get_setting("/exts/omni.kit.registry.nucleus/tryBothHttpAndHttps", True)

        # Cache invalidation on pull
        self._cache_invalidate_on_pull = _get_setting("/exts/omni.kit.registry.nucleus/cacheInvalidateOnPull", False)

        # Use parallel publish (multithreaded)
        self._parallel_publish = _get_setting("/exts/omni.kit.registry.nucleus/parallelPublish", False)
        self._parallel_publish_tasks = {}

        # register into ext manager:
        self._ext_manager = omni.kit.app.get_app().get_extension_manager()
        self._ext_manager.add_registry_provider(name, self)

        # Ongoing extension pull tasks
        self._pull_tasks = {}

        # Index implementations. First takes precedence.
        self._index_impls = [
            RegistryIndexV2(name, url, optional, registry_globals),
            RegistryIndexV1(name, url, optional, registry_globals),
        ]
        if _get_setting("/exts/omni.kit.registry.nucleus/defautIndexVersion", "v2") != "v2":
            self._index_impls.reverse()

        # store results of various index impls during refreshing
        self._refresh_results = {}

        # by default that will set read account if specified. Later if publish happens it will be switched off.
        self._auth_manager = self._globals.get_auth_manager(url)


    def _info(self, message):
        _info(f"[{self._name}] {message}")

    def _warn(self, message):
        _warn(f"[{self._name}] {message}")

    def _error(self, message):
        _error(f"[{self._name}] {message}")

    def shutdown(self):
        self._ext_manager.remove_registry_provider(self._name)
        for impl in self._index_impls:
            impl.shutdown()

    def get_urls(self) -> RegistryURLs:
        if len(self._index_impls) != 1:
            # Can't get urls if we have not selected index implementation
            return None
        return self._get_selected_index_impl().get_urls()

    def refresh_index(self):
        # if results are empty that means this is the first refresh call and we are starting refreshing
        if not self._refresh_results:
            for impl in self._index_impls:
                self._refresh_results[impl] = omni.ext.DownloadState.DOWNLOADING

        all_failed = True
        any_success = False
        any_downloading = False

        for impl, state  in self._refresh_results.items():
            # call only index impls that have not yet completed
            if state is None or state == omni.ext.DownloadState.DOWNLOADING:
                state = impl.refresh_index()

            if state != omni.ext.DownloadState.DOWNLOAD_FAILURE:
                all_failed = False
            if state == omni.ext.DownloadState.DOWNLOAD_SUCCESS:
                any_success = True
            if state == omni.ext.DownloadState.DOWNLOADING:
                any_downloading = True
            self._refresh_results[impl] = state

        if any_downloading:
            return omni.ext.DownloadState.DOWNLOADING

        # if we get there all index impls have completed refreshing, can reset the results for the future refresh sequence
        self._refresh_results = {}

        if all_failed:
            # Don't report failure if optional (we will return empty dict anyway)
            if self._optional:
                return omni.ext.DownloadState.DOWNLOAD_SUCCESS

            return omni.ext.DownloadState.DOWNLOAD_FAILURE
        elif any_success:
            return omni.ext.DownloadState.DOWNLOAD_SUCCESS
        return omni.ext.DownloadState.DOWNLOADING

    def sync_index(self):
        self._info("sync_index called.")
        return self._sync_index(resync=False)

    def _sync_index(self, resync=False):
        selected_impl = None
        for impl in self._index_impls:
            index, index_is_new = impl.sync_index(resync=resync)

            # peek first
            if not selected_impl:
                selected_impl = impl

            # in migration mode just sync both
            if self._run_migration:
                continue

            # Unless there was a NOT new later, then prefer it
            # This is the critical line that saves us from loading slow v1 index if v2 is available. v1 index task
            # might still be running, but we just about to cancel it and select v2 instead.
            if not index_is_new:
                selected_impl = impl
                break

        # check if we in run migration mode (we need both impls)
        self._check_run_migration()

        # shutdown all other impls, keep only selected one
        for impl in self._index_impls:
            if impl != selected_impl:
                impl.shutdown()
        self._index_impls = [selected_impl]
        self._info(f"selected index version implementation: {selected_impl.__class__.__name__}")

        return selected_impl.get_index_dict() or self._globals.empty_index

    def _check_run_migration(self):
        # Migration depends on which registry version is selected as "defautIndexVersion". Migrate from the other to
        # the current. E.g. if it is v2, then migrate from v1 to v2.
        if self._run_migration:
            from .registry_manager import start_index_changes_batching, apply_index_changes_batch

            start_index_changes_batching()

            if type(self._index_impls[0]) == RegistryIndexV2:
                migrate_v1_to_v2(self._index_impls[1], self._index_impls[0])
            else:
                migrate_v2_to_v1(self._index_impls[1], self._index_impls[0])

            apply_index_changes_batch()

            _print("[migration] Done. Exiting...")
            omni.kit.app.get_app().post_quit(0)

    def apply_index_changes_batch(self):
        self._info("apply_index_changes_batch called.")

        # check and wait for all publish tasks completed
        publish_tasks_cnt = len(self._parallel_publish_tasks)
        if publish_tasks_cnt:
            _print(f"Waiting for {publish_tasks_cnt} parallel publish tasks to complete...")
        while any(not task.done() for task, _ in self._parallel_publish_tasks.values()):
            self._info("Waiting for parallel publish tasks to complete...")
            time.sleep(0.5)
        if publish_tasks_cnt:
            _print("All parallel publish tasks completed.")

        # Check for any errors in async publish tasks. Here we made a decision to not update index at all if 
        # any of the parallel publish tasks failed. That is different from serial publish where we would still
        # publish some. We probably should change serial publish to fail too, but don't want to change previous behavior.
        # Failing everything will help to avoid partial extension publish, when some extensions are published and some not.
        any_failed = False
        for ext_id, (task, _) in self._parallel_publish_tasks.items():
            if task.done() and not task.result():
                self._error(f"Failed to parallel publish extension: {ext_id}.")
                any_failed = True
        self._parallel_publish_tasks.clear()
        if any_failed:
            return False

        for impl in self._index_impls:
            res = impl.apply_index_changes_batch()
            if not res:
                return False
        return True

    def _build_archive_name(self, ext_id: str, ext_path: str, ext_dict: dict) -> Tuple[str, bool]:
        # Optionally use hash for version part of archive name. If nothing changed since last published package it will
        # be reused.
        archive_name = ext_id
        overwrite = True
        use_hash = _get_setting("/exts/omni.kit.registry.nucleus/useContentHashAsArchiveName", False)
        if use_hash:
            #
            overwrite = False

            ext_name = ext_dict.get("package", {}).get("name", "")
            # Exclude generated config from hashing. Otherwise just changing kit or date of publishing produces
            # a different package. We don't want that, we only want to publish when actual content (code) changed.
            hash = sha1_folder(ext_path, exclude_files=["extension.gen.toml"])
            archive_name = f"{ext_name}-{hash}"

        return archive_name, overwrite

    def _zip_extension_to_archive(self, archive_name: str, ext_path: str, tmp_dir: str) -> str:
        # Postprocessing just before zipping, but after calculating a hash.
        if _get_setting("/exts/omni.kit.registry.nucleus/removeAuthorsFromConfig", False):
            remove_authors_from_extension(ext_path)

        archive_local = zip_extension(archive_name, ext_path, tmp_dir)
        return archive_local

    def _upload_archive(self, ext_id: str, ext_path: str, ext_dict: dict, tmp_dir: str) -> Tuple[bool, str, str]:
        """Upload archive to the remote.

        archive_remote: can be None if it can't be uploaded (e.g. for http registry).

        Returns:
            Tuple[bool, str, str]: (success, archive_local, archive_remote)
        """

        index_impl = self._get_selected_index_impl()
        urls = index_impl.get_urls()

        overwrite = True

        # Path to archive can already be specified through settings. Otherwise zip and upload local copy
        package_dict = ext_dict.setdefault("package", {})
        archive_remote = package_dict.get("archivePath", "")
        if archive_remote:
            return True, None, archive_remote

        archive_name, overwrite = self._build_archive_name(ext_id, ext_path, ext_dict)

        archive_local = None

        # Use packman or push to the same remote where index is
        use_packman = _get_setting("/exts/omni.kit.registry.nucleus/usePackmanToUploadArchives", False)
        if use_packman:
            # Try resolve first, package might already be uploaded. No need to even zip then:
            archive_path = resolve_packman_url(archive_name + ".zip")
            if archive_path:
                _info(f"packman package already exist, url: {archive_path}")
                self._globals.set_publish_results(ext_id, PublishResult.OK_EXISTS)
            else:
                # zip
                archive_local = self._zip_extension_to_archive(archive_name, ext_path, tmp_dir)

                archive_path = push_to_packman(archive_local)
                if not archive_path:
                    self._globals.set_publish_results(ext_id, PublishResult.FAIL)
                    return False, archive_local, None
                self._globals.set_publish_results(ext_id, PublishResult.OK)

            archive_remote = archive_path
        else:
            # zip
            archive_local = self._zip_extension_to_archive(archive_name, ext_path, tmp_dir)

            # Stop there for http, we will post archive as part of publish request
            if self._is_http:
                return True, archive_local, None

            # build path for data and archive to upload
            ext_name = package_dict.get("name", "")
            archive_remote = f"{urls.archives}/{ext_name}/{archive_name}.zip"
            archive_path = omni.client.make_relative_url(urls.index_file, archive_remote)
            archive_path.replace("\\", "/")
            if not upload_file(archive_local, archive_remote, overwrite=overwrite)[1]:
                return False, archive_local, None

        self._info(f"archive successfully uploaded (or already exist), archive path: {archive_path}")
        package_dict["archivePath"] = archive_path

        return True, archive_local, archive_remote

    def _get_selected_index_impl(self):
        assert len(self._index_impls) == 1
        return self._index_impls[0]

    def _find_archive(self, ext_id) -> str:
        index_impl = self._get_selected_index_impl()
        urls = index_impl.get_urls()
        package_dict = index_impl.get_package_dict(ext_id)
        archive_path = package_dict.get("package", {}).get("archivePath", None) if package_dict else None
        if archive_path:
            # if path explicitly specified, just use it. It can either be relative or absoulte
            archive_path = archive_path.replace("\\", "/")
            archive_path = omni.client.combine_urls(urls.index_file, archive_path)
            archive_path = omni.client.normalize_url(archive_path)
            return archive_path
        else:
            # otherwise search for archive.
            # note: client.stat() only works well on nucleus. This code path won't always work for http.
            for archive_dir in [urls.archives] + urls.archives_alternatives:
                archive_path = f"{archive_dir}/{ext_id}.zip"
                if omni_client_exists(archive_path, reason="find archive"):
                    return archive_path

        return None

    def publish_extension(self, ext_path: str, ext_item: carb.dictionary.Item) -> bool:
        self._info(f"publish extension: {ext_path}")

        # 0. Sync index
        self._sync_index(resync=False)

        # by this point, registry implementation should be selected and only one
        index_impl = self._get_selected_index_impl()

        if index_impl.get_index_dict() is None:
            self._error("can't publish, index unavailable.")
            return False

        # use regular python dict:
        ext_dict = ext_item.get_dict()

        # check extension can be published
        try:
            package_id = verify_and_get_package_id_for_publishing(ext_dict)
        except Exception as e:
            self._error(f"Extension is invalid for publishing: '{e}'")
            return False

        # Changelog parsing and verification
        verification_result, changelog_content = verify_extension_for_publishing(ext_item)
        if not verification_result:
            self._error("Verification step failed.")
            return False

        _print(
            f"publishing extension. Path: '{ext_path}', Archive: '{package_id}', Index: '{index_impl.get_urls().index}'."
        )

        if self._is_http:
            return self._publish_extension_http(package_id, ext_path, ext_dict)
        else:
            return self._publish_extension_nucleus(index_impl, package_id, ext_path, ext_dict, changelog_content)

    def _sign_in_for_write_auth(self) -> bool:
        if self._auth_manager and not self._auth_manager.sign_in_for_write_auth():
            _error(f"Failed to sign in for registry write operation.")
            return False
        return True

    def _publish_extension_nucleus(
        self, index_impl: IRegistryIndex, ext_id: str, ext_path: str, ext_dict: dict, changelog_content: str
    ) -> bool:
        d = carb.dictionary.get_dictionary()

        skip_upload_metadata = _get_setting("/exts/omni.kit.registry.nucleus/skipUploadMetadata", False)

        # We about to do first write operation, try switch auth
        if not self._sign_in_for_write_auth():
            return False

        # Publish task: runs on a separate thread or synchronously
        def publish_task():
            # Working in temp folder from here on
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 0. Create and upload an archive as a first step, it takes most time likely. Don't want to lock index while doing it.
                res, archive_local, archive_remote = self._upload_archive(ext_id, ext_path, ext_dict, tmp_dir)
                if not res:
                    _error(f"Publishing of '{ext_id}' failed while uploading an archive.")
                    return False

                # 1. Upload resources (images and metadata)
                if not index_impl.upload_resources(ext_id, ext_dict, tmp_dir=tmp_dir, skip_images=skip_upload_metadata):
                    _error(f"Resource upload failed for: '{ext_id}'. Aborting publishing.")
                    return False

                # 2. Update index
                if not index_impl.add_to_index(ext_id, ext_dict):
                    _error(f"Publishing of '{ext_id}' failed while updating an index.")
                    return False

                self._send_telemetry_event("publish_extension", ext_id)

                return True

        # Parallel publishing is only possible when batching is enabled.
        # We run all publish tasks on separat threads and wait for them to complete when
        # applying index batched changes.
        is_batching = self._globals.is_index_changes_batching()
        is_parallel = self._parallel_publish and is_batching
        if is_parallel:
            if ext_id in self._parallel_publish_tasks:
                _error(f"Publishing of '{ext_id}' is already in progress.")
                return False

            publish_result = concurrent.futures.Future()
            def publish_thread_task():
                nonlocal publish_result
                try:
                    publish_result.set_result(publish_task())
                except Exception as e:
                    _error(f"Failed to publish extension '{ext_id}': {e}")
                    traceback.print_exc()
                    publish_result.set_result(False)
                publish_result_type = PublishResult.OK if publish_result.result() else PublishResult.FAIL
                self._globals.set_publish_results(ext_id, publish_result_type)
                _print_mt(f"Publishing of '{ext_id}' on path: '{ext_path}' completed. Result: {publish_result_type}")

            _print_mt(f"Publishing of '{ext_id}' on path: '{ext_path}' starting in a separate thread.")
            thread = threading.Thread(target=publish_thread_task)
            thread.start()
            self._parallel_publish_tasks[ext_id] = (publish_result, thread)
            return True
        else:
            # Just run the task synchronously
            res = publish_task()
            if res:
                _print(f"Extension '{ext_id}' on path: '{ext_path}' was published successfully to '{self._index_url}'.")
            return res

        return False

    def _publish_extension_http(self, ext_id: str, ext_path: str, ext_dict: dict) -> bool:
        post_url = self._index_url
        # Working in temp folder from here on
        with tempfile.TemporaryDirectory() as tmp_dir:
            res, archive_local, archive_remote = self._upload_archive(ext_id, ext_path, ext_dict, tmp_dir)
            if not res:
                _error(f"Publishing of '{ext_id}' failed while uploading an archive.")
                return False

            # If archive is already uploaded, we can just post metadata, without an archive (packman upload case)
            # If archive is not uploaded, we need to post it as well.
            if archive_remote:
                archive_local = None

            return post_publish_extension_request(post_url, ext_id, ext_dict, archive_local)

    def _unpublish_extension_http(self, ext_id: str) -> bool:
        post_url = self._index_url
        return post_unpublish_extension_request(post_url, ext_id)

    def unpublish_extension(self, ext_id: str) -> bool:
        self._info(f"unpublish extension: {ext_id}")

        # 0. Sync index
        self._sync_index(resync=False)

        # by this point, registry implementation should be selected and only one
        index_impl = self._get_selected_index_impl()
        urls = index_impl.get_urls()

        if index_impl.get_index_dict() is None:
            self._error("can't unpublish, index unavailable.")
            return False

        _print(f"unpublishing extension. Archive: '{ext_id}', Index: '{urls.index}'.")

        # Clean global cache?
        self._globals.get_exts_cache().invalidate(ext_id)

        if self._is_http:
            return self._unpublish_extension_http(ext_id)
        else:
            return self._unpublish_extension_nucleus(ext_id, index_impl)

    def _yank_extension_nucleus(self, ext_id: str, package_dict: dict, index_impl: IRegistryIndex) -> bool:
        # Mark as yanked
        package_dict.setdefault("package", {})["yanked"] = True

        # Update index
        if not index_impl.add_to_index(ext_id, package_dict):
            _error(f"Unpublishing (yanking) of '{ext_id}' failed while updating an index.")
            return False

        return True

    def _unpublish_extension_nucleus(self, ext_id: str, index_impl: IRegistryIndex) -> bool:
        urls = index_impl.get_urls()
        package_dict = index_impl.get_package_dict(ext_id)
        ext_name = package_dict.get("package", {}).get("name", "")

        # We about to do first write operation, try switch auth
        if not self._sign_in_for_write_auth():
            return False

        if _get_setting("/exts/omni.kit.registry.nucleus/yankWhenUnpublishing", True):
            return self._yank_extension_nucleus(ext_id, package_dict, index_impl)

        # Working in temp folder from here on
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. Remove from index: remove package with ext_id key
            if not index_impl.remove_from_index(ext_id):
                return False

            # 2. Delete archive
            archive_remote = self._find_archive(ext_id)
            if archive_remote:
                self._info(f"delete: {archive_remote}")
                result = omni.client.delete(archive_remote)
                self._info(f"result: {result}")
                if result != omni.client.Result.OK:
                    self._error(f"Failed delete archive: '{archive_remote}'. Result: {result}")

                # 3. Delete data (it is ok if it fails, it will be overwritten on next publish anyway)
                archive_data_remote = os.path.splitext(archive_remote)[0] + ".json"
                omni_client_try_delete(archive_data_remote)
            else:
                self._info(f"Failed to find archive for: '{ext_id}'. It is probably in packman.")
                result = omni.client.Result.OK

            # try delete meta data
            omni_client_try_delete(f"{urls.archives}/{ext_id}.json")
            if ext_name:
                omni_client_try_delete(f"{urls.archives}/{ext_name}/{ext_id}.json")

            _print(f"Extension '{ext_id}' on path: was unpublished successfully from '{urls.index}'.")
            self._send_telemetry_event("unpublish_extension", ext_id)
            return result == omni.client.Result.OK

        return False

    @info_exec_time()
    def pull_extension(self, ext_id: str, ext_folder: str) -> bool:
        try:
            self._pull_extension_async(ext_id, ext_folder, sync=True).send(None)
        except StopIteration as e:
            return e.value
        return False

    def pull_extension_async(self, ext_id: str, ext_folder: str) -> omni.ext.DownloadState:
        task = self._get_or_run_extension_pull(ext_id, ext_folder)
        if not task.done():
            return omni.ext.DownloadState.DOWNLOADING
        self._remove_pull_task(ext_id)
        return omni.ext.DownloadState.DOWNLOAD_SUCCESS if task.result() else omni.ext.DownloadState.DOWNLOAD_FAILURE

    def _remove_pull_task(self, ext_id: str):
        self._pull_tasks.pop(ext_id, None)

    def _get_or_run_extension_pull(self, ext_id: str, ext_folder: str):
        if ext_id in self._pull_tasks:
            return self._pull_tasks[ext_id]

        task = asyncio.ensure_future(self._pull_extension_async(ext_id, ext_folder))
        self._pull_tasks[ext_id] = task
        return task

    def _send_telemetry_event(self, event_name: str, ext_id: str):
        omni.kit.app.send_telemetry_event(
            f"omni.kit.registry.nucleus@{event_name}", data1=ext_id, data2=self._index_url
        )

    async def _pull_extension_async(self, ext_id: str, ext_folder: str, sync: bool = False) -> bool:
        self._info(f"pull extension: {ext_id} in '{ext_folder}'")

        self._send_telemetry_event("pull_extension", ext_id)

        # Force Invalidate cache? Will trigger re-download of archive.
        exts_cache = self._globals.get_exts_cache()
        if self._cache_invalidate_on_pull:
            exts_cache.invalidate(ext_id)

        # Pull extension in 2 attempts: if we have issues with the cache we can clean and restart again.
        for attempt in range(2):
            try:
                return await self._pull_extension_async_impl(ext_id, ext_folder, sync)
            except CorruptedCacheError as e:
                self._error(
                    f"Failed pulling extension '{ext_id}'. Extension cache is corrupted: {e}. Cleaning the cache."
                )
                exts_cache.invalidate(ext_id)

                # try again?
                if attempt == 0:
                    continue

                return False
            except Exception as e:
                self._error(f"Failed pulling extension '{ext_id}' with: '{traceback.format_exc()}'")
                return False
        return False

    async def _pull_extension_async_impl(self, ext_id: str, ext_folder: str, sync: bool = False) -> bool:
        index_impl = self._get_selected_index_impl()
        package_dict = index_impl.get_package_dict(ext_id)
        if not package_dict:
            self._error(f"Can't find package for: '{ext_id}'. Likely the registry summary file desynced from the package file for this extension.")
            return False

        archive_name = ext_id
        archive_path = package_dict.get("package", {}).get("archivePath", None)
        archive_subdir = package_dict.get("package", {}).get("archiveSubdir", "")
        if archive_path and not archive_subdir:
            archive_name = os.path.splitext(os.path.basename(archive_path))[0]
            # unescape back (on filesystem just use '+' symbol)
            archive_name = archive_name.replace("%2B", "+")

        exts_cache = self._globals.get_exts_cache()
        exts_cache_path = exts_cache.get_ext_cache_path(archive_name)
        if not exts_cache_path:
            cache_path = exts_cache.get_cache_path()
            self._info(f"{ext_id} (archive_name: {archive_name}) is not in cache: '{cache_path}'")
            # Just download zip into temp folder and unzip into passed ext_folder:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # TODO: fix find_archive call to be async
                archive_remote = self._find_archive(ext_id)
                if not archive_remote:
                    self._error(f"Can't find archive for: '{ext_id}'.")
                    return False

                archive_local = f"{tmp_dir}/{ext_id}.zip"
                archive_local = archive_local.replace("\\", "/")

                # Try both http and https if one fails
                remote_urls = [archive_remote]
                if self._try_both_http_and_https:
                    if archive_remote.startswith("https:/"):
                        remote_urls.append(archive_remote.replace("https:/", "http:/"))
                    elif archive_remote.startswith("http:/"):
                        remote_urls.append(archive_remote.replace("http:/", "https:/"))

                result = None
                for remote_url in remote_urls:
                    _print_mt(f"downloading: '{remote_url}' -> '{archive_local}'...")
                    if sync:
                        if remote_url.startswith("http") and self._use_urllib_for_http:
                            try:
                                request.urlretrieve(remote_url, archive_local)
                                result = omni.client.Result.OK
                            except Exception as e:
                                self._error(f"request.urlretrieve failed with: '{e}'")
                                result = omni.client.Result.ERROR_NOT_FOUND
                        else:
                            result = omni_client_copy(remote_url, archive_local, "downloading ext archive")
                    else:
                        result = await omni_client_copy_async(remote_url, archive_local, "downloading ext archive")
                    if result == omni.client.Result.OK:
                        break
                    self._info(f"Failed to download: '{remote_url}', result: {result}")

                if result != omni.client.Result.OK:
                    self._warn(f"Failed to download: '{archive_remote}' with result: {result}")
                    return False

                # Unpacking on a separate thread, but wait for it with asyncio. Not to block in async mode.
                _print_mt(f"unpacking: {archive_local} -> {cache_path}/{archive_name}")
                unpacked_future = concurrent.futures.Future()

                def unpack():
                    try:
                        omni.ext.unpack_extension(
                            archive_local,
                            cache_path,
                            ext_id=archive_name,
                            archive_subdir=archive_subdir,
                            skip_security_checks=self._trusted,
                        )
                    finally:
                        unpacked_future.set_result(True)

                if sync:
                    unpack()
                else:
                    t = threading.Thread(target=unpack)
                    t.start()
                    await asyncio.wrap_future(unpacked_future)

                exts_cache_path = exts_cache.get_ext_cache_path(archive_name)
                if exts_cache_path:
                    self._finalize_install(ext_id, exts_cache_path)

        # By this point it should be in cache
        if not exts_cache_path:
            self._error(f"Extension is not in cache: '{ext_id}'. Probably failed to unpack or cache is corrupted.")
            return False

        # called before actual cache install because it can make a copy (instead of link).
        self._finalize_cache_install(ext_id, exts_cache_path)
        return exts_cache.install(exts_cache_path, ext_folder, ext_id)

    def _write_index_keys_to_cached_ext(self, ext_id: str, exts_cache_path: str, index_keys_to_write: List[str]):
        # If there is no "extension.gen.toml" generate one manually or append to existing one.
        # It is important when installed from github to write metadata and subdir.
        # It is important when installing extensions locked on kitHash and when useContentHashAsArchiveName is set (kit-sdk extensions):
        # we write kitHash to installed extension copy, each time it is installed. It is not there by default to be able to
        # use the same package for different kernel versions. However, we don't want package loaded by mistmatching kit
        # version (the one that was not used to install it).
        # It is also useful for other installation to have date and build number in local copies.

        if not os.path.isdir(exts_cache_path):
            return

        for p in ["extension.toml", "config/extension.toml"]:
            config_path = os.path.join(exts_cache_path, p)
            if os.path.exists(config_path):
                d = carb.dictionary.get_dictionary()
                gen_config_path = os.path.splitext(config_path)[0] + ".gen.toml"
                updated = False
                if os.path.exists(gen_config_path):
                    ext_dict = carb.dictionary.get_toml_serializer().create_dictionary_from_file(gen_config_path)
                    if not ext_dict:
                        raise CorruptedCacheError(f"Failed to read: '{gen_config_path}'")
                else:
                    ext_dict = d.create_item(None, "", carb.dictionary.ItemType.DICTIONARY)
                    updated = True

                index_impl = self._get_selected_index_impl()
                package_dict = index_impl.get_package_dict(ext_id)
                for key in index_keys_to_write:
                    v = get_dict_value_by_path(package_dict, key, default=None)
                    if v is not None:
                        # Special case for lists (for package/targets) -> concat them and make sure items are unique
                        if isinstance(v, list) or isinstance(v, tuple):
                            v = list(set(list(v) + list(ext_dict.get(key, []))))
                        # Get prev value to compare and avoid writing the file if nothing changed.
                        # Lists becomes tuples, handle that separately.
                        prev = d.get(ext_dict, key)
                        if isinstance(prev, tuple):
                            prev = list(prev)
                        if prev != v:
                            d.set(ext_dict, key, v)
                            updated = True

                if updated:
                    carb.dictionary.get_toml_serializer().save_file_from_dictionary(
                        ext_dict, gen_config_path, SERIALIZER_OPTION_MAKE_PRETTY
                    )
                d.destroy_item(ext_dict)
                return

    def _finalize_install(self, ext_id: str, exts_cache_path: str):
        # Write meta data and subdirs, called once when actually downloaded and installed
        self._write_index_keys_to_cached_ext(
            ext_id, exts_cache_path, INDEX_KEYS_TO_WRITE_TO_GENERATED_CONFIG_ON_DOWNLOAD
        )

    def _finalize_cache_install(self, ext_id: str, exts_cache_path: str):
        # Append targets, called every time when installed from cache (copy or link)
        self._write_index_keys_to_cached_ext(
            ext_id, exts_cache_path, INDEX_KEYS_TO_WRITE_TO_GENERATED_CONFIG_ON_INSTALL
        )
