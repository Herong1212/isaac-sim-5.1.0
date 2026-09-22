# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import asyncio
import omni.kit.app
import omni.ui as ui
from omni.ui import scene as sc

from typing import Callable, Coroutine, Any, Dict
from carb import log_warn, log_info
from .style import get_style, ICON_ROOT


def exec_after_redraw(callback: Callable, wait_frames: int = 2) -> Any:
    """
    Execute a function after redrawing the dialog. 
    This is useful for unit tests where you want to wait for a dialog to be redrawn 
    and then call it in the next update frame.
    
    Args:
        callback (Callable): The function to execute after redrawing the dialog.
                   Function signature is void callback().
         
    Keyword Args:
        wait_frames (int): The number of frames to wait before executing the callback.
                   default value is 2.
    
    Returns: 
        :obj: 'asyncio.Task': future that will fire when the callback is executed.
    """
    async def exec_after_redraw_async(callback: Callable, wait_frames: int) -> asyncio.Task:
        try:
            # Wait a few frames before executing
            for _ in range(wait_frames):
                await omni.kit.app.get_app().next_update_async()
            callback()
        except asyncio.CancelledError:
            return
        except Exception as e:
            # Catches exceptions from this delayed function call; often raised by unit tests where the dialog is being rapidly
            # created and destroyed. In this case, it's not worth the effort to relay the exception and have it caught, so better 
            # warn and carry on.
            log_warn(f"Warning: Ignoring a minor exception: {str(e)}")

    return asyncio.ensure_future(exec_after_redraw_async(callback, wait_frames))


def get_user_folders_dict() -> Dict[str, str]:
    """
    Gets dictionary of user folders.

    Returns:
        dict: dictionary of user folders as name path pairs.
    """
    from pathlib import Path
    from uuid import UUID

    user_folders = {}
    subfolders = ["Desktop", "Documents", "Downloads", "Pictures"]
   
    # http://msdn.microsoft.com/en-us/library/windows/desktop/dd378457.aspx
    folder_IDs = [
        UUID('{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}'),
        UUID('{FDD39AD0-238F-46AF-ADB4-6C85480369C7}'),
        UUID('{374DE290-123F-4565-9164-39C4925E467B}'),
        UUID('{33E28130-4E1E-4676-835A-98395C3BC3BB}'),
    ]
    name_id_map = dict(zip(subfolders, folder_IDs))

    for subfolder in subfolders:
        path = os.path.join(Path.home(), subfolder)
        if os.name == 'nt':
            # windows system's version >= windows 10
            # OM-111583: Need to use windll interface to get real user folder path
            import ctypes
            from ctypes import windll, wintypes

            class GUID(ctypes.Structure):
                _fields_ = [
                    ("data1", wintypes.DWORD),
                    ("data2", wintypes.WORD),
                    ("data3", wintypes.WORD),
                    ("data4", wintypes.BYTE * 8)
                ]

                def __init__(self, uuid):
                    ctypes.Structure.__init__(self)
                    self.data1, self.data2, self.data3, \
                        self.data4[0], self.data4[1], rest = uuid.fields
                    for i in range(2, 8):
                        self.data4[i] = rest>>(8-i-1)*8 & 0xff

            # http://msdn.microsoft.com/en-us/library/windows/desktop/bb762188.aspx
            try:
                _SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
                _SHGetKnownFolderPath.argtypes = [
                    ctypes.POINTER(GUID), wintypes.DWORD,
                    wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
                ]
                pathptr = ctypes.c_wchar_p()
                guid = GUID(name_id_map[subfolder])
                if _SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)) == 0:
                    path = pathptr.value
            except:
                log_warn("Not support get known folder path")
        if os.path.exists(path):
            user_folders[subfolder] = path.replace("\\", "/")

    return user_folders


class SingletonTask:
    def __init__(self):
        self._task = None

    def destroy(self):
        """ Called when the task is no longer needed. """
        self.cancel_task()

    def __del__(self):
        self.destroy()

    async def run_task(self, task: Coroutine) -> Any:
        """
        Run a task and return its result. 
        Args:
            task (Coroutine): The task to run. Must be a coroutine.
        
        Returns: 
            Any: The result of the task. 
        """
        if self._task:
            self.cancel_task()
            await omni.kit.app.get_app().next_update_async()

        self._task = asyncio.create_task(task)
        try:
            return await self._task
        except asyncio.CancelledError:
            log_info(f"Cancelling task ... {self._task}")
            raise
        except Exception as e:
            raise
        finally:
            self._task = None

    def cancel_task(self):
        """ Cancel the task associated with this task if any. """
        if self._task is not None:
            self._task.cancel()
        self._task = None


class Spinner(sc.Manipulator):
    """ An ov logo rotator with a given speed."""
    def __init__(self, rotation_speed: int = 2):
        super().__init__()
        self.__deg = 0
        self.__rotation_speed = rotation_speed

    def on_build(self):
        self.invalidate()
        self.__deg = self.__deg % 360
        transform = sc.Matrix44.get_rotation_matrix(0, 0, -self.__deg, True)
        with sc.Transform(transform=transform):
            sc.Image(f"{ICON_ROOT}/ov_logo.png", width=1.5, height=1.5)
        self.__deg += self.__rotation_speed


class AnimatedDots():
    def __init__(self, period : int = 30, phase : int = 3, width : int = 10, height : int = 20):
        """
        Initialize the event loop. 
        
        Keyword Args:
            period(int): The time between updates in seconds (30)
            phase(int): The phase of the update ( 0 - 3 )
            width(int): The width of the UI ( default 10 )
            height(int): The height of the UI ( default 20 )
        """
        self._period = period
        self._phase = phase
        self._stop_event = asyncio.Event()
        self._build_ui(width=width, height=height)

    def _build_ui(self, width : int = 0, height: int = 0):
        self._label = ui.Label("...", width=width, height=height)
        asyncio.ensure_future(self._inf_loop())

    async def _inf_loop(self):
        counter = 0
        while not self._stop_event.is_set():
            await omni.kit.app.get_app().next_update_async()
            if self._stop_event.is_set():
                break
            # Animate text
            phase = counter // self._period % self._phase + 1
            self._label.text = phase * "."
            counter += 1

    def __del__(self):
        self._stop_event.set()


class LoadingPane(SingletonTask):
    """ A loading pane frame used to play during loading file from remote"""
    def __init__(self, frame):
        super().__init__()
        self._frame = frame
        self._scene_view = None
        self._spinner = None
        self._build_ui()

    def _build_ui(self):
        with self._frame:
            with ui.ZStack(style=get_style()):
                ui.Rectangle(style_type_name_override="LoadingPane.Bg")
                with ui.VStack(style=get_style(), spacing=5):
                    ui.Spacer(height=ui.Percent(10))
                    with ui.HStack(height=ui.Percent(50)):
                        ui.Spacer()
                        self._scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT)
                        with self._scene_view.scene:
                            self._spinner = Spinner()
                        ui.Spacer()
                    with ui.HStack(spacing=0):
                        ui.Spacer()
                        ui.Label("Changing Directory", height=20, width=0)
                        AnimatedDots()
                        ui.Spacer()
                    with ui.HStack(height=ui.Percent(20)):
                        ui.Spacer()
                        ui.Button(
                            "Cancel",
                            width=100, height=20,
                            clicked_fn=lambda: self.hide(),
                            style_type_name_override="LoadingPane.Button",
                            alignment=ui.Alignment.CENTER,
                            identifier="LoadingPaneCancel"
                        )
                        ui.Spacer()
                    ui.Spacer(height=ui.Percent(10))

    def show(self):
        """  Show the loading frame. """
        self._frame.visible = True

    def hide(self):
        """ Hide the loading frame."""
        self.cancel_task()
        self._frame.visible = False

    def destroy(self):
        """Destroy the loading frame. """
        if self._spinner:
            self._spinner.invalidate()
            self._spinner = None
        if self._scene_view:
            self._scene_view.destroy()
            self._scene_view = None
        if self._frame:
            self._frame.visible = False
            self._frame.destroy()
            self._frame = None
        super().destroy()
