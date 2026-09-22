import os
import sys
import argparse
import fnmatch
import glob
import logging
import copy

from typing import Dict, Callable
from string import Template
from pathlib import Path

import omni.repo.man

logger = logging.getLogger(os.path.basename(__file__))


def generate(tool_config, options, repo_folders):
    exts_autosearch_paths = tool_config.get("exts_autosearch_paths", [])

    # Time check. Store last time we run, if of python libraries are older -> do nothing.
    time_check_file = os.path.join(repo_folders["build"], f".laststubgen_{options.config}")
    lastrun_time = os.path.getmtime(time_check_file) if os.path.isfile(time_check_file) and not options.force_run else 0

    def sub_extra_tokens(s):
        return Template(s).substitute({"config": options.config})

    def process_path(p):
        return os.path.normpath(sub_extra_tokens(p))

    search_wildcard = "*cp*.pyd" if omni.repo.man.get_host_platform() == "windows-x86_64" else "*cpython*.so"

    # Find extensions with pyd/so python libraries
    ext_all_paths = set()
    for ext_path in exts_autosearch_paths:
        ext_path = process_path(ext_path)
        search_path = ext_path + "/**/" + search_wildcard
        logger.info(f"Looking for python modules in '{search_path}'...")
        for filepath in glob.glob(search_path, recursive=True):
            filepath = os.path.normpath(filepath)
            if os.path.getmtime(filepath) < lastrun_time:
                continue
            ext_folder = Path(filepath).absolute().parts[len(Path(ext_path).absolute().parts)]
            ext_all_paths.add(os.path.join(ext_path, ext_folder))

    # allow excluding extensions
    exts_exclude = tool_config.get("exts_exclude", [])

    # build path to extensions to include/exclude
    ext_paths, ext_exclude_paths = set(), set()
    for e in ext_all_paths:
        if any(fnmatch.fnmatch(os.path.basename(e), exclude) for exclude in exts_exclude):
            ext_exclude_paths.add(e)
        else:
            ext_paths.add(e)

    # Run pybind11_stubgen script inside kit. It will find all python modules in that repo and generate stubs for them.
    if len(ext_paths) > 0:
        exts = {os.path.basename(e) for e in ext_paths}
        # allow including explicitly, only do it here to not mess with timestamp check.
        exts |= set(tool_config.get("exts_include", []))

        kit_path = process_path(tool_config.get("kit_path"))

        get_args_fn = lambda key: [sub_extra_tokens(a) for a in tool_config.get(key, [])]

        kit_extra_args = get_args_fn("kit_extra_args")

        # use exclude paths from settings, but also add explicit path to extensions that we excluded
        stubgen_exclude = get_args_fn("stubgen_exclude")
        stubgen_exclude += ext_exclude_paths

        stubgen_args = []
        stubgen_args += [arg for i in get_args_fn("stubgen_include") for arg in ("-i", f'"{i}"')]
        stubgen_args += [arg for i in stubgen_exclude for arg in ("-e", f'"{i}"')]
        if tool_config.get("stubgen_copy_back", False):
            stubgen_args += ["--copyback"]

        args = ["--disable-ext-startup", "--allow-root"]
        for ext in exts:
            args += ["--enable", ext]
        args += ["--exec", f"pybind11_stubgen.py " + " ".join(stubgen_args)]
        args += ["--/app/python/logSysStdOutput=false"]
        args += ["--/app/enableStdoutOutput=0"]
        args += ["--/plugins/carb.scripting-python.plugin/logScriptErrors=true"]
        args += ["--/log/flushStandardStreamOutput=1"]
        args += ["--/app/extensions/fastImporter/enabled=0"]
        args += ["--/app/extensions/mkdirExtFolders=0"]

        for ext_folder in tool_config.get("ext_folders", []):
            args += ["--ext-folder", process_path(ext_folder)]

        if options.log_info:
            args += ["-v"]
        args += kit_extra_args

        env = copy.deepcopy(os.environ)
        print(f"running kit for python stubs generation...")

        if "OMNI_KIT_LD_PRELOAD" in os.environ:
            # This envvar tells us to launch kit with certain libraries preloaded.
            # This is needed for ASAN and TSAN. If the process entrypoint isn't built against these
            # libraries (it won't be because it's part of carb_sdk+plugins), we need to preload
            # the libraries so they're the first libraries loaded.
            # We only set these options for the kit launch rather than the full repo_build process
            # to avoid running the sanitizers on python and other tools.
            env["LD_PRELOAD"] = f"{env['OMNI_KIT_LD_PRELOAD']}{os.pathsep}{os.getenv('LD_PRELOAD') or ''}"

            # TSAN will cause processes to fail if it detects errors, so we need to tell it to use
            # exit code 0 if it detects errors otherwise the build will fail.
            env["TSAN_OPTIONS"] = "exitcode=0"

        omni.repo.man.run_process([kit_path] + args, exit_on_error=True, env=env)

        # Check at least that some .pyi files were create in each of ext folders (exts included with config are not searched).
        any_missing = False
        for folder in ext_paths:
            if len(list(glob.glob(folder + "/**/*.pyi", recursive=True))) == 0:
                logger.error(f"Couldn't find any .pyi files in '{folder}'. Generation failed.")
                any_missing = True
        if any_missing:
            sys.exit(-1)
        else:
            print("python stub generation succeeded")

        # Update timestamp
        Path(time_check_file).touch()


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    tool_config = config.get("repo_stubgen", {})
    enabled = tool_config.get("enabled", False)
    if not enabled:
        return None

    parser.description = "Tool to generate stub files (.pyi) for python modules compiled with pybind11."
    parser.add_argument("-c", "--config", dest="config", required=False, default="debug")
    parser.add_argument("-v", "--info", dest="log_info", required=False, action="store_true")
    parser.add_argument(
        "-f",
        "--force",
        dest="force_run",
        required=False,
        action="store_true",
        help="Ignore timestamp check and run stubgen regardless.",
    )

    def run_repo_tool(options: Dict, config: Dict):
        repo_folders = config["repo"]["folders"]
        generate(tool_config, options, repo_folders)

    return run_repo_tool
