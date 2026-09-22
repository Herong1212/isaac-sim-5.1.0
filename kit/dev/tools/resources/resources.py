import packmanapi
import sys
import os
import shutil
import urllib.request
import json

MY_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.normpath(os.path.join(MY_DIR, "..", ".."))
BUILD_DIR = os.path.normpath(os.path.join(REPO_DIR, "_build"))
RESOURCES_DIR = os.path.join(BUILD_DIR, "resources")
RESOURCES_OVERRIDE_DIR = os.path.join(BUILD_DIR, "resources.override")
RESOURCES_DEPS_FILE = os.path.join(REPO_DIR, "deps", "resources.packman.xml")


def exit_with_error(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)


def stage():
    if os.path.exists(RESOURCES_OVERRIDE_DIR):
        exit_with_error(
            "Folder '%s' already exists - must remove using 'clean' command before using 'stage' command!"
            % RESOURCES_OVERRIDE_DIR
        )
    packmanapi.pull(RESOURCES_DEPS_FILE)
    shutil.copytree(RESOURCES_DIR, RESOURCES_OVERRIDE_DIR)
    print("Resources have been staged in '%s' - please update this folder with your changes." % RESOURCES_OVERRIDE_DIR)


def publish():
    if not os.path.exists(RESOURCES_OVERRIDE_DIR):
        exit_with_error(
            "Folder '%s' not found. First stage resources using 'stage' command and update them!"
            % RESOURCES_OVERRIDE_DIR
        )
    hash = packmanapi.hash(RESOURCES_OVERRIDE_DIR)
    hash_short = hash[:8]

    try:
        packmanapi.publish(RESOURCES_OVERRIDE_DIR, ["cloudfront"], "omniverse_kit_resources@" + hash_short)
    except packmanapi.PackmanErrorFileExists:
        print("Package is identical to existing package, no need to upload it.")

    sys.stdout.write("Updating '%s' ..." % RESOURCES_DEPS_FILE)
    with open(RESOURCES_DEPS_FILE, "r") as input_file:
        file_contents = input_file.read()

    keyword = 'version="'
    keyword_len = len(keyword)
    ix = file_contents.find(keyword)
    if ix == -1:
        exit_with_error("Couldn't find version to change in '%s'" % RESOURCES_DEPS_FILE)

    begin_version = ix + keyword_len
    end_version = ix + keyword_len + len(hash_short)
    file_contents = file_contents[:begin_version] + hash_short + file_contents[end_version:]

    with open(RESOURCES_DEPS_FILE, "w") as output_file:
        output_file.write(file_contents)
    sys.stdout.write(" done\n")


def clean():
    if os.path.exists(RESOURCES_OVERRIDE_DIR):
        shutil.rmtree(RESOURCES_OVERRIDE_DIR)


def main():
    help_str = """usage: {stage|publish|clean}
    stage:      Stage the resources directory into '_build/resources.override'.
                This will fail if kit has not been built yet.
                Changes to resources can be made into this folder before publishing.
    publish:    Publish the staged changes as a new resources package.
                This will update 'deps/resources.packman.xml' with the new
                resources package version that was published.
                This will fail if a '_build/resources.override' folder was not
                created previously with the 'stage' command.
    clean:      This will remove the staged resources directory"""

    if len(sys.argv) < 2:
        exit_with_error(help_str)

    cmd = sys.argv[1]
    if cmd == "stage":
        stage()
    elif cmd == "publish":
        publish()
    elif cmd == "clean":
        clean()
    else:
        exit_with_error("Unknown argument '" + cmd + "'\n" + help_str)


if __name__ == "__main__" or __name__ == "__mp_main__":
    main()
