import itertools
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

import carb.settings
import omni.kit.app

from .gitlab import get_gitlab_build_url, is_running_in_gitlab
from .teamcity import get_teamcity_build_url, is_running_in_teamcity
from .utils import call_git, get_global_test_output_path, is_running_on_ci

logger = logging.getLogger(__name__)


@lru_cache()
def get_nvdf_report_filepath() -> str:
    return os.path.join(get_global_test_output_path(), "nvdf_data.json")


def _partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries"""
    t1, t2 = itertools.tee(iterable)
    return itertools.filterfalse(pred, t1), filter(pred, t2)


def _get_json_data(report_data: List[Dict[str, str]], app_info: dict, ci_info: dict) -> Dict:
    """Transform report_data into json data

    Input:
    {"event": "start", "test_id": "omni.kit.viewport", "ext_name": "omni.kit.viewport", "start_time": 1664831914.002093}
    {"event": "stop", "test_id": "omni.kit.viewport", "ext_name": "omni.kit.viewport", "success": true, "skipped": false, "stop_time": 1664831927.1145973, "duration": 13.113}
    ...

    Output:
    {
        "omni.kit.viewport+omni.kit.viewport": {
            "app": { ... },
            "teamcity": { ... },
            "test": {
                "b_success": false,
                "d_duration": 1.185,
                "s_ext_name": "omni.kit.viewport",
                "s_name": "omni.kit.viewport",
                "s_type": "exttest",
                "ts_start_time": 1664893802530,
                "ts_stop_time": 1664893803715
                "result": { ... },
            },
        },
    }
    """

    def _aggregate_json_data(data: Dict[str, Any], config=""):
        test_id: str = data["test_id"] + config
        # increment retries count - that info is not available in the report_data, start count at 0 (-1 + 1 = 0)
        # by keeping all passed results we can know if all retries failed and set consecutive_failure to true
        if data["event"] == "start":
            retries = test_retries.get(test_id, -1) + 1
            test_retries[test_id] = retries
            data["retries"] = retries
        else:
            retries = test_retries.get(test_id, 0)
            if data["event"] == "stop":
                test_results[test_id].append(data.get("passed", False))
        test_id += f"{CONCAT_CHAR}{retries}"
        test_data = json_data.get(test_id, {}).get("test", {})
        test_data.update(data)
        # special case for time, convert it to nvdf ts_ format right away
        if "start_time" in test_data:
            test_data["ts_start_time"] = int(test_data.pop("start_time") * 1000)
        if "stop_time" in test_data:
            test_data["ts_stop_time"] = int(test_data.pop("stop_time") * 1000)
        # event is discarded
        if "event" in test_data:
            test_data.pop("event")
        # init passed to false if needed, it can be missing if a test crashes (no stop event)
        if "passed" not in test_data:
            test_data["passed"] = False
        json_data.update({test_id: {"app": app_info, "ci": ci_info, "test": test_data}})

    CONCAT_CHAR = "|"
    MIN_CONSECUTIVE_FAILURES = 3  # this value is in sync with repo.toml testExtMaxTestRunCount=3

    test_retries: Dict[str, int] = {}
    test_results = defaultdict(list)
    exttest, unittest = _partition(lambda data: data["test_type"] == "unittest", report_data)

    # add exttests - group by name + retry count
    json_data: Dict[str, Dict[str, Any]] = {}
    for data in exttest:
        _aggregate_json_data(data)
    # second loop to only keep exttest with results
    for key, data in list(json_data.items()):
        if not data.get("test", {}).get("result"):
            del json_data[key]

    # add all unittests - group by name + config + retry count
    for data in unittest:
        config = data["ext_test_id"].rsplit(CONCAT_CHAR, maxsplit=1)
        config = f"{CONCAT_CHAR}{config[1]}" if len(config) > 1 else ""
        _aggregate_json_data(data, config)
    # second loop to tag all consecutive failures (when all results are false and equal or above the retry count)
    for key, data in json_data.items():
        results = test_results.get(key.rsplit(CONCAT_CHAR, maxsplit=1)[0])
        all_failures = results and not any(results) and len(results) >= MIN_CONSECUTIVE_FAILURES - 1
        if all_failures:
            data["test"]["consecutive_failure"] = all_failures

    return json_data


def _can_post_to_nvdf() -> bool:
    # re-enable when is_app_external works
    # if omni.kit.app.get_app().is_app_external():
    #     logger.info("nvdf is disabled for external build")
    #     return False

    if not is_running_on_ci():
        logger.info("nvdf posting only enabled on CI")
        return False

    return True


def post_to_nvdf(report_data: List[Dict[str, str]]):
    if not report_data or not _can_post_to_nvdf():
        return

    try:
        app_info = get_app_info()
        ci_info = _get_ci_info()
        json_data = _get_json_data(report_data, app_info, ci_info)
        with open(get_nvdf_report_filepath(), "w") as f:
            json.dump(json_data, f, skipkeys=True, sort_keys=True, indent=4)

        # convert json_data to nvdf form and add to list
        json_array = []
        for data in json_data.values():
            data["ts_created"] = int(time.time() * 1000)
            json_array.append(to_nvdf_form(data))

        # post all results in one request
        project = "omniverse-kit-tests-results-v2"
        json_str = json.dumps(json_array, skipkeys=True)
        _post_json(project, json_str)
        # print(json_str)  # uncomment to debug

    except Exception as e:
        logger.warning(f"(post_to_nvdf) Exception occurred: {e}")


def post_coverage_to_nvdf(coverage_data: Dict[str, Dict]):
    if not coverage_data or not _can_post_to_nvdf():
        return

    try:
        app_info = get_app_info()
        ci_info = _get_ci_info()

        # convert json_data to nvdf form and add to list
        json_array = []
        for data in coverage_data.values():
            data["ts_created"] = int(time.time() * 1000)
            data["app"] = app_info
            data["ci"] = ci_info
            json_array.append(to_nvdf_form(data))

        # post all results in one request
        project = "omniverse-kit-tests-coverage-v2"
        json_str = json.dumps(json_array, skipkeys=True)
        _post_json(project, json_str)
        # print(json_str)  # uncomment to debug

    except Exception as e:
        logger.warning(f"(post_coverage_to_nvdf) Exception occurred: {e}")


def _post_json(project: str, json_str: str):
    url = f"https://gpuwa.nvidia.com/dataflow2/{project}/posting"
    resp = None

    try:
        req = urllib.request.Request(url)
        req.add_header("Content-Type", "application/json; charset=utf-8")
        json_data_bytes = json_str.encode("utf-8")  # needs to be bytes
        # use a short 10 seconds timeout to avoid taking too much time in case of problems
        resp = urllib.request.urlopen(req, json_data_bytes, timeout=10)
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        logger.warning(f"Error sending request to nvdf, response: {resp}, exception: {e}")


def query_nvdf(query: str) -> dict:
    project = "df-omniverse-kit-tests-results-v2*"
    url = f"https://gpuwa.nvidia.com/opensearch/{project}/_search"
    resp = None

    try:
        req = urllib.request.Request(url)
        req.add_header("Content-Type", "application/json; charset=utf-8")
        json_data = json.dumps(query).encode("utf-8")
        # use a short 10 seconds timeout to avoid taking too much time in case of problems
        with urllib.request.urlopen(req, data=json_data, timeout=10) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        logger.warning(f"Request error to nvdf, response: {resp}, exception: {e}")

    return {}


@lru_cache()
def _detect_kit_branch_and_mr(full_kit_version: str) -> Tuple[str, int]:
    match = re.search(r"^([^\+]+)\+([^\.]+)", full_kit_version)
    if match is None:
        logger.warning(f"Cannot detect kit SDK branch from: {full_kit_version}")
        branch = "Unknown"
    else:
        if match[2] in ["release", "production", "feature"]:
            branch = f"{match[2]}/{match[1]}"
        else:
            branch = match[2]
    # merge requests will be named mr1234 with 1234 being the merge request number
    if branch.startswith("mr") and branch[2:].isdigit():
        mr = int(branch[2:])
        # if we have a mr we don't have the branch name, try to get it from env variable
        branch = os.getenv("TARGET_BRANCH", "")
        if branch:
            # TARGET_BRANCH should look like 'refs/heads/release/23.12-105.2;release/23.12-105.2'
            if ";" in branch:
                branch = branch.split(";")[1]
        else:
            branch = os.getenv("omni.branchname", "")
    else:
        mr = 0
    return branch, mr


@lru_cache()
def _find_repository_info() -> str:
    """Get repo remote origin url, fallback on yaml if not found"""
    res = call_git(["config", "--get", "remote.origin.url"])
    remote_url = res.stdout.strip("\n") if res and res.returncode == 0 else ""
    if remote_url:
        return remote_url

    # Attempt to find the repository from yaml file
    kit_root = Path(sys.argv[0]).parent
    if kit_root.stem.lower() != "kit":
        info_yaml = kit_root.joinpath("INFO.yaml")
        if not info_yaml.exists():
            info_yaml = kit_root.joinpath("PACKAGE-INFO.yaml")
        if info_yaml.exists():
            repo_re = re.compile(r"^Repository\s*:\s*(.+)$", re.MULTILINE)
            content = info_yaml.read_text()
            matches = repo_re.findall(content)
            if len(matches) == 1:
                return matches[0].strip()
    return ""


@lru_cache()
def get_app_info() -> Dict:
    """This should be part of omni.kit.app.

    Example response:
        {
            "app_name": "omni.app.full.kit",
            "app_version": "1.0.1",
            "kit_version_full": "103.1+release.10030.f5f9dcab.tc",
            "kit_version": "103.1",
            "kit_build_number": 10030,
            "branch": "master"
            "config": "release",
            "platform": "windows-x86_64",
            "python_version": "cp37"
        }
    """
    app = omni.kit.app.get_app()
    build_version = app.get_build_version()  # eg 103.1+release.10030.f5f9dcab.tc
    settings = carb.settings.get_settings()
    info = {
        "app_name": settings.get("/app/name"),
        "app_name_full": settings.get("/app/window/title") or settings.get("/app/name"),
        "app_version": settings.get("/app/version"),
        "kit_version_full": build_version,
        "kit_version": build_version.split("+", 1)[0],
        "kit_build_number": int(build_version.rsplit(".", 3)[1]),
    }
    if is_running_in_gitlab():
        info.update(
            {
                "branch": os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME", os.getenv("CI_COMMIT_BRANCH", "")),
                "merge_request": int(os.getenv("CI_MERGE_REQUEST_IID", 0)),
                "git_hash": os.getenv("CI_COMMIT_SHORT_SHA", ""),
                "git_remote_url": os.getenv("CI_PROJECT_URL", ""),
            }
        )
    else:
        branch, mr = _detect_kit_branch_and_mr(build_version)

        info.update(
            {
                "branch": branch,
                "merge_request": mr,
                "git_hash": build_version.rsplit(".", 2)[1],
                "git_remote_url": _find_repository_info(),
            }
        )

    info.update(app.get_platform_info())
    return info


@lru_cache()
def _get_ci_info() -> Dict:
    info = {
        "ci_name": "local",
    }

    if is_running_in_gitlab():
        info.update(
            {
                "ci_name": "gitlab",
                "pipeline_id": os.getenv("CI_PIPELINE_ID", ""),
                "build_id": os.getenv("CI_JOB_ID", ""),
                "build_config_name": os.getenv("CI_JOB_NAME", ""),
                "build_url": get_gitlab_build_url(),
                "project_name": os.getenv("CI_PROJECT_NAME", ""),
                "node_id": os.getenv("CI_RUNNER_ID", ""),
            }
        )
    elif is_running_in_teamcity():
        info.update(
            {
                "ci_name": "teamcity",
                "build_id": os.getenv("TEAMCITY_BUILD_ID", ""),
                "build_config_name": os.getenv("TEAMCITY_BUILDCONF_NAME", ""),
                "build_url": get_teamcity_build_url(),
                "project_name": os.getenv("TEAMCITY_PROJECT_NAME", ""),
            }
        )

    return info


def to_nvdf_form(data: dict) -> Dict:
    """Convert dict to NVDF-compliant form.
    https://confluence.nvidia.com/display/nvdataflow/NVDataFlow#NVDataFlow-PostingPayload
    """
    reserved = {"ts_created", "_id"}
    prefixes = {str: "s_", float: "d_", int: "l_", bool: "b_", list: "obj_", tuple: "obj_"}
    key_illegal_pattern = "[!@#$%^&*.]+"

    def _convert(d):
        result = {}
        key = value = None

        try:
            for key, value in d.items():
                key = re.sub(key_illegal_pattern, "_", key)
                if key in reserved:
                    result[key] = value
                elif key.startswith("ts_"):
                    result[key] = value
                elif isinstance(value, dict):
                    # note that nvdf docs state this should prefix with 'obj_', but without works also.
                    # We choose not to as it matches up with existing fields from kit benchmarking
                    result[key] = _convert(value)
                elif hasattr(value, "__dict__"):
                    # support for Classes
                    result[key] = _convert(value.__dict__)
                elif isinstance(value, (list, tuple)):
                    if not value:
                        result[key] = value
                    elif isinstance(value[0], dict):
                        # note that nvdf docs state this should prefix with 'obj_', but without works also.
                        # We choose not to as it matches up with existing fields from kit benchmarking
                        result[key] = [_convert(v) for v in value]
                    else:
                        _type = type(value[0]) if value else str
                        result[prefixes[_type] + key] = value
                elif isinstance(value, (str, float, int, bool)):
                    result[prefixes[type(value)] + key] = value
                else:
                    raise ValueError(f"Type {type(value)} not supported in nvdf (data: {data})")
            return result
        except Exception as e:
            raise Exception(f"Exception for {key} {value} -> {e}")

    return _convert(data)


def remove_nvdf_form(data: dict):
    prefixes = ["s_", "d_", "l_", "b_"]

    def _convert(d):
        result = {}
        key = value = None

        try:
            for key, value in d.items():
                if isinstance(value, dict):
                    # note that nvdf docs state this should prefix with 'obj_', but without works also.
                    # We choose not to as it matches up with existing fields from kit benchmarking
                    result[key] = _convert(value)
                elif hasattr(value, "__dict__"):
                    # support for Classes
                    result[key] = _convert(value.__dict__)
                elif isinstance(value, (list, tuple, str, float, int, bool)):
                    if key[:2] in prefixes:
                        key = key[2:]
                    result[key] = value
                    if isinstance(value, (list, tuple)):
                        for v in value:
                            if isinstance(v, dict):
                                result[key] = [_convert(v) for v in value]
                                if isinstance(value, tuple):
                                    result[key] = tuple(result[key])
                else:
                    raise ValueError(f"Type {type(value)} not supported in nvdf (data: {data})")
            return result
        except Exception as e:
            raise Exception(f"Exception for {key} {value} -> {e}")

    return _convert(data)
