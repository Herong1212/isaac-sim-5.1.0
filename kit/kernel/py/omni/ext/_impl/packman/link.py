# Copyright 2019-2021 NVIDIA CORPORATION

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import pathlib
import subprocess
import sys

from . import errors, utils

logger = logging.getLogger("packman.link")


def _call_command(args):
    with utils.Utf8ConsoleEncoding():
        p = subprocess.Popen(
            args,
            bufsize=0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            shell=True,
        )
        out, err = p.communicate()
    # we need to return out and err as str, not bytes
    return p.returncode, out.decode("utf8", errors="ignore"), err.decode("utf8", errors="ignore")


def _sanitize_path(path):
    # Adjust paths so they match native format
    ret = path.replace("/", os.path.sep)  # posix fix
    ret = ret.rstrip(os.path.sep)  # chop of any trailing slashes
    return ret


def _create_junction_link(link_folder_path, target_folder_path):
    # target folder path can be relative but mklink interprets it as relative to CWD rather than relative to link
    # - this forces us to always make junction links absolute
    path = target_folder_path
    path = os.path.join(os.path.dirname(link_folder_path), path)
    path = os.path.normpath(path)

    logger.info(f"Creating Windows junction link '{link_folder_path}' => '{path}'")
    args = ("mklink", "/j", link_folder_path, path)
    ret_code, out, err = _call_command(args)
    if ret_code:
        # We cannot safely perform string comparisons into error messages. In other languages,
        # like Japanese, this will be quite different. So the best we can do is check the results
        # and raise/warn if we see something funky.
        try:
            target = get_link_target(link_folder_path)
        except errors.PackmanErrorFileNotLink:
            raise errors.PackmanErrorFileExists(
                f"Link '{link_folder_path}' cannot be created because it already exists as " "a different type of file."
            )
        except errors.PackmanErrorFileNotFound:
            raise errors.PackmanError(f"Failed to create junction at '{link_folder_path}' ({err})")
        if os.path.normcase(target) == os.path.normcase(path):
            return  # we are already set up
        try:
            if os.path.samefile(link_folder_path, path):
                return
        except OSError:
            # broken links can produce this error, log a warning
            logger.warning(f"Cannot verify if junction link was correctly created at '{link_folder_path}' ({err})")


def _create_symbolic_link(link_path: str, target_path: str, target_is_dir: bool):
    try:
        os.symlink(target_path, link_path, target_is_directory=target_is_dir)
    except FileExistsError as exc:
        # Another process might have beat us to it, only fail if it's not a link or
        # doesn't match
        try:
            target = get_link_target(link_path)
        except errors.PackmanErrorFileNotLink:
            raise errors.PackmanErrorFileExists(
                f"Link '{link_path}' cannot be created because it already exists as a different type of file."
            )
        if os.path.normcase(target) == os.path.normcase(target_path):
            return  # already set up
        if os.path.isabs(target_path):
            target_path_abs = target_path
        else:
            target_path_abs = os.path.join(link_path, target_path)
        try:
            if os.path.samefile(link_path, target_path_abs):
                return  # already set up
        except OSError:
            # broken links can produce this error, log a warning
            logger.warning(
                f"Cannot verify if symbolic link was correctly created at '{link_path}' " f"({utils.exc_to_str(exc)})"
            )


def _destroy_link_win(link_folder_path):
    args = ("rmdir", link_folder_path)
    ret_code, out, err = _call_command(args)
    if ret_code:
        msg = err.strip() + " (%s)" % link_folder_path
        raise RuntimeError(msg)


def get_link_target(link_folder_path: str) -> str:
    """Returns the target of the link at `link_folder_path`. If the provided path does not exist
    the call will raise PackmanErrorFileNotFound exception. If the provided path already exists and is not
    a link the call will raise PackmanErrorFileNotLink exception. If the OS does not support the link it
    will return PackmanErrorLinkUnsupported exception (Linux created link read on Windows).
    In all other cases it will return the link target.
    Note that the link target can be an absolute or relative path, depending on how the link was
    created. If relative then it's relative to the directory containing `link_folder_path`.
    """
    # with python 3.8 and beyond os.readlink now supports junctions (reparse points)
    # the only pitfall is that for reparse points it will return the path with the extended path prefix
    # that is: r"\\?\" - we need to chop this off to not cause complete chaos for users of this function.
    link_folder_path = _sanitize_path(link_folder_path)
    try:
        path = os.readlink(link_folder_path)
    except FileNotFoundError as exc:
        raise errors.PackmanErrorFileNotFound(utils.exc_to_str(exc))
    except (OSError, ValueError) as exc:
        # This is a bit of a nightmare. There are three kinds of OSErrors we can receive:
        # [WinError 4390], [WinError 1], and [Errno 22].  The there is ValueError. The ValueError
        # and [WinError 1] can possibly signal that it as link - but we cannot read its target.
        # Fortunately, there is a surefire way to determine if a file is a link, using os.stat
        # twice while toggling follow_symlinks.
        st_ino_src = os.stat(link_folder_path, follow_symlinks=False).st_ino
        try:
            st_ino_dst = os.stat(link_folder_path).st_ino
        except (OSError, FileNotFoundError):
            # unsupported links will raise an exception here, but they are still links!
            st_ino_dst = -1  # this will guarantee that it won't match st_ino_src
        if st_ino_src != st_ino_dst:
            raise errors.PackmanErrorLinkUnsupported(
                f"Path '{link_folder_path}' is a link but unsupported ({utils.exc_to_str(exc)})"
            )
        raise errors.PackmanErrorFileNotLink(
            f"Path '{link_folder_path}' exists but is not a link ({utils.exc_to_str(exc)})"
        )

    if os.name == "nt":
        if path.startswith(utils.WINDOWS_EXTENDED_PATH_PREFIX):
            path = path[4:]

    return path


def is_file_but_not_link(path: str) -> bool:
    try:
        get_link_target(path)
    except errors.PackmanErrorFileNotLink:
        return True
    except errors.PackmanError:
        pass  # these are all link related
    return False


def is_link(path: str) -> bool:
    try:
        get_link_target(path)
    except errors.PackmanErrorLinkUnsupported:
        return True
    except errors.PackmanError:
        return False
    return True


def create_link(link_path: str, target_path: str, target_is_dir=True):
    """
    Creates a symbolic link from 'link_path' to 'target_path'

    link_path: Absolute or relative path to link to create
    target_path: Absolute or relative path to target; if relative then it is relative to 'link_path'
    target_is_dir: This boolean is only used on Windows to specify if the target is a directory or file.
    """
    link_path = _sanitize_path(link_path)
    target_path = _sanitize_path(target_path)
    # Before we do anything we check to see if the link is already correctly set up:
    try:
        get_link_target(link_path)
    except errors.PackmanErrorFileNotFound:
        pass  # this is just fine
    except errors.PackmanErrorFileNotLink:
        raise errors.PackmanErrorFileExists(
            f"Link '{link_path}' cannot be created because it already exists as a different type of file (E001)"
        )
    except errors.PackmanErrorLinkUnsupported:
        # these are safe to remove
        os.remove(link_path)
    else:
        link_path_obj = pathlib.Path(link_path).absolute()  # this ensures the path is absolute
        target_path_obj = pathlib.Path(target_path)
        if target_path_obj.is_absolute():
            abs_target_path_obj = target_path_obj
        else:
            abs_target_path_obj = link_path_obj.parent / target_path_obj

        try:
            is_link_correct = os.path.samefile(link_path_obj, abs_target_path_obj)
        except OSError:
            # broken links can produce this error, we must assume that it needs to be recreated
            is_link_correct = False
        if is_link_correct:
            logger.info(f"Link path already set up '{link_path_obj}' => '{abs_target_path_obj}'")
            return
        else:
            os.remove(link_path)

    # We always try first using symlink, this can fail on Windows if admin privileges are not
    # present - we then fall back to junction point.
    try:
        _create_symbolic_link(link_path, target_path, target_is_dir=target_is_dir)
    except FileNotFoundError:
        # the link_path is invalid
        raise errors.PackmanErrorFileNotFound(f"Invalid source path for link: '{link_path}'")
    except OSError as exc:
        # Lack of privilege to create symbolic links on Windows will raise OSError.
        # There could be some other types of OSErrors, one of them is handled here above.
        # What other types exist, we simply cannot know. The best we can do is to assume that
        # this might be the problem, and if the target is a directory we can use junctions instead:
        if target_is_dir and os.name == "nt":
            _create_junction_link(link_path, target_path)
        else:
            raise errors.PackmanError(f"Failed to create link '{link_path}' ({utils.exc_to_str(exc)})")
    else:
        logger.info("Created symbolic link")


def destroy_link(link_folder_path):
    """
    Destroys an existing file system link
    :param link_folder_path: Path to linked folder to destroy.
    :return: None
    """
    link_folder_path = _sanitize_path(link_folder_path)
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if major == 3 and minor >= 8:
        # Things got a lot better and simpler in Python 3.8+
        os.remove(link_folder_path)
        return
    if os.name == "nt":
        _destroy_link_win(link_folder_path)
    else:
        os.unlink(link_folder_path)
