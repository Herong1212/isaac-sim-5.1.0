import os
import sys
import argparse

import packmanapi

try:
    import repoman

    repoman.bootstrap()
    import omni.repo.man
    from omni.repo.man.utils import ci_message
except Exception as exc:
    print(exc)
    print("Failed to bootstrap repo man")
    sys.exit(1)


ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")
VERSION = open(f"{ROOT_DIR}/VERSION").read()
MAJOR_VERSION = os.getenv("MAJOR_VERSION", VERSION)


def run_command():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepbuild", dest="prepbuild", action="store_true")
    parser.add_argument("--buildnumber", dest="buildnumber", action="store_true")
    options = parser.parse_args()

    # Preparing and early exitting the TeamCity build
    if options.prepbuild or options.buildnumber:
        build_number = omni.repo.man.build_number.generate_build_number_from_file("VERSION")
        ci_message("setParameter", name="build.number", value=build_number, ci_platforms=["teamcity"])
        ci_message("buildNumber", build_number, ci_platforms=["teamcity"])

    if options.buildnumber:
        print(f"Version: {build_number}")
        sys.exit(0)


if __name__ == "__main__":
    try:  # need to clean this up a little, but a job for another day
        run_command()
    except Exception as exc:
        ci_message("buildStatus", text="Error generating build number", status="ERROR", ci_platforms=["teamcity"])
        sys.exit(1)
