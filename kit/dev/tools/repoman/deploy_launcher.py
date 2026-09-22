import os
import logging

import packmanapi
import repoman

repoman.bootstrap()

import omni.repo.man

REPO_FOLDERS = omni.repo.man.get_repo_paths()
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = REPO_FOLDERS["root"]

logger = logging.getLogger(os.path.basename(__file__))

KIT_ARCHIVE_PATTERN = "_builtpackages/kit-sdk@*{platform}.{config}.7z"

CONFIGS = ["release"]
PLATFORMS = ["windows-x86_64", "linux-x86_64"]
LAUNCHER_PACKAGE_NAME = "kit-sdk-launcher"


if __name__ == "__main__":
    package_root = REPO_ROOT

    platform_host = omni.repo.man.get_host_platform()
    repo_exec = f"{REPO_ROOT}/repo.bat" if platform_host == "windows-x86_64" else f"{REPO_ROOT}/repo.sh"

    # Repackage all kit-sdk packages into kit-sdk-launcher packages (7z => zip)
    for config in CONFIGS:
        for platform in PLATFORMS:
            archive_path = os.path.join(REPO_ROOT, KIT_ARCHIVE_PATTERN.format(config=config, platform=platform))
            package_root, _ = omni.repo.man.find_and_extract_package(archive_path)

            print(f"Packaging {LAUNCHER_PACKAGE_NAME}...")
            omni.repo.man.run_process(
                [repo_exec, "package", "-m", LAUNCHER_PACKAGE_NAME, "-c", config, "--platform-target", platform, "--root", package_root],
                exit_on_error=True,
            )

    # Run deploy tool now:
    omni.repo.man.run_process([repo_exec, "deploy_launcher"], exit_on_error=True)
