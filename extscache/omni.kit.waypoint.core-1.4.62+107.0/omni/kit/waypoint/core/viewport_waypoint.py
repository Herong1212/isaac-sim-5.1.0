import asyncio
from contextlib import nullcontext
from typing import List, Optional, Tuple

import carb
import omni.kit.app
import omni.kit.commands
import omni.kit.prim.icon
import omni.timeline
import omni.usd
from pxr import Sdf, Usd

from .common import WAYPOINT_ICON_URL, WAYPOINT_ROOT_PRIM_PATH
from .pereference import WaypointPereference
from .settings import (
    AbstractWaypointSetting,
    CameraSetting,
    GeneralSetting,
    PrimVisibilitySetting,
    RendererSetting,
    SunstudySetting,
    ThumbnailSetting,
)


# A waypoint instance
class ViewportWaypoint:
    def __init__(
        self,
        name,
        parent_path="",
        icon_url: str = WAYPOINT_ICON_URL,
        icon_click: callable = None,
        sidecar_data: Optional[Usd.EditContext] = None,
        edit_context: Usd.EditContext = None,
        edit_target_exists: bool = False,
        hide_in_stage_window_disabled: bool = False,
        viewport_widget=None,
    ):
        self.icon_url = icon_url
        self.icon_click = icon_click
        self._usd_prim = None
        self.__sidecar_data = sidecar_data
        self.__edit_context = edit_context
        self.__edit_target_exists = edit_target_exists
        self.__hide_in_stage_window_disabled = hide_in_stage_window_disabled

        self._general_setting = GeneralSetting(self.edit_context)
        self._thumbnail_setting = ThumbnailSetting(self.edit_context, viewport_widget=viewport_widget)
        self._camera_setting = CameraSetting(self.edit_context, viewport_widget=viewport_widget)
        self._waypoint_settings: List[AbstractWaypointSetting] = [
            self._general_setting,
            self._camera_setting,
            RendererSetting(self.edit_context),
            SunstudySetting(self.edit_context),
            PrimVisibilitySetting(self.edit_context),
            # Thumbnail is the last one to notify creation done after thumbnail generated
            self._thumbnail_setting,
        ]

        self._init(name, parent_path)

    # We call a delete function when removing a waypoint, not destroy.
    # def destroy(self):
    #     for setting in self._waypoint_settings:
    #         setting.destroy()

    def __repr__(self):
        return f'"{self._name}"'

    def __str__(self):
        return f'"{self._name}"'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def path(self) -> str:
        return f"{self._parent_path}/{self._name}"

    @property
    def thumbnail(self) -> Optional[str]:
        return self._thumbnail_setting.thumbnail_path

    @property
    def thumbnail_data(self) -> Optional[Tuple[bytes, int, int]]:
        return self._thumbnail_setting.thumbnail_data

    @property
    def create_time(self) -> Optional[str]:
        return self._general_setting.data["create_time"]

    @property
    def created_by(self) -> Optional[str]:
        return self._general_setting.data["created_by"]

    @property
    def comment(self) -> str:
        return self._general_setting.data["comment"]

    @comment.setter
    def comment(self, comment: str):
        # TODO: Need a better way later
        if self.__sidecar_data and self.__sidecar_data.read_only:  # pragma: no cover
            self.__sidecar_data.notify_read_only("Set Comment")
            return

        with self.edit_context:
            self._general_setting.set_comment(comment)

    @property
    def frame(self) -> float:
        return self._general_setting.data.get("frame", 0.0)

    @frame.setter
    def frame(self, frame: float):
        self._general_setting.set_frame(frame)

    @property
    def camera_prim(self) -> Optional[Usd.Prim]:
        # Camera may not be captured
        return self._camera_setting.camera_prim

    @property
    def is_dirty(self) -> bool:
        for setting in self._waypoint_settings:
            if setting.is_dirty():
                return True
        return False

    @property
    def info(self) -> str:
        info = []
        for setting in self._waypoint_settings:
            if setting.info:
                info.extend(setting.info)
        return info

    @property
    def edit_context(self) -> Usd.EditContext:
        # Resolve any edit context conflict by prioritizing the sidecar
        if self.__sidecar_data and self.__edit_context:
            carb.log_warn(
                "Both SideCarData and WaypointExtension had edit context overrides for ViewportWaypoint. "
                "The returned edit context will be from SideCarData.edit_context."
            )

        # Override the edit context with either WaypointExtension or sidecar edits contexts if necessary
        if self.__sidecar_data:
            return self.__sidecar_data.edit_context
        if self.__edit_target_exists:
            return self.__edit_context

        return Usd.EditContext(omni.usd.get_context().get_stage(), Usd.EditTarget(None))

    @property
    def usd_prim(self) -> Optional[Usd.Prim]:
        return self._get_usd_prim()

    def recall(
        self,
        without_camera=False,
        enable_settings: Optional[List[str]] = None,
        disable_settings: Optional[List[str]] = None,
    ):
        recall_disable_settings = WaypointPereference.get_recall_disable_settings()
        if disable_settings is not None:
            recall_disable_settings.extend(disable_settings)
        if enable_settings is not None:
            for name in enable_settings:
                while name in recall_disable_settings:
                    recall_disable_settings.remove(name)

        usd_prim = self._get_usd_prim()
        if usd_prim:
            if without_camera:
                if self._camera_setting.get_name() not in recall_disable_settings:
                    recall_disable_settings.append(self._camera_setting.get_name())

            for setting in self._waypoint_settings:
                if setting.get_name() not in recall_disable_settings:
                    setting.recall(usd_prim)
        else:
            carb.log_warn("Failed to get prim of current viewport waypoint.")

    def stop_recalling(self):  # pragma: no cover (called by other extensions, but doesn't do anything either)
        pass

    def rename(self, new_name):
        if not Sdf.Path.IsValidPathString(new_name):
            return False

        usd_prim = self._get_usd_prim()
        if usd_prim:
            old_path = self.get_usd_prim_path()
            self._name = new_name
            new_path = self.get_usd_prim_path()
            move_dict = {old_path: new_path}
            omni.kit.commands.execute(
                "MovePrimsCommand", paths_to_move=move_dict, on_move_fn=self._on_rename_fn, destructive=False
            )
            for setting in self._waypoint_settings:
                setting.update(omni.usd.get_context().get_stage().GetPrimAtPath(new_path))
            return True

        return False

    async def create_async(self, on_created_fn: callable = None):
        carb.log_info(f"[Waypoint] Creating waypoint async...")
        capture_disable_settings = WaypointPereference.get_capture_disable_settings()

        for setting in self._waypoint_settings:
            setting.create(setting.get_name() not in capture_disable_settings)

        # Save current data (of models) to USD prim
        usd_prim = self._get_usd_prim()
        if usd_prim:
            for setting in self._waypoint_settings:
                if setting.is_valid():
                    await setting.save_async(usd_prim)

        carb.log_info(f"[Waypoint] Waypoint {self.name} created at {self.path}")

    def create(self, on_created_fn: callable = None):
        carb.log_info(f"[Waypoint] Creating waypoint...")
        capture_disable_settings = WaypointPereference.get_capture_disable_settings()

        def __on_created(result: bool, callback):
            if result:
                callback(self)

        self._thumbnail_setting.on_created_fn = lambda r, c=on_created_fn: __on_created(r, c)

        for setting in self._waypoint_settings:
            setting.create(setting.get_name() not in capture_disable_settings)

        # Save current data (of models) to USD prim
        usd_prim = self._get_usd_prim()
        if usd_prim:
            for setting in self._waypoint_settings:
                if setting.is_valid():
                    setting.save(usd_prim)

        carb.log_info(f"[Waypoint] Waypoint {self.name} created at {self.path}")

    def create_from_prim(self, prim: Usd.Prim) -> bool:
        prim_path = prim.GetPath().pathString
        slash_index = prim_path.rfind("/")
        waypoint_name = prim_path[slash_index + 1 :]
        parent_path = prim_path[:slash_index]

        self._init(waypoint_name, parent_path)

        carb.log_info(f"load {waypoint_name}")
        for setting in self._waypoint_settings:
            setting.load(prim)

        return bool(self.thumbnail_data)

    def delete(self):
        for setting in self._waypoint_settings:
            setting.delete()

        prim_icons = omni.kit.prim.icon.get_prim_icon_interface()
        prim_icons.remove_prim_icon(self.path)

        if omni.usd.get_context().get_stage().GetPrimAtPath(self.path):
            omni.kit.commands.execute("DeletePrimsCommand", paths=[self.path], destructive=False)

        self._init()

    def get_usd_prim_path(self) -> str:
        return self._parent_path + "/" + self._name

    def subscribe_changes(self, enable: bool) -> None:
        for setting in self._waypoint_settings:
            setting.subscribe_changes(enable)

    def _init(self, name="", parent_path=""):
        self._name = name
        if len(parent_path) > 0:
            self._parent_path = parent_path
        else:
            self._parent_path = WAYPOINT_ROOT_PRIM_PATH
        self._thumbnail = None
        self._usd_prim = None

        if not self.__hide_in_stage_window_disabled:
            asyncio.ensure_future(self._hide_waypoint_root_prim())

    def _on_rename_fn(self, old_prim_name: Sdf.Path, new_prim_name: Sdf.Path):
        pass

    def _get_usd_prim(self) -> Usd.Prim:
        if not self._usd_prim:
            prim_path = self.get_usd_prim_path()
            self._usd_prim = omni.usd.get_context().get_stage().GetPrimAtPath(prim_path)
        return self._usd_prim

    async def _hide_waypoint_root_prim(self):
        await omni.kit.app.get_app().next_update_async()
        root_prim = omni.usd.get_context().get_stage().GetPrimAtPath(WAYPOINT_ROOT_PRIM_PATH)
        if root_prim and not root_prim.GetMetadata("hide_in_stage_window"):
            omni.usd.editor.set_hide_in_stage_window(root_prim, True)
