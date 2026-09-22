# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""USD File interaction for Omniverse Kit.

:mod:`omni.kit.window.file` provides util functions to new/open/save/close USD files. It handles file picking dialog and prompt for unsaved stage.
"""
__all__ = ["FileWindowExtension","FileUtils", "get_file_utils_instance",
    "get_instance", "new", "open", "open_stage", "open_with_new_edit_layer", "reopen",
    "save", "save_as", "close", "save_layers", "prompt_if_unsaved_stage", "add_reference",
    "register_open_stage_addon", "register_open_stage_complete", "IGNORE_UNSAVED_STAGE"
]
import os
import time
import traceback
import asyncio
from typing import Awaitable, Callable, List, Optional
import carb
import omni.ext
import omni.usd
import omni.client
import omni.kit.app
import omni.kit.helper.file_utils as file_utils
from carb.eventdispatcher import get_eventdispatcher

from functools import partial
from omni.kit.helper.file_utils import asset_types
from omni.kit.window.file_importer import get_file_importer
from omni.kit.window.file_exporter import get_file_exporter
try:
    from omni.kit.widget.nucleus_connector import connect
    have_nucleus = True
except ModuleNotFoundError:
    have_nucleus = False
from .prompt_ui import Prompt
from .read_only_options_window import ReadOnlyOptionsWindow
from .app_ui import AppUI, DialogOptions, SaveOptionsDelegate, OpenOptionsDelegate
from .file_actions import register_actions, deregister_actions
from pxr import Tf, Sdf, Usd, UsdGeom, UsdUtils

_file_util_instance = None
IGNORE_UNSAVED_ON_EXIT_PATH = "/app/file/ignoreUnsavedOnExit"
IGNORE_UNSAVED_STAGE = "/app/file/ignoreUnsavedStage"
SHOW_UNSAVED_LAYERS_DIALOG = "/persistent/app/file/save/showUnsavedLayersDialog"


class _CheckpointCommentContext:

    def __init__(self, comment: str):
        self._comment = comment

    def __enter__(self):
        try:
            import omni.usd_resolver
            omni.usd_resolver.set_checkpoint_message(self._comment)
        except Exception as e:
            carb.log_error(f"Failed to import omni.usd_resolver: {str(e)}.")

        return self

    def __exit__(self, type, value, trace):
        try:
            import omni.usd_resolver
            omni.usd_resolver.set_checkpoint_message("")
        except Exception:
            pass


class _CallbackRegistrySubscription:
    """
    Simple subscription.

    _Event has callback while this object exists.
    """

    def __init__(self, callback_list: List, callback: Callable):
        """
        Save the callback in the given list.
        """
        self.__callback_list: List = callback_list
        self.__callback = callback
        callback_list.append(callback)

    def __del__(self):
        """Called by GC."""
        self.__callback_list.remove(self.__callback)


class FileWindowExtension(omni.ext.IExt):
    """ File window extension interface. """

    def on_startup(self, ext_id):
        """
        Initialize the extension.
        Args:
            ext_id(str): Extension identifier.
        """
        self._file_utils = FileUtils()
        self._file_utils.on_startup()
        self._ext_name = omni.ext.get_extension_name(ext_id)
        register_actions(self._ext_name)

    def on_shutdown(self):
        """ Cleanup the extension. """
        deregister_actions(self._ext_name)
        self._file_utils.on_shutdown()

class FileUtils:
    """ File utils class to provide file relate function. """

    def on_startup(self):
        """
        Initialize the FileUtils.
        """
        global _file_util_instance
        _file_util_instance = self

        self._open_stage_callbacks: List[Callable[[], None]] = []
        self._open_stage_complete_callbacks: List[Callable[[], None]] = []

        self.ui_handler = None
        self._task = None
        self._unsaved_stage_prompt = None
        self._file_existed_prompt = None
        self._open_readonly_usd_prompt = None
        self._app = omni.kit.app.get_app()
        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(IGNORE_UNSAVED_ON_EXIT_PATH, False)
        self.ui_handler = AppUI()
        self._save_options = None
        self._open_options = None



        def on_event(_):
            ignore_unsaved_file_on_exit = self._settings.get(IGNORE_UNSAVED_ON_EXIT_PATH)
            usd_context = omni.usd.get_context()
            if not ignore_unsaved_file_on_exit and usd_context.can_close_stage() and usd_context.has_pending_edit():
                self._app.try_cancel_shutdown("Interrupting shutdown - closing stage first")
                # OM-52366: fast shutdown will not close stage but post quit directly.
                fast_shutdown = carb.settings.get_settings().get("/app/fastShutdown")
                self.close(lambda *args: omni.kit.app.get_app().post_quit(), fast_shutdown=fast_shutdown)

        self._shutdown_subs = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_POST_QUIT,
            on_event=on_event, observer_name="window.file shutdown hook", order=0
        )

        self._stage_event_subs = get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.OPENING),
            on_event=self._on_stage_opening, observer_name="omni.kit.window.file"
        )

    def _on_stage_opening(self, _):
        # If a new stage is opening with scripting, it should hide the prompts of last opened stage.
        if self._unsaved_stage_prompt:
            self._unsaved_stage_prompt.destroy()
            self._unsaved_stage_prompt = None

        if self._file_existed_prompt:
            self._file_existed_prompt.destroy()
            self._file_existed_prompt = None

        if self._open_readonly_usd_prompt:
            self._open_readonly_usd_prompt.destroy()
            self._open_readonly_usd_prompt = None

    def on_shutdown(self):
        """ Cleanup the extension. """
        self._stage_event_subs = None
        self._shutdown_subs = None
        self._save_options = None
        self._open_options = None
        if self._task:
            self._task.cancel()
            self._task = None
        if self._unsaved_stage_prompt:
            self._unsaved_stage_prompt.destroy()
        self._unsaved_stage_prompt = None
        if self._file_existed_prompt:
            self._file_existed_prompt.destroy()
        self._file_existed_prompt = None
        if self._open_readonly_usd_prompt:
            self._open_readonly_usd_prompt.destroy()
        self._open_readonly_usd_prompt = None
        global _file_util_instance
        _file_util_instance = None
        if self.ui_handler:
            self.ui_handler.destroy()
        self.ui_handler = None

    def stop_timeline(self):
        """ Stop the timeline. """
        try:
            import omni.timeline

            timeline = omni.timeline.get_timeline_interface()
            if timeline:
                timeline.stop()
            else:
                carb.log_warn(f"Failed to stop timeline, get_timeline_interface() return None")
        except ModuleNotFoundError:
            carb.log_warn(f"Failed to stop timeline, omni.timeline not loaded")

    def new(self, template=None):
        """
        Create a new USD stage. If currently opened stage is dirty, a prompt will show to let you save it.

        Keyword Args:
            template (Optional[str]): the template to use.
        """
        self.stop_timeline()

        async def new_stage_job():
            # FIXME: Delay two frames to center prompt.
            await self._app.next_update_async()
            await self._app.next_update_async()
            with Prompt("Please Wait", "Creating new stage...", [], [], True):
                await self._app.next_update_async()  # Making sure prompt shows
                try:
                    import omni.kit.stage_template.core

                    await omni.kit.stage_template.core.new_stage_async(template=template)
                except ModuleNotFoundError:
                    if omni.usd.get_context().can_close_stage():
                        await omni.usd.get_context().close_stage_async()
                    await omni.usd.get_context().new_stage_async()
                await self._app.next_update_async()  # Wait anther frame for StageEvent.OPENED to be handled

        self.prompt_if_unsaved_stage(lambda *_: self._exclusive_task_wrapper(new_stage_job))

    def open(self, open_loadset=omni.usd.UsdContextInitialLoadSet.LOAD_ALL):
        """
        Bring up a file picker to choose a USD file to open. If currently opened stage is dirty, a prompt will show to let you save it.

        Keyword Args:
            open_loadset (:obj:`omni.usd.UsdContextInitialLoadSet`): initial load set enum, LOAD_ALL or LOAD_NONE.
        """
        self.stop_timeline()

        def open_handler(loadset: int, filename: str, dirname: str, selections: List[str]):
            if not filename.startswith('\\\\'):
                filename = filename.replace("\\", "/")
            if ':/' in filename or filename.startswith('\\\\'):
                # Filename is a pasted fullpath.  The first test finds paths that start with 'C:/' or 'omniverse://';
                # the second finds MS network paths that start like '\\analogfs\VENDORS\...'
                path = filename
            else:
                if dirname and dirname[-1] != '/':
                    dirname = f"{dirname}/"
                path = omni.client.make_absolute_url_if_possible(dirname, filename)

            result, entry = omni.client.stat(path)
            if result != omni.client.Result.OK:
                carb.log_warn(f"Failed to stat '{path}', attempting to open in read-only mode.")
                read_only = True
            else:
                # https://nvidia-omniverse.atlassian.net/browse/OM-45124
                read_only = entry.access & omni.client.AccessFlags.WRITE == 0

            if read_only:
                def _open_with_edit_layer():
                    self.open_with_new_edit_layer(path, open_loadset)

                def _open_original_stage():
                    self.open_stage(path, open_loadset, open_options=self._open_options)

                self._show_readonly_usd_prompt(_open_with_edit_layer, _open_original_stage)
            else:
                self.open_stage(path, open_loadset=loadset, open_options=self._open_options)

        file_importer = get_file_importer()
        if file_importer:
            file_importer.show_window(
                title="Open File",
                import_button_label="Open File",
                import_handler=partial(open_handler, open_loadset),
                should_validate=True,
            )
            if self._open_options is None:
                self._open_options = OpenOptionsDelegate()
            file_importer.add_import_options_frame("Options", self._open_options)

    def open_stage(
        self, path: str, open_loadset=omni.usd.UsdContextInitialLoadSet.LOAD_ALL,
        open_options: OpenOptionsDelegate = None
    ):
        """
        Open stage. If the current stage is dirty, a prompt will show to let you save it.

        Args:
            path(str): the path to the stage file to open.
        Keyword Args:
            open_loadset(:obj:`omni.usd.UsdContextInitialLoadSet`): initial load set enum, LOAD_ALL or LOAD_NONE.
            open_options(:obj:`OpenOptionsDelegate`): if set, use the open_loadset setting from options.
        """
        self.stop_timeline()
        ui_handler = self.ui_handler
        checkbox = None
        if open_options:
            checkbox = open_options.should_load_payload()
            if not checkbox: # open with payloads disabled
                open_loadset =  omni.usd.UsdContextInitialLoadSet.LOAD_NONE

        async def open_stage_job():
            # FIXME: Delay two frames to center prompt.
            await self._app.next_update_async()
            await self._app.next_update_async()
            prompt = Prompt("Please Wait", f"Opening {path}...", [], [], True, self._open_stage_callbacks, self._open_stage_complete_callbacks)
            prompt._window.width = 415
            with prompt:
                context = omni.usd.get_context()
                start_time = time.monotonic()
                result, err = await context.open_stage_async(path, open_loadset)
                success = True
                if not result or context.get_stage_state() != omni.usd.StageState.OPENED:
                    success = False
                    carb.log_error(f"Failed to open stage {path}: {err}")
                    ui_handler.show_open_stage_failed_prompt(path)
                else:
                    stage = context.get_stage()
                    identifier = stage.GetRootLayer().identifier
                    if not stage.GetRootLayer().anonymous:
                        omni.kit.app.queue_event(file_utils.FILE_OPENED_GLOBAL_EVENT, file_utils.FileEventModel(url=identifier).dict())

                open_duration = time.monotonic() - start_time
                omni.kit.app.send_telemetry_event("omni.kit.window.file@open_stage", duration=open_duration, data1=path, value1=float(success))

        async def open_stage_async():
            result, _ = await omni.client.stat_async(path)
            if result == omni.client.Result.OK:
                FileUtils._exclusive_task_wrapper(open_stage_job)
                return

            # Attempt to connect to nucleus server
            broken_url = omni.client.break_url(path)
            if broken_url.scheme == 'omniverse':
                server_url = omni.client.make_url(scheme='omniverse', host=broken_url.host)
                if have_nucleus:
                    connect(broken_url.host, server_url,
                        on_success_fn=lambda *_: FileUtils._exclusive_task_wrapper(open_stage_job),
                        on_failed_fn=lambda *_: carb.log_error(f"Invalid stage URL: {path}")
                    )
            else:
                carb.log_error(f"Invalid stage URL: {path}")

        self.prompt_if_unsaved_stage(lambda *_: asyncio.ensure_future(open_stage_async()))

    def _show_readonly_usd_prompt(self, ok_fn, middle_fn):
        if self._open_readonly_usd_prompt:
            self._open_readonly_usd_prompt.destroy()

        self._open_readonly_usd_prompt = ReadOnlyOptionsWindow(ok_fn, middle_fn)
        self._open_readonly_usd_prompt.show()

    def _show_file_existed_prompt(self, path, on_confirm_fn, on_cancel_fn=None):
        file_name = os.path.basename(path)
        if self._file_existed_prompt:
            self._file_existed_prompt.destroy()
        self._file_existed_prompt = Prompt(
            f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Overwrite',
            f"File {file_name} already exists, do you want to overwrite it?",
            ["OK", "Cancel"],
            [on_confirm_fn, None],
            False,
        )
        self._file_existed_prompt.show()

    def open_with_new_edit_layer(
        self, path: str, open_loadset: int = omni.usd.UsdContextInitialLoadSet.LOAD_ALL, callback: Callable[[], None] = None
    ):
        """
        Open stage and create a new edit layer.

        Args:
            path (str): path to open the stage.
        Keyword Args:
            open_loadset (:obj:`omni.usd.UsdContextInitialLoadSet`): initial load set enum, LOAD_ALL or LOAD_NONE.
            callback: (Callable): callback to call after creating stage. Function Signature:
                callback() -> None
        """
        self.stop_timeline()

        def create_handler(stage_path: str, callback: Callable, filename: str, dirname: str,
                           extension: str = None, selections: List[str] = []):
            # Allow incoming directory as /path/to/dir or /path/to/dir/
            if dirname and dirname[-1] != '/':
                dirname = f"{dirname}/"
            edit_layer_path = omni.client.make_absolute_url_if_possible(dirname, f"{filename}{extension}")
            self.create_stage(edit_layer_path, stage_path, callback=callback)

        def create_edit_layer(stage_path: str, callback: Callable):
            file_exporter = get_file_exporter()
            if file_exporter:
                dirname = omni.client.combine_urls(stage_path, ".")
                if dirname and dirname[-1] != '/':
                    dirname += "/"

                if Sdf.Layer.IsAnonymousLayerIdentifier(stage_path):
                    basename = Sdf.Layer.GetDisplayNameFromIdentifier(stage_path)
                else:
                    url = omni.client.break_url(stage_path)
                    basename = os.path.basename(url.path)
                edit_layer_path = omni.client.make_absolute_url_if_possible(
                    dirname, f"{os.path.splitext(basename)[0]}_edit"
                )

                file_exporter.show_window(
                    title="Create Edit Layer",
                    export_button_label="Save",
                    export_handler=partial(create_handler, stage_path, callback),
                    filename_url=edit_layer_path,
                )

        self.prompt_if_unsaved_stage(lambda: create_edit_layer(path, callback))

    def create_stage(self, edit_layer_path: str, file_path: str, callback: Callable = None):
        """
        Create a stage with edit layer from paths.

        Args:
            edit_layer_path (str): path to create the edit layer.
            file_path (str): path to create the stage.
        Keyword Args:
            callback: (Callable): callback to call after creating stage. Function Signature:
                callback() -> None
        """
        self.stop_timeline()

        async def create_stage_async(edit_layer_path: str, stage_path: str, callback: Callable[[], None]):
            # OMPE-48320: make sure edit_layer_path start with "file:/" if it is a file url
            edit_layer_path = omni.client.make_file_url_if_possible(edit_layer_path)
            edit_layer = Sdf.Layer.FindOrOpen(edit_layer_path)
            if edit_layer:
                edit_layer.Clear()
            else:
                edit_layer = Sdf.Layer.CreateNew(edit_layer_path)

            if not edit_layer:
                carb.log_error(f"open_with_new_edit_layer: failed to create edit layer {edit_layer_path}")
                return

            # FIXME: Delay two frames to center prompt.
            await self._app.next_update_async()
            await self._app.next_update_async()
            with Prompt("Please Wait", "Creating new stage...", [], [], True):
                await self._app.next_update_async()  # Making sure prompt shows
                root_layer = Sdf.Layer.CreateAnonymous()
                root_layer.subLayerPaths.insert(0, file_path)
                root_layer.subLayerPaths.insert(0, edit_layer_path)

                # Copy all meta
                base_layer = Sdf.Layer.FindOrOpen(file_path)
                UsdUtils.CopyLayerMetadata(base_layer, root_layer, True)
                omni.usd.resolve_paths(base_layer.identifier, root_layer.identifier, False, True)

                # Set edit target
                stage = Usd.Stage.Open(root_layer)
                edit_target = stage.GetEditTargetForLocalLayer(edit_layer)
                stage.SetEditTarget(edit_target)
                await omni.usd.get_context().attach_stage_async(stage)
                await self._app.next_update_async()  # Wait anther frame for StageEvent.OPENED to be handled

            if callback:
                callback()

        async def create_stage_prompt_if_exists(edit_layer_path: str, file_path: str, callback: Callable):
            result, _ = await omni.client.stat_async(edit_layer_path)
            # File is existed already.
            if result == omni.client.Result.OK:
                self._show_file_existed_prompt(
                    edit_layer_path,
                    lambda: FileUtils._exclusive_task_wrapper(
                        create_stage_async, edit_layer_path, file_path, callback
                    )
                )
            else:
                await create_stage_async(edit_layer_path, file_path, callback)

        asyncio.ensure_future(create_stage_prompt_if_exists(edit_layer_path, file_path, callback))

    def reopen(self):
        """Reopen currently opened stage. If the stage is dirty, a prompt will show to let you save it."""
        self.stop_timeline()

        async def reopen_stage_job():
            context = omni.usd.get_context()
            path = context.get_stage_url()
            # FIXME: Delay two frames to center prompt.
            await self._app.next_update_async()
            await self._app.next_update_async()
            with Prompt("Please Wait", f"Reopening {path}...", [], [], True):
                await self._app.next_update_async()  # Making sure prompt shows
                result, err = await context.reopen_stage_async()
                await self._app.next_update_async()  # Wait anther frame for StageEvent.OPENED to be handled
                if not result or context.get_stage_state() != omni.usd.StageState.OPENED:
                    carb.log_error(f"Failed to reopen stage {path}: {err}")
                    self.ui_handler.show_open_stage_failed_prompt(path)

        if not (omni.usd.get_context().get_stage_state() == omni.usd.StageState.OPENED and not omni.usd.get_context().is_new_stage()):
            FileUtils.post_notification("Cannot Reopen. No valid stage")
            return

        self.prompt_if_unsaved_stage(lambda *_: FileUtils._exclusive_task_wrapper(reopen_stage_job))

    def save(
        self, callback: Callable[[bool, str], None],
        allow_skip_sublayers: bool = False,
        dialog_options=DialogOptions.NONE):
        """
        Save currently opened stage to file. Will call Save As for a newly created stage.

        Keyword Args:
            callback (Callable): function to call after saving. Function Signature:
                callback(result: bool, url: str) -> None
            allow_skip_sublayers (bool): True to skip sublayers.
            dialog_options (:obj:`DialogOptions`): options for opening the dialog.
        """
        # Syncs render settings to stage before save so stage could
        # get the correct edit state if render settings are changed.
        if omni.usd.get_context().get_stage_state() != omni.usd.StageState.OPENED:
            FileUtils.post_notification("Cannot Save. No valid stage")
            return

        self.stop_timeline()

        async def save_async(callback: Callable, allow_skip_sublayers: bool):
            is_new_stage = omni.usd.get_context().is_new_stage() or \
                omni.usd.get_context().get_stage_state() != omni.usd.StageState.OPENED

            is_writeable = False
            try:
                filename_url = omni.usd.get_context().get_stage().GetRootLayer().identifier
                result, stat = await omni.client.stat_async(filename_url)
            except Exception:
                pass
            else:
                if result == omni.client.Result.OK:
                    is_writeable = stat.flags & omni.client.ItemFlags.WRITEABLE_FILE

            # OM-47514 When saving a checkpoint or read-only file, use save_as instead
            if is_new_stage or not is_writeable:
                self.save_as(False, callback, allow_skip_sublayers=allow_skip_sublayers)
            else:
                stage = omni.usd.get_context().get_stage()
                dirty_layer_identifiers = omni.usd.get_dirty_layers(stage, True)
                self.ui_handler.save_root_and_sublayers(
                    "", dirty_layer_identifiers,
                    on_save_done=callback,
                    dialog_options=dialog_options,
                    allow_skip_sublayers=allow_skip_sublayers
                )

        asyncio.ensure_future(save_async(callback, allow_skip_sublayers))

    def save_as(self, flatten: bool, callback: Callable[[bool, str], None], allow_skip_sublayers: bool = False):
        """
        Bring up a file picker to choose a file to save current stage to.

        Args:
            flatten (bool): Whether to flatten the stage or not.

        Keyword Args:
            callback (Callable): function to call after saving. Function Signature:
                callback(result: bool, url: str) -> None
            allow_skip_sublayers (bool): True to skip sublayers.
        """
        self.stop_timeline()

        def save_handler(callback: Callable, flatten: bool, filename: str, dirname: str, extension: str = '', selections: List[str] = []):
            if dirname and dirname[-1] != '/':
                dirname += "/"
            path = omni.client.make_absolute_url_if_possible(dirname, f"{filename}{extension}")

            async def check_and_save():
                result, stat = await omni.client.stat_async(dirname)
                if result == omni.client.Result.OK and (stat.access & omni.client.AccessFlags.WRITE) == 0:
                    error = "Save couldn't be completed as target directory is read-only."
                    if callback:
                        callback(False, error)
                    FileUtils.post_notification(error)
                else:
                    result, stat = await omni.client.stat_async(path)
                    if result == omni.client.Result.OK and (stat.access & omni.client.AccessFlags.WRITE) == 0:
                        error = "Save couldn't be completed as target file exists already and it is read-only."
                        if callback:
                            callback(False, error)
                        FileUtils.post_notification(error)
                    else:
                        self.save_stage(
                            path, callback=callback, flatten=flatten,
                            save_options=self._save_options,
                            allow_skip_sublayers=allow_skip_sublayers
                        )

            asyncio.ensure_future(check_and_save())

        if omni.usd.get_context().get_stage_state() != omni.usd.StageState.OPENED:
            error = "Cannot Save As. No valid stage."
            if callback:
                callback(False, error)

            FileUtils.post_notification(error)
            return

        file_exporter = get_file_exporter()
        if file_exporter:
            # OM-48033: Save as should open to latest opened stage path. Solution also covers ...
            # OM-58150: Save as should pass in the current file name as default value.
            filename_url = file_utils.get_last_url_visited(asset_type=asset_types.ASSET_TYPE_USD)
            if filename_url:
                # OM-91056: File Save As should not prefill the file name
                filename_url = os.path.dirname(filename_url) + "/"
            file_exporter.show_window(
                title="Save File As...",
                export_button_label="Save",
                export_handler=partial(save_handler, callback, flatten),
                filename_url=filename_url,
                # OM-64312: Set save-as dialog to validate file names in file exporter
                should_validate=True,
            )

            if self._save_options is None:
                self._save_options = SaveOptionsDelegate()
            file_exporter.add_export_options_frame("Save Options", self._save_options)

            # OM-55838: Don't show "include sesson layer" for non-flatten save-as.
            self._save_options.show_include_session_layer_option = flatten
        else:
            if callback:
                callback(False, "Save couldn't be completed as file exporter widget is invalid.")

    def save_stage(
        self, path: str, callback: Callable[[bool, str], None] = None,
        flatten: bool = False, save_options: SaveOptionsDelegate = None, allow_skip_sublayers: bool = False
    ):
        """
        Save current stage to the given path, if the path exists bring up the filepicker to choose a potential new path.

        Args:
            path (str): path to save the file.

        Keyword Args:
            callback (Callable): function to call after saving. Function Signature:
                callback(result: bool, url: str) -> None
            flatten (bool): whether to flatten the stage or not.
            save_options (:obj:`SaveOptionsDelegate`): if set, load save settings from it.
            allow_skip_sublayers (bool): True to skip sublayers.
        """
        self.stop_timeline()
        stage = omni.usd.get_context().get_stage()
        save_comment = ""
        if save_options:
            save_comment = save_options.get_comment()

        include_session_layer = False
        if save_options and flatten:
            include_session_layer = save_options.include_session_layer()

        if flatten:
            path = path or stage.GetRootLayer().identifier
            # TODO: Currently, it's implemented differently for export w/o session layer as
            # flatten is a simple operation and we don't want to break the ABI of omni.usd.
            if include_session_layer:
                omni.usd.get_context().export_as_stage_with_callback(path, callback)
            else:
                async def flatten_stage_without_session_layer(path, callback):
                    await self._app.next_update_async()
                    await self._app.next_update_async()
                    with Prompt("Please Wait", "Exporting flattened stage...", [], [], True):
                        await self._app.next_update_async()
                        usd_context = omni.usd.get_context()
                        if usd_context.can_save_stage():
                            stage = usd_context.get_stage()
                            # Creates empty anon layer.
                            anon_layer = Sdf.Layer.CreateAnonymous()
                            temp_stage = Usd.Stage.Open(stage.GetRootLayer(), anon_layer)
                            success = temp_stage.Export(path)
                            if callback:
                                if success:
                                    callback(True, "")
                                else:
                                    callback(False, f"Error exporting flattened stage to path: {path}.")
                        else:
                            error = "Stage busy or another saving task is in progress!!"
                            carb.log_error(error)
                            if callback:
                                callback(False, error)

                asyncio.ensure_future(flatten_stage_without_session_layer(path, callback))
        else:
            async def save_stage_async(path: str, callback: Callable):
                if path == stage.GetRootLayer().identifier:
                    dirty_layer_identifiers = omni.usd.get_dirty_layers(stage, True)
                    self.ui_handler.save_root_and_sublayers(
                        "", dirty_layer_identifiers, on_save_done=callback, save_comment=save_comment, allow_skip_sublayers=allow_skip_sublayers)
                else:
                    path = path or stage.GetRootLayer().identifier
                    dirty_layer_identifiers = omni.usd.get_dirty_layers(stage, False)
                    save_fn = lambda: self.ui_handler.save_root_and_sublayers(
                        path, dirty_layer_identifiers, on_save_done=callback, save_comment=save_comment, allow_skip_sublayers=allow_skip_sublayers)
                    cancel_fn = lambda: self.ui_handler.save_root_and_sublayers(
                        "", dirty_layer_identifiers, on_save_done=callback, save_comment=save_comment, allow_skip_sublayers=allow_skip_sublayers)

                    result, _ = await omni.client.stat_async(path)
                    if result == omni.client.Result.OK:
                        # Path already exists, prompt to overwrite
                        self._show_file_existed_prompt(path, save_fn, on_cancel_fn=cancel_fn)
                    else:
                        save_fn()

            asyncio.ensure_future(save_stage_async(path, callback))

    def close(self, on_closed: Callable[[], None], fast_shutdown=False):
        """
        Check if current stage is dirty. If it's dirty, it will ask if to save the file, then close stage.

        Args:
            on_closed (Callable): function to call after closing, Function Signature:
                on_closed() -> None

        Keyword Args:
            fast_shutdown (bool): clear pending edits immediately to shutdown faster.
        """
        self.stop_timeline()

        async def close_stage_job():
            if not fast_shutdown:
                # FIXME: Delay two frames to center prompt.
                await self._app.next_update_async()
                await self._app.next_update_async()
                with Prompt("Please Wait", "Closing stage...", [], [], True):
                    await self._app.next_update_async()  # Making sure prompt shows
                    await omni.usd.get_context().close_stage_async()
                    await self._app.next_update_async()  # Wait anther frame for StageEvent.CLOSED to be handled
            else:
                # Clear dirty state to allow quit fastly.
                omni.usd.get_context().set_pending_edit(False)

            if on_closed:
                on_closed()

        self.prompt_if_unsaved_stage(lambda *_: FileUtils._exclusive_task_wrapper(close_stage_job))

    def save_layers(
        self, new_root_path: str, dirty_layers: List[str],
        on_save_done: Callable[[bool, str], None], create_checkpoint=True, checkpoint_comment=""
    ):
        """
        Save current layers.

        Args:
            new_root_path (str): path to set the root layer.
            dirty_layers (List[str]): layer identifiers to save.
            on_save_done (Callable): function to call after saving. Function Signature:
                on_save_done(result: bool, url: str) -> None

        Keyword Args:
            create_checkpoint (bool): true to create checkpoints.
            checkpoint_comments (str): comment on the created checkpoint.
        """
        # Skips if it has no real layers to be saved.
        self.stop_timeline()

        # It's possible that all layers are not dirty but it has pending edits to be saved,
        # like render settings, which needs to be saved into root layer during save.
        usd_context = omni.usd.get_context()
        has_pending_edit = usd_context.has_pending_edit()
        if not new_root_path and not dirty_layers and not has_pending_edit:
            if on_save_done:
                on_save_done(True, "")
            return

        try:
            async def save_layers_job(*_):
                # FIXME: Delay two frames to center prompt.
                await self._app.next_update_async()
                await self._app.next_update_async()
                with Prompt("Please Wait", "Saving layers...", [], [], True):
                    await self._app.next_update_async()  # Making sure prompt shows
                    await self._app.next_update_async()  # Need 2 frames since save happens on mainthread

                    with _CheckpointCommentContext(checkpoint_comment):
                        result, err, saved_layers = await usd_context.save_layers_async(new_root_path, dirty_layers)

                    await self._app.next_update_async()  # Wait anther frame for StageEvent.SAVED to be handled

                    # Clear unique task since it's possible that
                    # post-call to on_save_done needs to create unique
                    # instance also.
                    if _file_util_instance and _file_util_instance._task:
                        _file_util_instance._task = None

                    if on_save_done:
                        on_save_done(result, err)
                    if result:
                        omni.kit.app.queue_event(file_utils.FILE_SAVED_GLOBAL_EVENT, file_utils.FileEventModel(url=new_root_path).dict())
                    else:
                        self.ui_handler.show_save_layers_failed_prompt()

            FileUtils._exclusive_task_wrapper(save_layers_job)
        except Exception as exc:
            error = f"Save Error: {exc}"
            if on_save_done:
                on_save_done(False, error)
            carb.log_error(error)
            traceback.print_exc()

    def prompt_if_unsaved_stage(self, callback: Callable[[], None]):
        """
        Check if current stage is dirty. If it's dirty, ask to save the file, then execute callback. Otherwise runs callback directly.


        Args:
            callback (Callable): function to call upon saving. Function Signature:
                callback() -> None
        """
        def should_show_stage_save_dialog():
            # Use settings to control if it needs to show stage save dialog for layers save.
            # For application that uses kit and does not want this, it can disable this.
            settings = carb.settings.get_settings()
            settings.set_default_bool(SHOW_UNSAVED_LAYERS_DIALOG, True)
            show_stage_save_dialog = settings.get(SHOW_UNSAVED_LAYERS_DIALOG)
            return show_stage_save_dialog

        async def callback_async():
            await omni.kit.app.get_app().next_update_async()
            callback()

        ignore_unsaved = self._settings.get(IGNORE_UNSAVED_STAGE)
        if omni.usd.get_context().has_pending_edit() and not ignore_unsaved:
            if omni.usd.get_context().is_new_stage() or should_show_stage_save_dialog():
                if self._unsaved_stage_prompt:
                    self._unsaved_stage_prompt.destroy()
                self._unsaved_stage_prompt = Prompt(
                    f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")}',
                    "Would you like to save this stage?",
                    ["Save", "Don't Save", "Cancel"],
                    [lambda *_: self.save(callback, allow_skip_sublayers=True), lambda *_: asyncio.ensure_future(callback_async()) if callback else None, None],
                    modal=True)
                self._unsaved_stage_prompt.show()
            else:
                self.save(callback, allow_skip_sublayers=True)
        else:
            if callback:
                callback()

    def add_reference(self, is_payload=False):
        """
        Prompt for the file to add reference or payload to.

        Keyword Args:
            is_payload (bool): True to add payload instead of reference.
        """
        self.stop_timeline()

        def on_file_picked(is_payload: bool, filename: str, dirname: str, selections: List[str]):
            if not filename.startswith('\\\\'):
                filename = filename.replace("\\", "/")
            if ':/' in filename or filename.startswith('\\\\'):
                # Filename is a pasted fullpath.  The first test finds paths that start with 'C:/' or 'omniverse://';
                # the second finds MS network paths that start like '\\analogfs\VENDORS\...'
                reference_path = filename
            else:
                if dirname and dirname[-1] != '/':
                    dirname += "/"
                reference_path = omni.client.make_absolute_url_if_possible(
                    dirname, filename
                )

            name = os.path.splitext(os.path.basename(reference_path))[0]
            stage = omni.usd.get_context().get_stage()
            if stage.HasDefaultPrim():
                prim_path = omni.usd.get_stage_next_free_path(
                    stage, stage.GetDefaultPrim().GetPath().pathString + "/" + omni.usd.make_valid_identifier(name), False
                )
            else:
                prim_path = omni.usd.get_stage_next_free_path(stage, "/" + omni.usd.make_valid_identifier(name), False)

            if is_payload:
                omni.kit.commands.execute(
                    "CreatePayload", usd_context=omni.usd.get_context(), path_to=prim_path, asset_path=reference_path, instanceable=False
                )
            else:
                omni.kit.commands.execute(
                    "CreateReference", usd_context=omni.usd.get_context(), path_to=prim_path, asset_path=reference_path, instanceable=False
                )

        file_importer = get_file_importer()
        if file_importer:
            file_importer.show_window(
                title="Select File",
                import_button_label="Add Reference" if not is_payload else "Add Payload",
                import_handler=partial(on_file_picked, is_payload),
                should_validate=True,
            )

    def register_open_stage_addon(self, callback: Callable[[], None]):
        """
        Register callback to call when opening a stage.

        Args:
            callback (Callable): function to call. Function Signature:
                callback() -> None
        Return:
            :obj:`_CallbackRegistrySubscription`: The callback subscription.
        """
        return _CallbackRegistrySubscription(self._open_stage_callbacks, callback)

    def register_open_stage_complete(self, callback: Callable[[], None]):
        """
        Register callback to call when finish opening a stage.

        Args:
            callback (Callable): function to call. Function Signature:
                callback() -> None
        Return:
            :obj:`_CallbackRegistrySubscription`: The callback subscription.
        """
        return _CallbackRegistrySubscription(self._open_stage_complete_callbacks, callback)

    @staticmethod
    def _exclusive_task_wrapper(job: Awaitable, *args):
        # Only allow one task to be run
        if _file_util_instance._task:
            carb.log_info("_exclusive_task_wrapper already running. Cancelling")
            _file_util_instance._task.cancel()
            _file_util_instance._task = None

        async def exclusive_task():
            await job(*args)
            _file_util_instance._task = None

        _file_util_instance._task = asyncio.ensure_future(exclusive_task())

    def post_notification(message: str, info: bool = False, duration: int = 3):
        """
        Post a notification message.

        Args:
            message (str): message text.
            info (bool): If True, post the message as info or otherwise warning.
            duration (int): Duration of notification, in seconds.
        """
        try:
            import omni.kit.notification_manager as nm
            if info:
                type = nm.NotificationStatus.INFO
            else:
                type = nm.NotificationStatus.WARNING

            nm.post_notification(message, status=type, duration=duration)
        except ModuleNotFoundError:
            carb.log_warn(message)

def get_instance():
    """Get the file utils instance."""
    return _file_util_instance

# used for test
def get_file_utils_instance():
    """Get the file utils instance."""
    return _file_util_instance

def new(template=None):
    """
    Create a new USD stage. If currently opened stage is dirty, a prompt will show to let you save it.

    Keyword Args:
        template (Optional[str]): the template to use.
    """
    if _file_util_instance:
        _file_util_instance.new(template)


def open(open_loadset=omni.usd.UsdContextInitialLoadSet.LOAD_ALL):
    """
    Bring up a file picker to choose a USD file to open. If currently opened stage is dirty, a prompt will show to let you save it.

    Keyword Args:
        open_loadset (:obj:`omni.usd.UsdContextInitialLoadSet`): initial load set enum, LOAD_ALL or LOAD_NONE.
    """
    if _file_util_instance:
        _file_util_instance.open(open_loadset)


def open_stage(path: str, open_loadset=omni.usd.UsdContextInitialLoadSet.LOAD_ALL):
    """
    Open stage. If the current stage is dirty, a prompt will show to let you save it.

    Args:
        path (str): path to open the stage.
    Keyword Args:
        open_loadset (:obj:`omni.usd.UsdContextInitialLoadSet`): initial load set enum, LOAD_ALL or LOAD_NONE.
    """
    if _file_util_instance:
        _file_util_instance.open_stage(path, open_loadset=open_loadset)


def open_with_new_edit_layer(path: str, open_loadset=omni.usd.UsdContextInitialLoadSet.LOAD_ALL, callback: Callable[[], None]=None):
    """
    Open stage and create a new edit layer.

    Args:
        path (str): path to open the stage.
    Keyword Args:
        open_loadset (:obj:`omni.usd.UsdContextInitialLoadSet`): initial load set enum, LOAD_ALL or LOAD_NONE.
        callback: (Callable): callback to call after creating stage. Function Signature:
            callback() -> None
    """
    if _file_util_instance:
        _file_util_instance.open_with_new_edit_layer(path, open_loadset, callback)


def create_stage(self, edit_layer_path: str, file_path: str, callback: Callable = None):
    """
    Create a stage with edit layer from paths.

    Args:
        edit_layer_path (str): path to create the edit layer.
        file_path (str): path to create the stage.
    Keyword Args:
        callback: (Callable): callback to call after creating stage. Function Signature:
            callback() -> None
    """
    if _file_util_instance:
        _file_util_instance.create_stage(edit_layer_path, file_path, callback)


def reopen():
    """Reopen currently opened stage. If the stage is dirty, a prompt will show to let you save it."""
    if _file_util_instance:
        _file_util_instance.reopen()


def save(on_save_done: Optional[Callable[[bool, str], None]]=None, exit=False, dialog_options=DialogOptions.NONE):
    """
    Save currently opened stage to file. Will call Save As for a newly created stage.

    Keyword Args:
        on_save_done (Callable): function to call after saving. Function Signature:
            on_save_done(result: bool, url: str) -> None
        exit(bool): Unused parameter.
        dialog_options (:obj:`DialogOptions`): options for opening the dialog.
    """
    if _file_util_instance:
        _file_util_instance.save(on_save_done, dialog_options=dialog_options)


def save_as(flatten, on_save_done: Optional[Callable[[bool, str], None]]=None):
    """
    Bring up a file picker to choose a file to save current stage to.

    Args:
        flatten (bool): Whether to flatten the stage or not.

    Keyword Args:
        on_save_done (Callable): function to call after saving. Function Signature:
            on_save_done(result: bool, url: str) -> None
    """
    if _file_util_instance:
        _file_util_instance.save_as(flatten, on_save_done)


def close(on_closed: Optional[Callable[[], None]]=None):
    """
    Check if current stage is dirty. If it's dirty, it will ask if to save the file, then close stage.

    Keyword Args:
        on_closed (Callable): function to call after closing, Function Signature:
            on_closed() -> None
    """
    if _file_util_instance:
        _file_util_instance.close(on_closed)


def save_layers(new_root_path, dirty_layers, on_save_done, create_checkpoint=True, checkpoint_comment=""):
    """
    Save current layers.

    Args:
        new_root_path (str): path to set the root layer.
        dirty_layers (List[str]): layer identifiers to save.
        on_save_done (Callable): function to call after saving. Function Signature:
            on_save_done(result: bool, url: str) -> None

    Keyword Args:
        create_checkpoint (bool): true to create checkpoints.
        checkpoint_comments (str): comment on the created checkpoint.
    """
    if _file_util_instance:
        _file_util_instance.save_layers(new_root_path, dirty_layers, on_save_done, create_checkpoint, checkpoint_comment)


def prompt_if_unsaved_stage(job: Callable[[], None]):
    """
    Check if current stage is dirty. If it's dirty, ask to save the file, then execute callback. Otherwise runs callback directly.

    Args:
        job (Callable): function to call upon saving. Function Signature:
            job() -> None
    """
    if _file_util_instance:
        _file_util_instance.prompt_if_unsaved_stage(job)


def add_reference(is_payload=False):
    """
    Prompt for the file to add reference or payload to.

    Keyword Args:
        is_payload (bool): True to add payload instead of reference.
    """
    if _file_util_instance:
        _file_util_instance.add_reference(is_payload=is_payload)


def register_open_stage_addon(callback):
    """
    Register callback to call when opening a stage.

    Args:
        callback (Callable): function to call. Function Signature:
            callback() -> None
    Return:
        :obj:`_CallbackRegistrySubscription`: The callback subscription.
    """
    if _file_util_instance:
        return _file_util_instance.register_open_stage_addon(callback)


def register_open_stage_complete(callback):
    """
    Register callback to call when finish opening a stage.

    Args:
        callback (Callable): function to call. Function Signature:
            callback() -> None
    Return:
        :obj:`_CallbackRegistrySubscription`: The callback subscription.
    """
    if _file_util_instance:
        return _file_util_instance.register_open_stage_complete(callback)
