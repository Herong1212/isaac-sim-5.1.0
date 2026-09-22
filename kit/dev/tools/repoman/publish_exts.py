import argparse
import fnmatch
import json
import logging
import os
import shutil
import sys
import tempfile
from string import Template
from typing import Callable, Dict
from urllib.parse import urlparse

import omni.repo.man
from omni.repo.man.utils import ci_message
from omni.repo.man.guidelines import get_abi_platform_translation
import packmanapi

logger = logging.getLogger("omni.repo.publish_exts")


def try_get_git_url():
    """Try to get git url from current repo.

    Might fail if no git or we are not in git repo. In that case return empty string."""
    try:
        # Call git to try get url. It can include user:password in some cases, remove those.
        git_url = omni.repo.man.call_git(["config", "--get", "remote.origin.url"], silence_errors=True).decode().strip()
        parsed = urlparse(git_url)
        return parsed._replace(netloc=parsed.hostname).geturl()
    except Exception as e:
        logger.info(f"Failed to get git url: {e}")
        return ""


class ToolContext:
    def __init__(self, options: Dict, stats_file: str):
        self.options = options
        self.stats_file = stats_file
        self.kit_root = ""
        self.git_repo_url = try_get_git_url()
        logger.info(f"Git repo url: {self.git_repo_url}")

    def resolve_tokens(self, p: str, root: str):
        platform_host = omni.repo.man.get_host_platform()
        abi = omni.repo.man.get_token("abi")
        mapping = omni.repo.man.get_platform_file_mapping(platform_host)
        mapping["publish_root"] = root.replace("\\", "/")
        mapping["config"] = self.options.config
        mapping["kit_config"] = self.options.kit_config
        mapping["platform_target"] = self.options.platform_target
        # prepend with publish_ to avoid conflicts with repo_man tokens
        mapping["publish_platform_target"] = self.options.platform_target
        mapping["publish_platform_target_abi"] = get_abi_platform_translation(self.options.platform_target, abi)
        mapping["python_tag"] = self.options.python_tag
        mapping["kit_root"] = self.kit_root
        return Template(p).substitute(mapping)


def teamcity_report_fail(test_id, fail_type, err):
    omni.repo.man.teamcity_message("testFailed", name=test_id, fail_type=fail_type, message=err)


def teamcity_start_test(test_id):
    omni.repo.man.teamcity_message("testStarted", name=test_id, captureStandardOutput="true")


def teamcity_stop_test(test_id):
    omni.repo.man.teamcity_message("testFinished", name=test_id)


def report_stats(stats_file, verify_only):
    exts = {}
    try:
        with open(stats_file, "r") as f:
            d = json.load(f)
            logger.info(f"Loaded stats from: {stats_file}")
            exts = d["_exts"]
    except Exception as e:
        print(f"Failed opening stats file, error: {e}")

    res_to_str = {
        "OK": "[  ok  ]",
        "OK_EXISTS": "[exists]",
        "FAIL": "[ fail ]",
        "SKIP": "[ skip ]",
    }

    # wording
    summary_text = "Verification" if verify_only else "Publish"
    status_text = "verified" if verify_only else "published"
    action_failure_text = "verification" if verify_only else "publishing"
    status_error_text = "VERIFICATION_ERROR" if verify_only else "PUBLISH_FAILED"

    # simulate as tests for TC reporting:
    failed_exts = ""
    for package_id, res in exts.items():
        test_id = package_id.replace(".", "_")
        teamcity_start_test(test_id)
        if res == "FAIL":
            teamcity_report_fail(test_id, "Error", f"{action_failure_text} failed")
            failed_exts += f"{res_to_str[res]} {package_id}\n"
        teamcity_stop_test(test_id)

    # do report
    print("\n")
    print("=" * 60)
    print(f"Extension {summary_text} Summary")
    print("=" * 60)
    for package_id, res in exts.items():
        print(f"{res_to_str[res]} {package_id}")

    print("=" * 60)
    print("=" * 60)

    # If anything failed report as build problem
    if failed_exts:
        omni.repo.man.teamcity_message("buildProblem", description=failed_exts, status=status_error_text)

    results = list(exts.values())
    total_ok = results.count("OK")
    total_ok_exists = results.count("OK_EXISTS")
    total_fail = results.count("FAIL")
    total_skipped = results.count("SKIP")
    status = f"{total_ok} extension packages {status_text} out of {len(exts)} (failed: {total_fail}, skipped: {total_skipped}, exists: {total_ok_exists})."
    omni.repo.man.teamcity_message("buildStatus", text=status)

    if not omni.repo.man.is_running_on_ci():
        # remove file if local, not to confuse users on multiple runs
        try:
            os.remove(stats_file)
        except (OSError, FileNotFoundError):
            pass


def sign_folders(paths, signing_config, tool_context: ToolContext):
    simulate = tool_context.options.dry_run

    if tool_context.options.config not in signing_config.get("configs", []):
        logger.info(f"Skipping signing for config: {tool_context.options.config}")
        return

    if tool_context.options.platform_target not in signing_config.get("platforms", []):
        logger.info(f"Skipping signing for platform: {tool_context.options.platform_target}")
        return

    try:
        import omni.repo.codesign

        for path in paths:
            print(f"Signing folder: '{path}' using repo_codesign (simulate={simulate})...")
            res = omni.repo.codesign.sign_folder(path, simulate=simulate)
            if not res:
                raise Exception(f"repo_codesign failed to sign path: {path}")

    except ImportError:
        raise Exception(
            "Failed to import 'omni.repo.codesign'. `repo_codesign' tool is required when signing is enabled, add it to your 'repo-deps.packman.xml'."
        )


def run(tool_config, tool_context, root, repo_folders):
    exts_to_publish = tool_config.get("exts", {})
    write_auth = tool_config.get("write_auth", "")
    read_auth = tool_config.get("read_auth", "")

    # If read_auth is not set, use write_auth, it normally has all permissions
    if not read_auth:
        read_auth = write_auth

    def sub_extra_tokens(s):
        return tool_context.resolve_tokens(s, root)

    def process_path(p):
        return os.path.normpath(sub_extra_tokens(p))

    kit_path = process_path(tool_config.get("kit_path"))
    kit_extra_args = [sub_extra_tokens(arg) for arg in tool_config.get("kit_extra_args", [])]

    publish_verification = tool_config.get("publish_verification", False)

    signing_config = tool_config.get("signing", {})
    signing_enabled = signing_config.get("enabled", False)
    if tool_context.options.verify:
        signing_enabled = False
    if signing_enabled:
        folders = [process_path(path) for path in signing_config.get("folders", [])]
        sign_folders(folders, signing_config, tool_context)

    # Set env vars
    env_vars = tool_config.get("kit_env_vars", {})
    for e, v in env_vars.items():
        print(f"Setting env var: {e}={v}")
        os.environ[e] = v

    build_number = omni.repo.man.build_number.generate_build_number_from_file(repo_folders["version_file"])

    # For USD version compatibility
    # Compatibility with a particular USD version has two parts:
    # 1. Enabling usd.version_compatibility.enable in an Extensions's repo.toml
    # 2. Writing the USD target as part of the Extension's metadata
    #
    # The first option will use Extension registries specific to the USD version that the Extension was built against
    # This helps Extensions isolate and use versions of USD that are not completely supported by Kit.
    # A couple examples of this would be:
    # - testing out new versions of USD that introduce new features,
    # - custom build of USD that can introduce ABI incompatible changes but necessary for different applications
    #
    # The second will allow individual Extensions (in the sampe repository) to determine if they are explicitly dependent on USD.
    # Examples here would include:
    # - One Extension in the repository has a direct dependency on USD (such as it introduces a SdfFileFormat, UsdAPISchema, etc.)
    # - The Extension(s) uses features of USD that are not backwards-compatible

    usd_version_compat_config = tool_config.get("usd", {}).get("version_compatibility", {})
    usd_version_compat_enabled = usd_version_compat_config.get("enable", False)
    usd_version_compat_registries = usd_version_compat_config.get("registries", [])

    registries = usd_version_compat_registries if usd_version_compat_enabled else tool_config.get("registries", [])

    all_good = True
    for registry in registries:
        logger.info(f"publishing extensions: {exts_to_publish} in registry: '{registry}'")

        args = ["--allow-root", "--portable", "--/crashreporter/gatherUserStory=0"]

        publish_args = []
        publish_args += [arg for i in exts_to_publish.get("include", []) for arg in ("-i", f'"{i}"')]
        publish_args += [arg for i in exts_to_publish.get("exclude", []) for arg in ("-e", f'"{i}"')]
        publish_args += ["--stats-file", tool_context.stats_file]

        if tool_context.options.dry_run:
            publish_args += ["-n"]
        if tool_context.options.verify:
            publish_args += ["--verify"]
        if tool_context.options.dump:
            publish_args += ["--dump", tool_context.options.dump]
        if exts_to_publish.get("exclude_apps", False):
            publish_args += ["--exclude-apps"]

        args += ["--enable", "omni.kit.registry.nucleus"]
        args += ["--exec", "publish_exts.py " + " ".join(publish_args)]
        args += ["--/app/enableStdoutOutput=0"]
        args += ["--/log/flushStandardStreamOutput=1"]
        args += ["--/app/extensions/mkdirExtFolders=0"]

        # Disable applying dict filters ("filter:[keyword]"), so that they are kept in published ext data
        args += ["--/app/extensions/applyDictFilters=0"]

        args += ['--/app/extensions/registryPublishDefault="{}"'.format(registry["name"])]
        args += ['--/exts/omni.kit.registry.nucleus/registries/0/name="{}"'.format(registry["name"])]
        args += ['--/exts/omni.kit.registry.nucleus/registries/0/url="{}"'.format(registry["url"])]
        args += ['--/exts/omni.kit.registry.nucleus/registries/1/url=""'] # to disable kit/sdk registry (not needed)
        args += ['--/exts/omni.kit.registry.nucleus/accounts/0/url=""'] # to match all hosts with provided auth
        args += ['--/exts/omni.kit.registry.nucleus/accounts/0/write="{}"'.format(write_auth)]
        args += ['--/exts/omni.kit.registry.nucleus/accounts/0/read="{}"'.format(read_auth)]

        args += [f"--/app/extensions/target/platform={tool_context.options.platform_target}"]
        args += [f"--/app/extensions/target/config={tool_context.options.config}"]
        if tool_context.options.python_tag:
            args += [f"--/app/extensions/target/python={tool_context.options.python_tag}"]

        # Extra data
        args += ['--/app/extensions/publishExtraDict/package/publish/buildNumber="{}"'.format(build_number)]
        repo_name = tool_config.get("repo_name", "")
        if repo_name:
            args += ['--/app/extensions/publishExtraDict/package/publish/repoName="{}"'.format(repo_name)]
        else:
            logging.warn(
                "'repo_publish_exts.repo_name' is not set in repo.toml. Please set it, e.g.: repo_name = 'kit-usd'"
            )
        if tool_context.git_repo_url:
            args += ['--/app/extensions/publishExtraDict/package/repository="{}"'.format(tool_context.git_repo_url)]
        if signing_enabled:
            args += ["--/app/extensions/publishExtraDict/package/publish/signed=1"]

        for ext_folder in tool_config.get("ext_folders", []):
            path = process_path(ext_folder)
            args += ["--ext-folder", path]

        if not publish_verification:
            args += ["--/app/extensions/skipPublishVerification=1"]

        if tool_config.get("use_content_hash_as_archive_name", False):
            args += ["--/exts/omni.kit.registry.nucleus/useContentHashAsArchiveName=1"]

        if tool_config.get("use_packman_to_upload_archive", True):
            args += ["--/exts/omni.kit.registry.nucleus/usePackmanToUploadArchives=1"]

        if tool_config.get("skip_upload_metadata", False):
            args += ["--/exts/omni.kit.registry.nucleus/skipUploadMetadata=1"]

        if tool_config.get("remove_authors_from_config", False):
            args += ["--/exts/omni.kit.registry.nucleus/removeAuthorsFromConfig=1"]

        if tool_config.get("write_target_kit_hash", False):
            args += ["--/app/extensions/writeTarget/kitHash=1"]

        if tool_config.get("parallel_publish", False):
            args += ["--/exts/omni.kit.registry.nucleus/parallelPublish=1"]
            # The removal of generated config is not supported in parallel publish (it happens synchronously)
            args += ["--/app/extensions/removeGeneratedConfigAfterPublish=0"]

        # set more retries for publishing:
        retry_count = tool_config.get("retry_count", 12)
        args += [f"--/exts/omni.kit.registry.nucleus/retryParameters/maxRetries={retry_count}"]

        if tool_context.options.log_info:
            args += ["-v"]

        args += kit_extra_args

        args = [kit_path] + args

        print(f"running kit for ext publishing, args: {args}")
        returncode = omni.repo.man.run_process(args, exit_on_error=False)

        # Publish TC artifacts
        if omni.repo.man.is_running_in_teamcity():
            publish_artifacts = [
                os.path.join(root, sub_extra_tokens(p)) for p in tool_config.get("publish_artifacts", [])
            ]
            for p in publish_artifacts:
                ci_message("publishArtifacts", p, ci_platforms=["teamcity"])

        # fail?
        if returncode != 0:
            all_good = False

    return all_good


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    tool_config = config.get("repo_publish_exts", {})
    enabled = tool_config.get("enabled", False)
    if not enabled:
        return None

    archive_pattern = tool_config.get("archive_pattern")

    parser.description = "Tool to publish kit extensions to the registry."
    parser.add_argument("-c", "--config", dest="config", required=False, default="release")
    parser.add_argument(
        "--kit-config",
        dest="kit_config",
        required=False,
        default=None,
        help="Kit config (debug/release) to use for publishing, by default is the same as passed with -c.",
    )
    parser.add_argument(
        "-p",
        "--platform-target",
        dest="platform_target",
        default=omni.repo.man.get_host_platform(),
        required=False,
        help="Platform. (default: %(default)s)",
    )
    parser.add_argument(
        "-py",
        "--python-tag",
        dest="python_tag",
        required=False,
        help="Python Tag (Version). (default: %(default)s)",
    )
    parser.add_argument("-v", "--info", dest="log_info", required=False, action="store_true")
    parser.add_argument(
        "-n",
        "--dry",
        dest="dry_run",
        required=False,
        action="store_true",
        help="Dry run.",
    )
    parser.add_argument(
        "-a",
        "--publish-all",
        dest="publish_all",
        required=False,
        action="store_true",
        help="Publish extensions for all supported configs and platforms.",
    )
    parser.add_argument(
        "-fp",
        "--from-package",
        dest="from_package",
        default=False,
        action="store_true",
        help=f"Use package from '{archive_pattern}' instead of a root folder.",
    )
    parser.add_argument(
        "-x",
        "--clean",
        dest="clean",
        default=False,
        action="store_true",
        help="Clean run (force extract package again).",
    )
    parser.add_argument(
        "--verify",
        dest="verify",
        default=False,
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

    def run_repo_tool(options: Dict, config: Dict):
        tool_config = config.get("repo_publish_exts", {})
        repo_folders = config["repo"]["folders"]

        if options.log_info:
            logger.setLevel(logging.INFO)

        options.kit_config = options.kit_config or options.config

        configs = [options.config]
        platforms = [options.platform_target]
        python_tags = [options.python_tag]
        if options.publish_all:
            configs = tool_config.get("configs")
            platforms = tool_config.get("platforms")
            python_tags = tool_config.get("python_tags")

        repo_root = repo_folders["root"]

        # stats file to save publish results between kit processes
        os.makedirs(f"{repo_root}/_build", exist_ok=True)
        stats_file = f"{repo_root}/_build/_publish_stats.json"

        tool_context = ToolContext(options, stats_file)

        # Setup kit root (package, path)
        kit_root = tool_config.get("kit_root", repo_root)
        kit_root = tool_context.resolve_tokens(kit_root, repo_root)
        if options.from_package:
            kit_archive_pattern = tool_config.get("kit_archive_pattern")
            if kit_archive_pattern:
                kit_archive_pattern = tool_context.resolve_tokens(kit_archive_pattern, repo_root)
                kit_root, _ = omni.repo.man.find_and_extract_package(kit_archive_pattern, options.clean)
        tool_context.kit_root = kit_root
        logger.info(f"kit root: {kit_root}")

        all_good = True
        for platform in platforms:
            for config in configs:
                for python_tag in python_tags:
                    print(f"running publish and verification tool for config: {config}, platform: {platform}, python version: {python_tag}")

                    options.config = config
                    options.platform_target = platform
                    options.python_tag = python_tag

                    publish_root = tool_config.get("publish_root", repo_root)
                    publish_root = tool_context.resolve_tokens(publish_root, repo_root)

                    if options.from_package:
                        archive_pattern_resolved = tool_context.resolve_tokens(archive_pattern, repo_root)
                        try:
                            publish_root, _ = omni.repo.man.find_and_extract_package(archive_pattern_resolved, options.clean)
                        except Exception as e:
                            if tool_config.get("fail_when_package_missing"):
                                logger.error(f"Failed to find and extract package: {archive_pattern_resolved} for config: {config}, platform: {platform}, python version: {python_tag}")
                                raise e
                            else:
                                logger.warning(f"Failed to find and extract package: {archive_pattern_resolved} for config: {config}, platform: {platform}, python version: {python_tag}, skipping.")

                    logger.info(f"publish root: {kit_root}")

                    all_good &= run(tool_config, tool_context, publish_root, repo_folders)

        if not options.dump:
            report_stats(stats_file, options.verify)

        if not all_good:
            sys.exit(-1)

    return run_repo_tool
