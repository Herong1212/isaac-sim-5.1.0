# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from .properties_scheme_delegate import NavMeshAreaAPISchemeDelegate, NavMeshExcludeAPISchemeDelegate
from .utils import Prompt, refresh_property_window
from omni.kit.property.usd.usd_property_widget import SchemaPropertiesWidget, UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutProperty
import omni.anim.navigation.core as nav
import omni.ui as ui
import omni.usd

from pxr import Sdf, Usd
import NavSchema
from typing import List, Optional
import weakref

NAVMESH_AREA_ATTR = "nav:area"
NAVMESH_AREA_ATTRS = [NAVMESH_AREA_ATTR]

NAVMESH_VOLUME_TYPE_ATTR = "nav:volume:type"
NAVMESH_VOLUME_ATTRS = [NAVMESH_VOLUME_TYPE_ATTR]

EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
ICON_PATH = f"{EXT_PATH}/icons"
REMOVE_BUTTON_STYLE = style = {"image_url": f"{ICON_PATH}/remove.svg", "margin": 0, "padding": 0}


class NavigationProperties:
    def __init__(self, navmesh_menu, ext_id):
        self._registered = False
        self._ext_id = ext_id
        self.initialize(navmesh_menu)

    def initialize(self, navmesh_menu):
        if self._registered:
            return
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            self._navmesh_area_api_properties_widget = NavMeshAreaAPIPropertiesWidget(navmesh_menu)
            self._navmesh_exclude_api_properties_widget = NavMeshExcludeAPIPropertiesWidget(navmesh_menu)
            w.register_widget("prim", "navmesh_area_api", self._navmesh_area_api_properties_widget)
            w.register_widget("prim", "navmesh_exclude_api", self._navmesh_exclude_api_properties_widget)
            w.register_scheme_delegate("prim", "navmesh_area_api_scheme", NavMeshAreaAPISchemeDelegate())
            w.register_scheme_delegate("prim", "navmesh_exclude_api_scheme", NavMeshExcludeAPISchemeDelegate())
            self._registered = True

    def destroy(self):
        if not self._registered:
            return
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            w.unregister_scheme_delegate("prim", "navmesh_volume_scheme")
            w.unregister_scheme_delegate("prim", "navmesh_exclude_api_scheme")
            w.unregister_widget("prim", "navmesh_area_api")
            w.unregister_widget("prim", "navmesh_exlude_api")


class NavMeshAreaItem(ui.AbstractItem):
    def __init__(self, str):
        super().__init__()
        self.model = ui.SimpleStringModel(str)


class NavMeshAreaItemModel(ui.AbstractItemModel):
    def __init__(self, prim_paths: List[Sdf.Path]):
        super().__init__()
        self._prim_paths = prim_paths
        self._stage = omni.usd.get_context().get_stage()
        self._nav_area_items = []
        inav = nav.acquire_interface()

        def get_nav_area_index(prim_path) -> int:
            prim = self._stage.GetPrimAtPath(prim_path)
            nav_area_name = prim.GetAttribute(NAVMESH_AREA_ATTR).Get()
            return inav.find_area(nav_area_name)

        index = get_nav_area_index(self._prim_paths[0])
        if (index == -1):
            # if the first index is not found. Then it was removed so pick the first one.
            index = 0
        else:
            # otherwise we see if they are all matching.
            if len(self._prim_paths) > 1:
                for i in range(1, len(self._prim_paths)):
                    next_index = get_nav_area_index(self._prim_paths[i])
                    if next_index != index:
                        # if any do not match. Then we have mixed, so pick -1 to allow multi-select
                        index = -1
                        break
        self._selected_index = ui.SimpleIntModel(index)
        self._selected_index.add_value_changed_fn(
            self._on_seleceted_index_changed
        )
        area_count = inav.get_area_count()
        for i in range(area_count):
            area_name = inav.get_area_name(i)
            self._nav_area_items.append(NavMeshAreaItem(area_name))

    def get_item_children(self, item):
        return self._nav_area_items

    def get_item_value_model(self, item=None, column_id=0):
        if item is None:
            return self._selected_index
        return item.model

    def _on_seleceted_index_changed(self, model):
        selected_index = model.as_int
        nav_area_name = self._nav_area_items[selected_index].model.as_string
        for prim_path in self._prim_paths:
            prim = self._stage.GetPrimAtPath(prim_path)
            prim.GetAttribute(NAVMESH_AREA_ATTR).Set(nav_area_name)
        self._item_changed(None)


class NavMeshAreaAPIPropertiesWidget(SchemaPropertiesWidget):
    def __init__(self, navmesh_menu, title: Optional[str] = "NavMesh"):
        super().__init__(title, NavSchema.NavMeshAreaAPI, False)
        self._navmesh_menu = weakref.ref(navmesh_menu)
        self._nav_area_field_subs = {}
        self._nav_area_prop_hidden = False

    def clean(self):
        sub_keys = self._nav_area_field_subs.keys()
        for sub_key in sub_keys:
            self._nav_area_field_subs[sub_key] = None
        super().clean()

    def _on_edit_navmesh(self):
        navmesh_menu = self._navmesh_menu()
        if navmesh_menu:
            navmesh_menu.show_window()

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        self._nav_area_prop_hidden = False
        show_widget = False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            if prim.HasAPI(NavSchema.NavMeshAreaAPI):
                if prim.GetAttribute(NAVMESH_VOLUME_TYPE_ATTR).Get() == "Exclude":
                    self._nav_area_prop_hidden = True
                show_widget = True
        return show_widget

    def _filter_props_to_build(self, props):
        filtered_props = []
        for prop in props:
            if prop.GetName() in NAVMESH_VOLUME_ATTRS:
                filtered_props.append(prop)
            elif prop.GetName() in NAVMESH_AREA_ATTRS and not self._nav_area_prop_hidden:
                filtered_props.append(prop)
        return filtered_props

    def _on_usd_changed(self, notice, stage):
        if stage != self._payload.get_stage():
            return
        if not self._collapsable_frame:
            return
        if len(self._payload) == 0:
            return
        # Widget is pending rebuild, no need to check for dirty
        if self._pending_rebuild_task is not None:
            return

        for path in notice.GetChangedInfoOnlyPaths():
            if path.name.endswith(NAVMESH_VOLUME_TYPE_ATTR):
                refresh_property_window()
                return

        super()._on_usd_changed(notice=notice, stage=stage)

    def _customize_props_layout(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            CustomLayoutProperty(NAVMESH_VOLUME_TYPE_ATTR)
            CustomLayoutProperty(NAVMESH_AREA_ATTR)

        return frame.apply(props)

    def build_impl(self):
        if self._collapsable:
            self._collapsable_frame = ui.CollapsableFrame(
                self._title,
                build_header_fn=self._build_custom_frame_header,
                collapsed=self._collapsed
            )

            def on_collapsed_changed(collapsed):
                self._collapsed = collapsed

            self._collapsable_frame.set_collapsed_changed_fn(on_collapsed_changed)
        else:
            self._collapsable_frame = ui.Frame(
                height=10,
                style={"Frame": {"padding": 5}}
            )
        self._collapsable_frame.set_build_fn(self._build_frame)

    def _build_custom_frame_header(self, collapsed, text):
        if collapsed:
            alignment = ui.Alignment.RIGHT_CENTER
            width = 5
            height = 7
        else:
            alignment = ui.Alignment.CENTER_BOTTOM
            width = 7
            height = 5

        with ui.HStack(spacing=8):
            with ui.VStack(width=0):
                ui.Spacer()
                ui.Triangle(
                    style_type_name_override="CollapsableFrame.Header",
                    width=width,
                    height=height,
                    alignment=alignment
                )
                ui.Spacer()
            ui.Label(text, style_type_name_override="CollapsableFrame.Header")
            with ui.HStack(width=0):
                ui.Spacer(width=8)
                with ui.VStack(width=0):
                    ui.Button(
                        "Edit NavMesh",
                        identifier="edit_navmesh",
                        image_url="resources/glyphs/pencil.svg",
                        image_width=14,
                        image_height=14,
                        height=16,
                        width=110,
                        style={"border_radius": 4, "stack_direction": ui.Direction.LEFT_TO_RIGHT},
                    ).set_mouse_pressed_fn(lambda *_: self._on_edit_navmesh())
            with ui.HStack(width=0):
                ui.Spacer(width=8)
                with ui.VStack(width=0):
                    ui.Spacer(height=5)
                    ui.Button(style=REMOVE_BUTTON_STYLE, height=16, width=16).set_mouse_pressed_fn(lambda *_: self._on_remove_with_prompt())
                ui.Spacer(width=5)

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        if ui_prop.attr_name == NAVMESH_AREA_ATTR:
            self._nav_area_model = NavMeshAreaItemModel(prim_paths)
            with ui.HStack(spacing=4):
                label_kwargs = {"name": "label", "width": 160, "height": 18}
                display_name = ui_prop.metadata.get(Sdf.PropertySpec.DisplayNameKey, ui_prop.attr_name)
                ui.Label(display_name, **label_kwargs)
                ui.Spacer(width=5)
                ui.ComboBox(self._nav_area_model)
        else:
            return super().build_property_item(stage, ui_prop, prim_paths)

    def _on_remove_with_prompt(self):
        def on_remove_navmesh_area_api():
            selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            for selected_path in selected_paths:
                omni.kit.commands.execute("RemoveNavMeshAPI", prim_path=selected_path, api=NavSchema.NavMeshAreaAPI)
                #remove nav:area as well
                omni.kit.commands.execute("RemovePropertyCommand", prop_path=Sdf.Path(selected_path).AppendProperty(NAVMESH_AREA_ATTR))

        prompt = Prompt(
            "Remove NavMesh Area?", "Are you sure you want to remove the 'NavMesh Area' component?", "Yes", "No",
            ok_button_fn=lambda: on_remove_navmesh_area_api(), modal=True
        )
        prompt.show()


class NavMeshExcludeAPIPropertiesWidget(SchemaPropertiesWidget):
    def __init__(self, navmesh_menu, title: Optional[str] = "NavMesh Exclude"):
        super().__init__(title, NavSchema.NavMeshExcludeAPI, False)
        self._navmesh_menu = weakref.ref(navmesh_menu)

    def build_items(self):
        """ Called to build menu items """
        super().build_items()
        if len(self._payload) == 1:
            path = self._payload[0]
            prim = self._get_prim(path)
            if prim is not None and prim.IsValid() and prim.HasAPI(NavSchema.NavMeshExcludeAPI):
                pass

    def build_impl(self):
        if self._collapsable:
            self._collapsable_frame = ui.CollapsableFrame(
                self._title, build_header_fn=self._build_custom_frame_header, collapsed=self._collapsed
            )

            def on_collapsed_changed(collapsed):
                self._collapsed = collapsed

            self._collapsable_frame.set_collapsed_changed_fn(on_collapsed_changed)
        else:
            self._collapsable_frame = ui.Frame(height=10, style={"Frame": {"padding": 5}})
        self._collapsable_frame.set_build_fn(self._build_frame)

    def _on_remove_with_prompt(self):
        def on_remove_navmesh_exclude_api():
            selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            for selected_path in selected_paths:
                omni.kit.commands.execute("RemoveNavMeshAPI", prim_path=selected_path, api=NavSchema.NavMeshExcludeAPI)
            navmesh_menu = self._navmesh_menu()
            if navmesh_menu:
                navmesh_menu.remove_exclusion(list(selected_paths))

        prompt = Prompt(
            "Remove NavMesh Exclude?", "Are you sure you want to remove the 'NavMesh Exclude' component?", "Yes", "No",
            ok_button_fn=lambda: on_remove_navmesh_exclude_api(), modal=True
        )
        prompt.show()

    def _build_custom_frame_header(self, collapsed, text):
        if collapsed:
            alignment = ui.Alignment.RIGHT_CENTER
            width = 5
            height = 7
        else:
            alignment = ui.Alignment.CENTER_BOTTOM
            width = 7
            height = 5

        with ui.HStack(spacing=8):
            with ui.VStack(width=0):
                ui.Spacer()
                ui.Triangle(
                    style_type_name_override="CollapsableFrame.Header", width=width, height=height, alignment=alignment
                )
                ui.Spacer()
            ui.Label(text, style_type_name_override="CollapsableFrame.Header")
            with ui.HStack(width=0):
                ui.Spacer(width=8)
                with ui.VStack(width=0):
                    ui.Spacer(height=5)
                    ui.Button(style=REMOVE_BUTTON_STYLE, height=16, width=16).set_mouse_pressed_fn(lambda *_: self._on_remove_with_prompt())
                ui.Spacer(width=5)
