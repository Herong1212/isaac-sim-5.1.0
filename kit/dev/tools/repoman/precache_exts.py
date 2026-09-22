import os
import argparse
import logging
import fnmatch
import tempfile
import atexit
import sys
import shutil
import copy

from functools import cache
from typing import Dict, Callable, Tuple
from string import Template

import packmanapi
import omni.repo.man
from omni.repo.man.utils import ci_message

logger = logging.getLogger("omni.repo.precache_exts")

@cache
def get_tmp_dir() -> str:
    """Get a temporary directory for the current process (singleton)."""
    tmp = tempfile.TemporaryDirectory()
    atexit.register(tmp.cleanup)
    return tmp.name


def resolve_tokens(p: str, root: str, config: str, platform_host: str, app_name: str = None):
    mapping = omni.repo.man.get_platform_file_mapping(platform_host)
    mapping["package_root"] = root.replace("\\", "/")
    mapping["config"] = config
    mapping["app_name"] = app_name or ""
    return Template(p).substitute(mapping)


def cleanup_folder(folder):
    omni.repo.man.clean_folders([folder])
    if os.path.exists(folder):
        raise Exception(
            f"{folder} was not successfully removed, most probably due to a file lock on 1 or more of the files."
        )


def get_backup_path(path):
    return get_tmp_dir() + "/" + os.path.basename(path) + ".bak"


def backup_file(path):
    shutil.copy2(path, get_backup_path(path))


def restore_file(path):
    if os.path.exists(path):
        os.remove(path)
    shutil.move(get_backup_path(path), path)


def find_and_remove_version_lock(path):
    """Remove generated part (version lock) from kit file.

    If exists, parse and return the version lock as it was before removing it.
    """
    logger.info(f"trying to remove generate part in kit file: {path}")

    content = ""
    generated_block = None
    with open(path, "r") as f:
        content = f.read()
        lines = content.split("\n")
        try:
            start = next(i for i, v in enumerate(lines) if v.startswith("# BEGIN GENERATED PART"))
            end = next(i for i, v in enumerate(lines) if v.startswith("# END GENERATED PART"))
            generated_block = "\n".join(lines[start:end + 1])
            del lines[start - 2 : end + 2]
        except StopIteration as e:
            logger.info(f"generated part was not found in: {path}")
            return

        content = "\n".join(lines)

    with open(path, "w") as f:
        f.write(content)
        print(f"removed generated part in: {path}")

    if generated_block:
        data = omni.repo.man.get_toml_module().loads(generated_block)
        return data.get("settings", {}).get("app", {}).get("exts", {}).get("enabled")

    return None



def load_toml(path):
    return omni.repo.man.get_toml_module().load(path)


def ext_id_to_name_version(ext_id: str) -> Tuple[str, str]:
    """Convert 'omni.foo-tag-1.2.3' to 'omni.foo-tag' and '1.2.3'"""
    if "-" not in ext_id:
        return ext_id, ""
    a, b, *rest = ext_id.split("-")
    if b:
        if not b[0:1].isdigit():
            return f"{a}-{b}", "-".join(rest)
        return a, "-".join([b] + rest)
    return a, ""


def create_link(src, dst):
    print(f"Creating a link '{src}' -> '{dst}'")
    packmanapi.link(src, dst)


def create_ext_links(cache_path, links_path, tool_config):
    if not links_path:
        return

    exts_to_link = tool_config.get("links", {}).get("exts")
    include = exts_to_link.get("include", [])
    exclude = exts_to_link.get("exclude", [])

    def matches(ext_id: str):
        return any(fnmatch.fnmatch(ext_id, p) for p in include) and not any(
            fnmatch.fnmatch(ext_id, p) for p in exclude
        )

    for ext_id in os.listdir(cache_path):
        ext_name, version = ext_id_to_name_version(ext_id)
        if matches(ext_name):
            ext_path = f"{cache_path}/{ext_id}"
            src_path = f"{links_path}/{ext_name}"
            if not os.path.exists(src_path):
                os.makedirs(links_path, exist_ok=True)
                create_link(src_path, ext_path)


def try_parse_test_deps(config_path) -> list[str]:
    """
    Try to get all test dependencies from the extension.toml file.
    For each [[test]] entry, get the "dependencies".
    """
    try:
        cfg_data = load_toml(config_path)
    except Exception as e:
        logger.warning(f"Failed to parse {config_path}: {e}")
        return []

    test_deps = []
    for test_cfg in cfg_data.get("test", []):
        test_deps.extend(test_cfg.get("dependencies", []))
    return test_deps


def build_lock_update_args(update_exts, prev_version_lock):
    """
    Logic for updating version lock only for a subset of extensions.
    We keep previous lock, but modify it to remove the extensions that we want to update.
    This function only used when some extensions are specified in -u flag. E.g. `-u omni.foo omni.bar`.
    """
    import json

    logger.info(f"Building relaxed version lock to only update a subset of exts: {update_exts}")

    # remove update_exts from the previous version lock:
    relaxed_lock = []
    for lock_ext in prev_version_lock:
        lock_name, lock_version = ext_id_to_name_version(lock_ext)
        in_update_list = False
        for update_ext in update_exts:
            update_name, update_version = ext_id_to_name_version(update_ext)
            if lock_name == update_name:
                in_update_list = True
                # If update version was specified, still add to the relaxed (new) lock.
                # E.g. if you specify `-u omni.foo-2` it would limit the lock to 2.x.x
                if update_version:
                    relaxed_lock.append(update_ext)
        # If not in the update list (not specified in -u) - keep it locked to the previous version.
        if not in_update_list:
            relaxed_lock.append(lock_ext)

    # generate a new config file with the relaxed lock:
    precache_extra_cfg = os.path.join(get_tmp_dir(), "precache-config.json").replace("\\", "/")
    with open(precache_extra_cfg, "w") as f:
        json.dump({ "app": { "extensions": { "enabled": relaxed_lock } } }, f)
    return [f"-m={precache_extra_cfg}"]



def get_all_extensions_and_test_deps(ext_folders):
    """Find all extensions in the repo and their test dependencies."""
    exts = []
    test_deps = []
    for ext_folder in ext_folders:
        if not os.path.exists(ext_folder):
            continue
        for ext in os.listdir(ext_folder):
            ext_path = f"{ext_folder}/{ext}"
            for config_path in [f"{ext_path}/extension.toml", f"{ext_path}/config/extension.toml"]:
                if os.path.exists(config_path):
                    exts.append(ext)
                    test_deps.extend(try_parse_test_deps(config_path))
                    break
    return exts, test_deps


def generate_exts_deps_app(generated_app_path, local_extensions, test_deps):
    renegenerate = True
    if os.path.exists(generated_app_path):
        content = load_toml(generated_app_path)
        ext_deps = set(content.get("dependencies", {}).keys())
        # Check if the list of extensions (+ versions) is the same as in the generated app
        if ext_deps == (set(local_extensions) | set(test_deps)):
            renegenerate = False
        else:
            print(f"Regenerating {generated_app_path} because it contains outdated extensions list.")

    if renegenerate:
        os.makedirs(os.path.dirname(generated_app_path), exist_ok=True)
        with open(generated_app_path, "w") as f:
            f.write(
                r"""
########################################################################################################################
# This kit file is generated by "repo precache_exts" tool.
# It is an app, that contains all extensions from the repo as dependencies. It is used to:
# 1. lock all versions of their dependencies (reproducible builds).
# 2. precache (download) all dependencies before building.
#
# This file is regenerated if:
# 1. Any extension is added or removed from the repo.
# 2. Any extension version is updated
# 3. This file is removed.
#
# To update version lock the same `repo build -u` flag can be used.
########################################################################################################################

[settings.app.exts.folders]
'++' = ["${app}/../exts", "${app}/../extscache/"]

[dependencies]
# All local extensions built in this repo:
"""
            )
            local_extensions_set = set(local_extensions)
            for ext_name in sorted(local_extensions):
                f.write(f'"{ext_name}" = {{}}\n')
            if test_deps:
                f.write("\n# All test dependencies:\n")
                for ext_name in sorted(test_deps):
                    if ext_name not in local_extensions_set:
                        f.write(f'"{ext_name}" = {{}}\n')

    return generated_app_path


def run(tool_config, options, root, platform_host):
    registries = tool_config.get("registries", [])
    apps = tool_config.get("apps", [])

    def sub_extra_tokens(s, app_name=None):
        return resolve_tokens(s, root, options.config, platform_host, app_name=app_name)

    def process_path(p, app_name=None):
        return os.path.normpath(sub_extra_tokens(p, app_name=app_name)) if p else None

    def extract_app_name(app):
        app_name = os.path.basename(app)
        return os.path.splitext(app_name)[0]

    kit_path = process_path(tool_config.get("kit_path"))
    kit_extra_args = [sub_extra_tokens(arg) for arg in tool_config.get("kit_extra_args", [])]

    ext_folders = [process_path(path) for path in tool_config.get("ext_folders", [])]

    # If we are enabling version compatibility with USD we want to look for compatible extensions
    # in the designated registries when pre-caching. Order is important here, if we have an extension
    # with the same version we want to use the one published to the USD version compatible registry
    usd_version_compat_config = tool_config.get("usd", {}).get("version_compatibility", {})
    usd_version_compat_enabled = usd_version_compat_config.get("enable", False)
    if usd_version_compat_enabled:
        registries = usd_version_compat_config.get("registries", []) + registries

    # Gather all extensions and test dependencies in the repo:
    local_extensions, test_deps = get_all_extensions_and_test_deps(ext_folders)

    # Auto-add test dependencies to the generated app?
    if not tool_config.get("generated_app", {}).get("add_test_deps", True):
        test_deps = []
    # Default test deps:
    test_deps.extend(tool_config.get("generated_app", {}).get("default_test_deps", []))
    # Remove versions and duplicates:
    test_deps = list({ext_id_to_name_version(d)[0] for d in test_deps})

    def get_all_apps():
        # Precache all specified app path
        for app in apps:
            yield process_path(app), []

        # If specified - generate an app with ALL extensions in the repo and precache it too to lock all versions
        generated_app_path = process_path(tool_config.get("generated_app_path"))
        if generated_app_path and len(local_extensions) > 0:
            # Do not put local extensions in the lock (this kit file is not published):
            extra_args = ["--/app/extensions/generateVersionLockSkipLocalExts=1"]
            yield generate_exts_deps_app(generated_app_path, local_extensions, test_deps), extra_args

    # Remember cleaned path to avoid cleaning for each app
    cleaned_cache_path = set()

    update_exts = options.update
    if update_exts:
        # flatten
        update_exts = [item for sublist in update_exts for item in sublist]

    for app_path, extra_args in get_all_apps():
        logger.info(f"precaching app: {app_path}")

        app_name = extract_app_name(app_path)

        cache_path = process_path(tool_config.get("cache_path"), app_name=app_name)

        # update_exts can be:
        # 1. None - just precache
        # 2. [] - update version lock for all extensions: precache_exts -u
        # 3. ["omni.foo", "omni.foo"] - update version lock only for specified extensions: precache_exts -u omni.foo omni.bar
        is_updating_lock = update_exts != None
        prev_version_lock = None
        if is_updating_lock or options.clean:
            backup_file(app_path)
            prev_version_lock = find_and_remove_version_lock(app_path)
            if cache_path and cache_path not in cleaned_cache_path:
                cleaned_cache_path.add(cache_path)
                cleanup_folder(cache_path)

        if cache_path:
            os.makedirs(cache_path, exist_ok=True)

        if options.clean:
            continue

        args = [app_path]
        args += ["--allow-root"]

        if tool_config.get("kit_portable", True):
            args += ["--portable"]

        # If we don't download in any specific folder - we are downloading in a regular app data
        if not cache_path and is_updating_lock:
            args += ["--clear-data"]

        args += ["--ext-precache-mode"]
        args += ["--/crashreporter/gatherUserStory=0"]
        args += ["--/app/settings/persistent=0"]
        args += ["--/app/settings/loadUserConfig=0"]
        if tool_config.get("generate_version_lock", True):
            args += ["--/app/extensions/generateVersionLock=1"]
        if tool_config.get("generate_version_lock_overwrite", True):
            args += ["--/app/extensions/generateVersionLockOverwrite=1"]
        if tool_config.get("kit_parallel_pull", False):
            args += ["--/app/extensions/parallelPullEnabled=1"]
        if tool_config.get("kit_use_urllib_for_http", False):
            args += ["--/exts/omni.kit.registry.nucleus/useUrllibForHttp=1"]
        if tool_config.get("kit_omit_ext_version", False):
            args += ["--/exts/omni.kit.registry.nucleus/omitExtVersion=1"]
        args += ["--/app/enableStdoutOutput=1"]
        args += ["--/app/extensions/detailedSolverExplanation=1"]
        args += ["--/app/extensions/registryEnabled=1"]
        args += ["--/app/extensions/mkdirExtFolders=0"]
        if cache_path:
            args += [f"--/app/extensions/registryCacheFull='{cache_path}'"]
        args += ["--/log/flushStandardStreamOutput=1"]
        for i, registry in enumerate(registries):
            args += ['--/exts/omni.kit.registry.nucleus/registries/{}/name="{}"'.format(i, registry["name"])]
            args += ['--/exts/omni.kit.registry.nucleus/registries/{}/url="{}"'.format(i, registry["url"])]

        args += [f"--/app/extensions/target/config={options.config}"]

        for ext_folder in ext_folders:
            args += ["--ext-folder", ext_folder]

        if options.log_info:
            args += ["-v"]

        if is_updating_lock and len(update_exts) > 0 and prev_version_lock:
            args += build_lock_update_args(update_exts, prev_version_lock)

        args += extra_args

        args += kit_extra_args

        args = [kit_path] + args

        # Set env vars
        env_vars = tool_config.get("kit_env_vars", {})
        env = copy.deepcopy(os.environ)
        for e, v in env_vars.items():
            print(f"Setting env var: {e}={v}")
            env[e] = v

        if "OMNI_KIT_LD_PRELOAD" in os.environ:
            # This envvar tells us to launch kit with certain libraries preloaded.
            # This is needed for ASAN and TSAN. If the process entrypoint isn't built against these
            # libraries (it won't be because it's part of carb_sdk+plugins), we need to preload
            # the libraries so they're the first libraries loaded.
            # We only set these options for the kit launch rather than the full repo_build process
            # to avoid running the sanitizers on python and other tools.
            env["LD_PRELOAD"] = f"{env['OMNI_KIT_LD_PRELOAD']}{os.pathsep}{os.getenv('LD_PRELOAD') or ''}"
            print(f'LD_PRELOAD={env["LD_PRELOAD"]}')

            # TSAN will cause processes to fail if it detects errors, so we need to tell it to use
            # exit code 0 if it detects errors otherwise the build will fail.
            env["TSAN_OPTIONS"] = "exitcode=0"

        print("running kit for app precache, cmd: {}".format(" ".join(args)))
        returncode = omni.repo.man.run_process(args, exit_on_error=False, env=env)

        # Create ext short links (for build-time mostly)
        if returncode == 0:
            links_path = process_path(tool_config.get("links", {}).get("path", None), app_name=app_name)
            create_ext_links(cache_path, links_path, tool_config)

        # Publish TC artifacts
        publish_artifacts = [
            os.path.join(root, resolve_tokens(p, root, options.config, platform_host))
            for p in tool_config.get("publish_artifacts", [])
        ]
        for p in publish_artifacts:
            ci_message("publishArtifacts", p, ci_platforms=["teamcity"])

        # fail?
        if returncode != 0:
            if is_updating_lock:
                print("Version lock update failed. Restoring app file...")
                restore_file(app_path)
            sys.exit(returncode)


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    tool_config = config.get("repo_precache_exts", {})
    enabled = tool_config.get("enabled", False)
    if not enabled:
        return None

    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.description = """
Tool to precache kit apps. Downloads extensions without running.

It automatically creates a version lock for each app it precaches. Version lock can be updated with `-u` flag.
Update version lock for all or selected extensions. E.g.:
    - (all): precache_exts -u
    - (selected): precache_exts -u omni.foo omni.bar
    - (select + version limit): precache_exts -u omni.foo-2 omni.bar-3
"""

    parser.add_argument("-c", "--config", dest="config", required=False, default="release")
    parser.add_argument("-v", "--info", dest="log_info", required=False, action="store_true")
    parser.add_argument(
        "-x",
        "--clean",
        dest="clean",
        required=False,
        action="store_true",
        help="Reset version lock and cache: remove generated part from kit files, clean cache path and exit.",
    )
    parser.add_argument(
        "-u",
        "--update",
        dest="update",
        nargs="*",
        action="append",
        help="Update version lock for all or selected extensions. E.g. '-u', '-u omni.foo omni.bar'."
    )

    def run_repo_tool(options: Dict, config: Dict):
        tool_config = config.get("repo_precache_exts", {})
        repo_folders = config["repo"]["folders"]

        if options.log_info:
            logger.setLevel(logging.INFO)

        platform_host = omni.repo.man.get_host_platform()
        run(tool_config, options, repo_folders["root"], platform_host)

    return run_repo_tool
