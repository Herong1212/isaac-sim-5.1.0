import os

from functools import lru_cache

import carb
import carb.tokens

from .common import is_windows, info_exec_time, run_process, _print, _print_mt


@lru_cache()
def get_packman_dir():
    tokens = carb.tokens.get_tokens_interface()
    return tokens.resolve("${kit}/dev/tools/packman")


@lru_cache()
def get_packman_path():
    packman = get_packman_dir() + "/packman"
    if is_windows():
        packman += ".cmd"
    return packman


@lru_cache()
def get_packman_python_path():
    python = get_packman_dir() + "/python"
    python += ".bat" if is_windows() else ".sh"
    return python


def resolve_packman_url(archive_local: str):
    archive_name = os.path.splitext(os.path.basename(archive_local))[0]
    args = [get_packman_path(), "resolve", archive_name, "-r=cloudfront"]
    carb.log_info(f"resolving using packman with cmd: {args}")
    rcode, output = run_process(args)
    if rcode != 0:
        carb.log_info(f"Failed resolving url for packman package. Output: {output}")
        return None

    carb.log_info(f"packman resolve succeeded, output: {output}")
    try:
        lines = output.strip().split("\n")
        archive_path = lines[-1]
        if not archive_path.startswith("http://") and not archive_path.startswith("https://"):
            raise Exception(f"doesn't look like url: {archive_path}")

        # WAR for S3 links not supporting "+", amazon treats it as space.
        archive_path = archive_path.replace("+", "%2B")
        return archive_path
    except Exception as e:
        carb.log_info(f"Failed resolving url for packman package: {archive_name}. Error: {e}")
        return None


@info_exec_time()
def push_to_packman(archive_local: str):
    args = [get_packman_path(), "push", archive_local, "-r=cloudfront"]
    _print_mt(f"pushing using packman with cmd: {args}")
    rcode, output = run_process(args)
    if rcode == 0:
        carb.log_info(f"packman push succeeded, output:\n{output}")
    else:
        # Failure here still can be ok, if package already present. Try resolve link
        carb.log_warn(f"packman push failed, output:\n{output}")

    archive_path = resolve_packman_url(archive_local)
    if not archive_path:
        carb.log_error(f"Failed resolving url for packman package: {archive_local}.")
    return archive_path

