import argparse
from math import e
import os
import shutil
import glob
import base64
import logging
import json
import hashlib
import platform
import shutil
import sys

import packmanapi
import repoman

from functools import lru_cache

repoman.bootstrap()

import omni.repo.man
from omni.repo.man import process_args_to_cmd
from omni.repo.man.utils import ci_message

REPO_FOLDERS = omni.repo.man.get_repo_paths()
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = REPO_FOLDERS["root"]

logger = logging.getLogger(os.path.basename(__file__))

KIT_ARCHIVE_PATTERN = "_builtpackages/omniverse-kit@*{config}.7z"

#
PRODUCTS = ["kit-sdk", "coreapi"]

APPS_TO_INCLUDE_IN_KIT_SDK = {
    "omni.app.dev",
    "omni.app.editor.base",
    "omni.app.empty",
    "omni.app.full",
    "omni.app.hydra",
    "omni.app.mini-hydra",
    "omni.app.mini",
    "omni.app.viewport",
}


@lru_cache()
def get_repo_exec():
    host_platform = omni.repo.man.get_host_platform()
    return f"{REPO_ROOT}/repo.bat" if host_platform == "windows-x86_64" else f"{REPO_ROOT}/repo.sh"


def create_package(package_name, root, options, python_tag, stage_only = False) -> str:
    """Stage and create package using repo_package tool.

    It first prepares all the content in permnanent folder (staging) and then packages into an archive.
    That staging path is returned and can be used to create another package.
    """
    command = [get_repo_exec(), "package", "-m", package_name, "-c", options.config, "--root", root]
    stage_path = f"{REPO_ROOT}/_builtpackages/{package_name}-{options.config}"

    # unused at the moment, this would correspond to the custom setting in repo.toml
    # for adding the PEP python tag to the package name if we wanted it
    #if python_tag:
    #    command.extend(["--python-tag", python_tag])
    #    stage_path += f"-{python_tag}"

    if platform.system() == "Darwin":
        command.extend(["--platform-target", "macos-universal"])

    # Stage package in specified path and keep it:
    command.extend(["--temp-dir", stage_path])
    command.extend([f"--/repo_package/packages/{package_name}/keeptemp=1"])
    # If we are only staging, skip packaging (no archive will be created):
    if stage_only:
        command.extend(["--stage-only"])
    # Forward no-strip option if specified
    if options.no_strip:
        command.extend(["--no-strip"])

    print(f"Packaging {package_name}... Command: " + process_args_to_cmd(command))
    omni.repo.man.run_process(command, exit_on_error=True)

    return stage_path

def remove_unnecessary_files_from_kit_sdk(root, options):
    # Normally we specify files to be included/excluded in "package.toml".
    # It works well for a big patterns, like excluding a whole dir. But if we specify individual files in "package.toml", it
    # would affect performance of the packaging process. Ideally, we would restructure files in the repo so that those
    # that should be packaged are separated in other dir. But it is tricky to do for all "apps" that are in the same place.
    # So just specially for apps we do it here programmatically.

    def remove_if_exists(path):
        if os.path.exists(path):
            print(f"Removing: {path}")
            os.remove(path)

    # Remove apps and their shell scripts to run unless they are in the list of apps to include in the SDK
    bin_dir = omni.repo.man.resolve_tokens(root + "/_build/${platform}/${config}", extra_tokens = { "config": options.config})
    for app in glob.glob(f"{bin_dir}/apps/*"):
        stem = os.path.splitext(os.path.basename(app))[0]
        if not stem in APPS_TO_INCLUDE_IN_KIT_SDK:
            remove_if_exists(app)
            remove_if_exists(f"{bin_dir}/{stem}.bat")
            remove_if_exists(f"{bin_dir}/{stem}.sh")


def build_kit_sdk_packages(root, options, python_tag):
    # Remove unnecessary files from the root folder:
    remove_unnecessary_files_from_kit_sdk(root, options)

    # Package sdk using this package as a root:
    kit_sdk_root = create_package("kit-sdk", root=root, options=options, python_tag=python_tag)

    # Use kit sdk package content now to build kit-kernel (smaller) package out of it
    kit_kernel_root = create_package("kit-kernel", root=kit_sdk_root, options=options, python_tag=python_tag)

    # construct the new name pieces with the OpenUSD / python arguments
    usd_python_tag = f"usd_{options.usd_ver}_{options.python_ver}"

    # rename the kit-sdk and kit-kernel packages to include the OpenUSD / Python version
    print("Creating tagged packages...")
    packages_path = os.path.abspath(os.path.join(REPO_ROOT, "_builtpackages"))
    all_packages = os.listdir(packages_path)
    for filename in sorted(all_packages):
        if filename.startswith("kit-sdk") or filename.startswith("kit-kernel"):
            # we want to insert the usd_python_tag after the .gl portion
            start_index = filename.find(".gl.")
            if start_index != -1 and usd_python_tag not in filename:
                new_name = filename[0:start_index] + f".{usd_python_tag}" + filename[start_index:]
                print(f"Creating: {new_name}")
                shutil.copy(os.path.join(packages_path, filename), os.path.join(packages_path, new_name))

    # Build pip/whl package out of kit-kernel package:
    if options.config == "release":
        command = [get_repo_exec(), "python_package", "--source-root", kit_kernel_root]
        print(f"Packaging kit pip package... Command: " + process_args_to_cmd(command))
        omni.repo.man.run_process(command, exit_on_error=True)
        print(f"##teamcity[publishArtifacts '_builtpackages/*.whl']")

        # tag the wheel as well
        all_packages = os.listdir(packages_path)
        for filename in sorted(all_packages):
            if filename.endswith(".whl"):
                start_index = filename.find(f"-{python_tag}-")
                if start_index != -1:
                    new_name = filename[0:start_index] + f"-{usd_python_tag}" + filename[start_index:]
                    print(f"Creating: {new_name}")
                    shutil.copy(os.path.join(packages_path, filename), os.path.join(packages_path, new_name))

    # Make package TC artifact:
    ci_message("publishArtifacts", "_builtpackages/kit-*.7z", ci_platforms=["teamcity"])
    ci_message("publishArtifacts", "_builtpackages/kit-*.zip", ci_platforms=["teamcity"])


def build_coreapi_packages(root, options, python_tag):
    # Package coreapi using this package as a root:
    coreapi_root = create_package("coreapi", root=root, options=options, python_tag=python_tag, stage_only=True)

    with omni.repo.man.change_cwd(REPO_ROOT):
        # Download extra extensions from outside of kit repo
        cmd = [
            f"{coreapi_root}/omni.app.coreapi-alpha_headless.sh",
            "--ext-precache-mode",
            "--/app/extensions/registryEnabled=1",
            f"--/app/extensions/registryCacheFull={coreapi_root}/extscache",
            "--/app/extensions/parallelPullEnabled=1",
            "--/exts/omni.kit.registry.nucleus/cacheCreateLinks=0",
            "--/structuredLog/enableJsonStdout=false", # leaving this enabled makes reading errors hard
        ]
        print(f"Downloading (precaching) extra extensions... Command: " + process_args_to_cmd(cmd))
        omni.repo.man.run_process(cmd, exit_on_error=True)

        # Remove unused extensions using kit extension manager API (remove all disabled extensions):
        cmd = [
            f"{coreapi_root}/omni.app.coreapi-alpha_headless.sh",
            "--disable-ext-startup",
            "--exec",
            "./source/docker/coreapi-alpha-service/remove_unused_extensions.py",
        ]
        print(f"Trimming unused extensions... Command: " + process_args_to_cmd(cmd))
        omni.repo.man.run_process(cmd, exit_on_error=True)

        coreapi_root = os.path.relpath(coreapi_root)
        data_path = os.path.relpath(f"{root}/data")

        # Build docker image:
        uid = os.getuid()
        uid = uid if uid != 0 else 1001
        dockerfile_path = f"{REPO_ROOT}/source/docker/coreapi-alpha-service/Dockerfile"
        cmd = [
            "docker",
            "build",
            "-t",
            f"{options.image_tag}",
            "--build-arg",
            f"UID={uid}",
            "--build-arg",
            f"COREAPI_PACKAGE_PATH={coreapi_root}",
            "--build-arg",
            f"KIT_DATA_PATH={data_path}",
            "-f",
            dockerfile_path,
            ".",
        ]
        print(f"Building docker image... Command: " + process_args_to_cmd(cmd))
        omni.repo.man.run_process(cmd, exit_on_error=True)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", dest="config", required=False, default="release", help="Config target. (default: %(default)s)"
    )
    parser.add_argument("-x", "--clean", dest="clean", required=False, action="store_true")
    parser.add_argument(
        "-p",
        "--platform-target",
        dest="platform_target",
        default=omni.repo.man.get_host_platform(),
        required=False,
        help="Platform. (default: %(default)s)",
    )
    parser.add_argument(
        "--usd-ver",
        dest="usd_ver",
        required=True,
        help="Version of OpenUSD the package was built with in the form x.y"
    )
    parser.add_argument(
        "--python-ver",
        dest="python_ver",
        required=True,
        help="Python version used by the OpenUSD the package was built with in the form x.y"
    )
    parser.add_argument(
        "--from-package",
        dest="from_package",
        default=False,
        action="store_true",
        help=f"Use package from '{KIT_ARCHIVE_PATTERN}' instead of a root folder.",
    )
    parser.add_argument(
        "--product", dest="product", default=PRODUCTS[0], choices=PRODUCTS, help="Product name. (default: %(default)s)"
    )
    parser.add_argument(
        "--image-tag", dest="image_tag", required=False, help="Image tag to use for coreapi docker image."
    )
    parser.add_argument(
        "--no-strip",
        dest="no_strip",
        default=False,
        action="store_true",
        help=f"Disable stripping of debug symbols when preparing the package. USE FOR DEVELOPMENT PURPOSES ONLY.",
    )

    options = parser.parse_args()
    platform_target = options.platform_target

    # set python_tag to be the standard python tag for the given version
    # e.g., cp39 => .cp39
    python_tag = f"cp{options.python_ver.replace('.', '')}"
    build_flavor = f".{python_tag}" if python_tag else ""

    print(f"Packaging build flavor: 'usd {options.usd_ver} {options.python_ver}'...")

    package_root = REPO_ROOT
    if options.from_package:
        archive_path = os.path.join(
            REPO_ROOT, KIT_ARCHIVE_PATTERN.format(config=options.config)
        )
        package_root, _ = omni.repo.man.find_and_extract_package(archive_path, options.clean)

    if options.product == "kit-sdk":
        build_kit_sdk_packages(package_root, options, python_tag)
    elif options.product == "coreapi":
        build_coreapi_packages(package_root, options, python_tag)
    else:
        raise ValueError(f"Unknown product: {options.product}")


if __name__ == "__main__":
    main()
