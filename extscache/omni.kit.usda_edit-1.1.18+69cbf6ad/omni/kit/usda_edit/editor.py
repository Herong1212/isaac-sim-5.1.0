# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Optional
import carb.settings
import os
import shutil
import subprocess

_created_processes = {}

def close_all_editors():
    global _created_processes
    for proc in _created_processes.values():
        proc.kill()
    _created_processes = {}

def close_editor(usda_filename: str):
    global _created_processes
    proc = _created_processes.pop(usda_filename, None)
    if proc is not None:
        proc.kill()

def _is_exe(path):
    """Return true if the path is executable"""
    return os.path.isfile(path) and os.access(path, os.X_OK)

def run_editor(usda_filename: str):
    """Open text editor with usda_filename in it"""
    global _created_processes

    # Find out which editor it's necessary to use
    # Check the settings
    settings = carb.settings.get_settings()
    editor: Optional[str] = settings.get("/app/editor")
    if not editor:
        # If settings doesn't have it, check the environment variable EDITOR.
        # It's the standard way to set the editor in Linux.
        editor = os.environ.get("EDITOR", None)
        if not editor:
            # VSCode is the default editor
            editor = "code"

    # Remove quotes because it's a common way for windows to specify paths
    if editor[0] == '"' and editor[-1] == '"':
        editor = editor[1:-1]

    if not _is_exe(editor):
        try:
            # Check if we can run the editor
            editor = shutil.which(editor)
        except shutil.Error:
            editor = None

    if not editor:
        if os.name == "nt":
            # All Windows have notepad
            editor = "notepad"
        else:
            # Try different editors on Linux
            editors = ['gedit', 'vim', 'vi', 'nano']
            for editor_ in editors:
                if shutil.which(editor_) is not None:
                    editor = editor_
                    break

    # If no edtior can be found, report this error
    if not editor:
        return False

    if os.name == "nt":
        # Using cmd on the case the editor is bat or cmd file
        call_command = ["cmd", "/c"]
    else:
        call_command = []

    call_command.append(editor)
    call_command.append(usda_filename)

    # Non blocking call
    proc = subprocess.Popen(call_command)
    _created_processes[usda_filename] = proc
    return True
