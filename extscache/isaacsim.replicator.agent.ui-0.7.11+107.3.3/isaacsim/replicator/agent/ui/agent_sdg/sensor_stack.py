import asyncio

import carb
import omni.kit.app
from isaacsim.replicator.agent.core.config_file.defines import *
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.ui_util import *
from omni.ui import color as cl
from omni.metropolis.utils.ui_util import UIUtil

SAVE_BTN_TEXT = "Save"
UNSAVE_BTN_TEXT = "*Save"


class SensorStack:
    def __init__(self, events, variables):
        self._variables = variables
        self._events = events
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(lambda: asyncio.ensure_future(self.build_camera_ui()))
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(
            lambda: asyncio.ensure_future(self.build_camera_ui())
        )
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(lambda: asyncio.ensure_future(self.build_camera_ui()))
        self._settings = carb.settings.get_settings()
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._cam_ui_stack = None
        self._radio_collection = None
        self._cam_list_stack = None
        self._lidar_list_stack = None
        self._cam_num_field = None
        self._lidar_num_field = None

    async def refresh_cam_list_stack(self):
        await self.refresh_list_stack(
            property_name="camera_list", stack=self._cam_list_stack, refresh_fn=self.refresh_cam_list_stack
        )

    # async def refresh_lidar_list_stack(self):
    #     await self.refresh_list_stack(
    #         property_name="lidar_list", stack=self._lidar_list_stack, refresh_fn=self.refresh_lidar_list_stack
    #     )

    async def refresh_list_stack(self, property_name, stack, refresh_fn):
        # Refresh stack
        stack.clear()
        await omni.kit.app.get_app().next_update_async()
        # Read from config file
        camera_group: OrPropertyGroup = self._sim_manager.get_config_file_property_group("sensor", "camera_group")
        with stack:
            # Populate list UI
            camera_list_prop: Property = camera_group.get_property(property_name)
            if camera_list_prop is not None:
                for index, cam in enumerate(camera_list_prop.get_value()):
                    with ui.HStack(spacing=3, height=20):
                        field = ui.StringField()
                        field.model.set_value(cam)
                        field.model.add_end_edit_fn(
                            lambda model, i=index: self._on_list_edit(property_name, i, model, refresh_fn)
                        )
                        del_btn = ui.Button(f"{UIUtil.get_trash_glyph()}", width=30, height=20)
                        del_btn.set_clicked_fn(lambda i=index: self._on_list_del(property_name, i, refresh_fn))
            # Recreate button
            add_btn = ui.Button(text=f"{UIUtil.get_plus_glyph()} Add", width=55, height=20, spacing=3)
            add_btn.set_clicked_fn(lambda p=property_name: self._on_list_add(p, refresh_fn))

    def _on_list_add(self, property_name, refresh_fn):
        camera_group: OrPropertyGroup = self._sim_manager.get_config_file_property_group("sensor", "camera_group")
        camera_list_prop = camera_group.get_property(property_name)
        # Add selection if it is camera
        context = omni.usd.get_context()
        stage = context.get_stage()
        selected_prims = context.get_selection().get_selected_prim_paths()
        selected_cameras = [path for path in selected_prims if stage.GetPrimAtPath(path).GetTypeName() == "Camera"]
        if selected_cameras:
            for path in selected_cameras:
                camera_list = camera_list_prop.get_value().copy()
                camera_list.append(path)
                camera_list_prop.set_value(camera_list)
        # Add empty string otherwise
        else:
            camera_list = camera_list_prop.get_value().copy()
            camera_list.append("")
            camera_list_prop.set_value(camera_list)
        asyncio.ensure_future(refresh_fn())

    def _on_list_del(self, property_name, index, refresh_fn):
        camera_group: OrPropertyGroup = self._sim_manager.get_config_file_property_group("sensor", "camera_group")
        camera_list_prop = camera_group.get_property(property_name)
        camera_list = camera_list_prop.get_value().copy()
        camera_list.pop(index)
        camera_list_prop.set_value(camera_list)
        asyncio.ensure_future(refresh_fn())

    def _on_list_edit(self, property_name, index, model, refresh_fn):
        camera_group: OrPropertyGroup = self._sim_manager.get_config_file_property_group("sensor", "camera_group")
        camera_list_prop = camera_group.get_property(property_name)
        camera_list = camera_list_prop.get_value().copy()
        old_cam_path = camera_list[index]
        new_cam_path = model.get_value_as_string()
        if new_cam_path != old_cam_path:
            camera_list[index] = new_cam_path
            camera_list_prop.set_value(camera_list)
            asyncio.ensure_future(refresh_fn())

    def _on_radio_value_changed(self, model):
        camera_group: OrPropertyGroup = self._sim_manager.get_config_file_property_group("sensor", "camera_group")
        new_val = model.get_value_as_int()
        if new_val != camera_group.get_mode():
            camera_group.set_mode(new_val)
            asyncio.ensure_future(self.build_camera_ui())

    def build_ui(self):
        self._cam_ui_stack = ui.VStack()

    async def build_camera_ui(self):
        self._cam_ui_stack.clear()
        await omni.kit.app.get_app().next_update_async()
        camera_group: OrPropertyGroup = self._sim_manager.get_config_file_property_group("sensor", "camera_group")
        mode = camera_group.get_mode() if camera_group is not None else -1
        with self._cam_ui_stack:
            # No UI if mode is error
            if mode == -1:
                self._radio_collection = None
                self._cam_list_stack = None
                self._lidar_list_stack = None
                self._cam_num_field = None
                self._lidar_num_field = None
                return
            # Num/List switch buttons
            with ui.HStack():
                ui.Label("Camera Property Type", width=150)
                self._radio_collection = ui.RadioCollection()
                self._radio_collection.model.set_value(mode)
                self._radio_collection.model.add_value_changed_fn(self._on_radio_value_changed)
                ui.RadioButton(text="Num", height=20, width=20, radio_collection=self._radio_collection)
                ui.RadioButton(text="List", height=20, width=20, radio_collection=self._radio_collection)
            ui.Spacer(height=10)
            # Populate camera num or list UI
            if mode == 0:
                with ui.HStack(height=20):
                    ui.Label("Camera Number", height=20, width=120)
                    self._cam_num_field = ui.IntField()
                    set_property_to_ui(self._cam_num_field, camera_group.get_property("camera_num"))
                    self._cam_num_field.model.add_end_edit_fn(
                        lambda m: set_ui_to_property(self._cam_num_field, camera_group.get_property("camera_num"))
                    )
                # with ui.HStack():
                #     ui.Label("Lidar Number", height=20, width=120)
                #     self._lidar_num_field = ui.IntField(width=100, height=20)

                #     set_property_to_ui(self._lidar_num_field, camera_group.get_property("lidar_num"))
                #     self._lidar_num_field.model.add_end_edit_fn(
                #         lambda m: set_ui_to_property(self._lidar_num_field, camera_group.get_property("lidar_num"))
                #     )
            else:
                with ui.HStack():
                    ui.Label("Camera List", width=UI_DISTANCE, height=20)
                    self._cam_list_stack = ui.VStack(width=300, spacing=5)
                    await self.refresh_cam_list_stack()
                # with ui.HStack():
                #     ui.Label("Lidar List", alignment=ui.Alignment.TOP, width=UI_DISTANCE)
                #     self._lidar_list_stack = ui.VStack(width=300, spacing=5)
                #     await self.refresh_lidar_list_stack()
            ui.Spacer(height=5)
