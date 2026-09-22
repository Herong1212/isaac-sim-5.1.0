# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path
from pxr import Sdf
from pxr import Tf
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from .usda_edit_utils import Singleton
from .editor import close_editor
import asyncio
import carb
import functools
import omni.kit.app
import os.path
import random
import string
import tempfile
import traceback
from omni.kit.async_engine import run_coroutine

from omni.usd import make_valid_identifier


def handle_exception(func):
    """
    Decorator to print exception in async functions
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            # We always cancel the task. It's not a problem.
            pass
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


@Singleton
class LayerWatch:
    """
    Singleton object that contains all the layer watchers. When the watcher
    is removed, the tmp file and directory are also removed.
    """

    def __init__(self):
        self.__items = {}

    def start_watch(self, identifier):
        """
        Create a temporary usda file and watch it. When this file is changed,
        the layer with the given identifier will be updated.
        """
        watch_item = self.__items.get(identifier, None)
        if not watch_item:
            watch_item = LayerWatchItem(identifier)
            self.__items[identifier] = watch_item

        return watch_item.file_name

    def stop_watch(self, identifier):
        """
        Stop watching to the temporary file created to the layer with the
        given identifier. It will remove the temporary file.
        """
        if identifier in self.__items:
            close_editor(self.__items[identifier].file_name)
            self.__items[identifier].destroy()
            del self.__items[identifier]

    def has_watch(self, identifier):
        """
        Return true if the layer with the given identifier is watched.
        """
        return identifier in self.__items

    def stop_all(self):
        """
        Stop watching for all the layers.
        """
        for _, watch in self.__items.items():
            watch.destroy()

        self.__items = {}

    @handle_exception
    async def wait_import_async(self, identifier):
        """
        Wait for the importing of the layer. It happens when the layer is
        changed.
        """
        if identifier in self.__items:
            await self.__items[identifier].wait_import_async()

    def _find_item(self, identifier):
        return self.__items.get(identifier, None)

class LayerWatchItem(FileSystemEventHandler):
    def __init__(self, identifier):
        super().__init__()

        # SdfLayer
        self.__layer = Sdf.Layer.FindOrOpen(identifier)

        # Generate random name for temp directory
        while True:
            letters = string.ascii_lowercase
            dir_name = "kit_usda_" + "".join(random.choice(letters) for i in range(8))

            tmp_path = Path(tempfile.gettempdir()).joinpath(dir_name)
            if not tmp_path.exists():
                break

        # Create temporary directory
        tmp_path.mkdir()

        # Create temporary usda file
        tmp_file_path = tmp_path.joinpath(make_valid_identifier(Path(identifier).stem) + ".usda")
        self.__file_name = tmp_file_path.resolve().__str__()
        self.__layer.Export(self.__file_name)

        # Save the timestamp
        self.__last_mtime = os.path.getmtime(self.__file_name)

        self.__build_task = None
        self.__loop = asyncio.get_event_loop()

        # Watch the file
        self.__observer = Observer()
        self.__observer.schedule(self, path=tmp_path, recursive=False)
        self.__observer.start()

        # This event is set when the layer is re-imported.
        self.__imported_event = asyncio.Event()

    @property
    def file_name(self):
        """Return the temporary file name"""
        return self.__file_name

    def on_modified(self, event):
        """Called by watchdog when the temporary file is changed"""
        # Check it's the file we are watching.
        if Path(event.src_path).resolve() != Path(self.file_name).resolve():
            return


        # Check the modification time.
        mtime = os.path.getmtime(self.file_name)
        if self.__last_mtime == mtime:
            return
        self.__last_mtime = mtime
        # Watchdog calls callback from different thread and USD doesn't like
        # it. We need to import USDA from the main thread.
        if self.__build_task:
            self.__build_task.cancel()
        self.__build_task = run_coroutine(self.__import())

    @handle_exception
    async def __import(self):
        """Import temporary file to the USD layer"""
        # Wait one frame on the case there was multiple events at the same time
        await omni.kit.app.get_app().next_update_async()

        file_name = self.file_name

        # The file extension. For anonymous layers it's ".sdf"
        format_id = f".{self.__layer.GetFileFormat().formatId}"
        if format_id == ".omni_usd" or format_id == ".usd_omni_wrapper":
            # The layer is on the omni server
            # Import is not implemented in the Omniverse file format. So we
            # clear it and transfer the content to the layer on the server.
            usda = Sdf.Layer.FindOrOpen(file_name)
            self.__layer.Clear()
            self.__layer.TransferContent(usda)

        else:
            # USD can't do cross-format Import, but it can do cross-format
            # export.
            if Path(file_name).suffix != format_id:
                # Export usda to the format of the layer.
                usda = Sdf.Layer.FindOrOpen(file_name)
                file_name = file_name + format_id
                usda.Export(file_name)

            # Import
            self.__layer.Import(file_name)

        if not self.__layer.anonymous:
            # Save if it's not an anonymous layer. So the edit goes directly to
            # the server or to the filesystem.
            self.__layer.Save()

        self.__imported_event.set()
        self.__imported_event.clear()

    @handle_exception
    async def wait_import_async(self):
        """
        Wait for the importing of the layer. It happens when the layer is
        changed.
        """
        await self.__imported_event.wait()

    def destroy(self):
        """Stop watching. Delete the temporary file and the temporary directory."""
        if self.__observer:
            self.__observer.stop()
            # Wait when it stops.
            # TODO: We need to stop all of them and then join all of them.
            self.__observer.join()
            self.__observer = None

        if self.__layer:
            self.__layer = None

        # Remove tmp file and tmp folder
        if os.path.exists(self.__file_name):
            tmp_path = Path(self.__file_name).parent
            for f in tmp_path.iterdir():
                if f.is_file():
                    f.unlink()
            tmp_path.rmdir()

        self.__imported_event.set()

    def __del__(self):
        self.destroy()
