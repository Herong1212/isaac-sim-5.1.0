# Copyright (c) 2020-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a widget for binding materials to selected USD prims within NVIDIA Omniverse Kit."""

__all__ = ["MaterialBindingWidget"]

import contextlib
import copy
import os
from functools import partial
from typing import List, Optional, Set

import carb
import omni.kit.material.library
import omni.kit.widget.context_menu
import omni.ui as ui
import omni.usd
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.async_engine import run_coroutine
from omni.kit.material.library.listbox_widget import MaterialListBoxWidget
from omni.kit.material.library.search_widget import SearchWidget
from omni.kit.material.library.thumbnail_loader import ThumbnailLoader
from omni.kit.widget.highlight_label import HighlightLabel
from omni.kit.window.property.templates import LABEL_HEIGHT, SimplePropertyWidget
from pxr import Tf, Usd, UsdShade

from .context_menu import show_context_menu
from .material_utils import Constant, get_binding_from_prims


class MaterialBindingWidget(SimplePropertyWidget):
    """A widget designed to bind materials to selected USD prims.

    This widget facilitates the association of materials to prims in USD stages by providing a user interface for selection and assignment. It supports context menus, search functionality, thumbnail previews, and asynchronous material retrieval.

    Args:
        extension_path (Optional[str]): The path where the extension is located. Used for loading icons and other resources.
        add_context_menu (bool): Indicates whether to add a context menu to the widget.
        title (str): The title of the widget.
        material_purpose (str): The purpose of the material (e.g., 'allPurpose', 'preview', etc.).
        filter_fn (Optional[callable]): A function used to filter materials.
        get_materials_async_fn (Optional[callable]): An asynchronous function to retrieve materials.

    Keyword Args:
        collapsed (bool): Specifies whether the widget is initially collapsed.
        collapsable (bool): Specifies whether the widget is collapsible.
        enable_bound_widget (bool): Enables the display of the bound widget.
        enable_strength_widget (bool): Enables the display of the material strength widget."""

    EXTENSION_PATH = None
    """Optional[str]: Path for extension-specific resources."""

    def __init__(
        self,
        extension_path: Optional[str] = None,
        add_context_menu=False,
        title="Materials on selected models",
        material_purpose=UsdShade.Tokens.allPurpose,
        filter_fn=None,
        get_materials_async_fn=None,
        **kwargs,
    ):
        """Initializes a new instance of the MaterialBindingWidget."""
        collapsed = kwargs.get("collapsed", False)
        collapsable = kwargs.get("collapsable", True)
        super().__init__(title=title, collapsed=collapsed, collapsable=collapsable)
        self._strengths = {
            "Weaker than Descendants": UsdShade.Tokens.weakerThanDescendants,
            "Stronger than Descendants": UsdShade.Tokens.strongerThanDescendants,
        }

        if not extension_path:  # pragma: no cover
            extension_path = MaterialBindingWidget.EXTENSION_PATH or ""
            # Error if extension_path is still bool(extension_path) == False ?

        self._extension_path = extension_path
        self._thumbnail_loader = ThumbnailLoader()
        self._task_or_future = None
        self._material_purpose = material_purpose
        self._filter_fn = filter_fn
        self._get_materials_async_fn = get_materials_async_fn

        if self._filter_fn is not None and self._get_materials_async_fn is None:  # pragma: no cover
            carb.log_error(
                "When setting a custom filter in MaterialBindingWidget you must also set get_materials_async_fn with e.g. get_materials_from_stage_async from an instance of MaterialUtils to avoid reusing a non-filtered cached material list."
            )
        self._enable_bound_widget = kwargs.get("enable_bound_widget", True)
        self._enable_strength_widget = kwargs.get("enable_strength_widget", True)

        self._theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._listbox_widget = None
        self._search_widget = SearchWidget(theme=self._theme, icon_path=None)

        self._style = {
            "Image::material": {"margin": 12},
            "Button::material_mixed": {"margin": 10},
            "Button.Image::material_mixed": {"image_url": f"{self._extension_path}/data/icons/material_mixed@3x.png"},
            "Button::material_solo": {"margin": 10},
            "Button.Image::material_solo": {"image_url": f"{self._extension_path}/data/icons/material@3x.png"},
            "Field::prims": {"font_size": Constant.FONT_SIZE},
            "Field::prims_mixed": {"font_size": Constant.FONT_SIZE, "color": Constant.MIXED_COLOR},
            "Label::prim": {"font_size": Constant.FONT_SIZE},
            "ComboBox": {"font_size": Constant.FONT_SIZE},
            "Label::combo_mixed": {
                "font_size": Constant.FONT_SIZE,
                "color": Constant.MIXED_COLOR,
                "margin_width": 5,
            },
        }

        self._listener = None
        self._first_row = False
        self._combo_subscription = None
        self._any_item_visible = False

        self._paste_all_menu = None
        if add_context_menu:
            # paste all on collapsible frame header
            from .context_menu import is_bindable_prim_selected, is_material_copied, is_paste_all, paste_material_all

            menu_dict = {
                "name": "Paste To All",
                "enabled_fn": [is_bindable_prim_selected, is_material_copied, is_paste_all],
                "onclick_fn": paste_material_all,
            }
            self._paste_all_menu = omni.kit.widget.context_menu.add_menu(
                menu_dict, "group_context_menu.Materials on selected models", "omni.kit.window.property"
            )

        usd = omni.usd.get_context()
        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.property.material:material_binding_widget",
                event_name=usd.stage_event_name(event),
                on_event=lambda _: self.reset(),
            )
            for event in (omni.usd.StageEventType.CLOSING, omni.usd.StageEventType.CLOSED)
        ]

    def clean(self):  # pragma: no cover
        """Cleans up the widget's resources."""
        self._thumbnail_loader = None
        if self._listbox_widget:
            self._listbox_widget.clean()
        self._listbox_widget = None
        self._search_widget.clean()
        self._paste_all_menu = None
        super().clean()

    def _materials_changed(self):
        self.request_rebuild()

    def _get_prim(self, prim_path):
        if prim_path:
            stage = self._payload.get_stage()
            if stage:
                return stage.GetPrimAtPath(prim_path)

        return None  # pragma: no cover

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (Dict): The new payload to be handled by the widget.

        Returns:
            bool: True if the payload is valid and handled; False otherwise."""
        if not super().on_new_payload(payload):  # pragma: no cover
            return False

        if not payload:  # pragma: no cover
            return False

        if len(payload) == 0:  # pragma: no cover
            return False

        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if prim and not omni.usd.is_prim_material_supported(prim):
                return False
            if not prim and not Usd.CollectionAPI.IsCollectionAPIPath(prim_path):
                return False

        return True

    def _get_index(self, items: List[str], value: str, default_value: int = 0):
        index = default_value
        with contextlib.suppress(ValueError):
            index = items.index(value)
        return index

    def _get_theme_name(self, darkname, lightname):
        if self._theme == "NvidiaDark":
            return darkname
        return lightname

    def _show_material_popup(self, name_field: ui.StringField, material_index: int, bind_material_fn: callable):
        if self._listbox_widget:
            self._listbox_widget.clean()
            del self._listbox_widget
            self._listbox_widget = None

        self._listbox_widget = MaterialListBoxWidget(
            icon_path=None,
            index=material_index,
            on_click_fn=bind_material_fn,
            theme=self._theme,
            filter_fn=self._filter_fn,
            get_materials_async_fn=self._get_materials_async_fn,
        )
        self._listbox_widget.set_parent(name_field)
        self._listbox_widget.set_selection_on_loading_complete(
            name_field.model.get_value_as_string() if material_index >= 0 else None
        )
        self._listbox_widget.build_ui()

    def _build_material_popup(
        self,
        material_list: List[str],
        material_index: int,
        thumbnail_image: ui.Button,
        bound_prim_list: Set[Usd.Prim],
        material_missing: bool,
        bind_material_fn: callable,
        on_goto_fn: callable,
        on_dragdrop_fn: callable,
    ):
        def drop_accept(url):
            if len(url.split("\n")) > 1:
                carb.log_warn("build_material_popup multi-file drag/drop not supported")
                return False

            if url.startswith("material::"):
                return True

            url_ext = os.path.splitext(url)[1]
            return url_ext.lower() in [".mdl"]

        def dropped_mtl(event, bind_material_fn):
            url = event.mime_data
            subid = None
            # remove omni.kit.browser.material "material::" prefix
            if url.startswith("material::"):
                url = url[10:]
                parts = url.split(".mdl@")
                if len(parts) == 2:
                    subid = parts[1]
                    url = url.replace(f".mdl@{subid}", ".mdl")

            bind_material_fn(url=url, subid=subid)

        name_field, listbox_button, goto_button = self._search_widget.build_ui_popup(
            search_size=LABEL_HEIGHT,
            popup_text=material_list[material_index] if material_index >= 0 else "Mixed",
            index=material_index,
            update_fn=bind_material_fn,
            missing=material_missing,
        )

        name_field.set_mouse_pressed_fn(
            lambda x, y, b, m, f=name_field: self._show_material_popup(f, material_index, bind_material_fn)
        )
        name_field.set_accept_drop_fn(drop_accept)
        name_field.set_drop_fn(partial(dropped_mtl, bind_material_fn=on_dragdrop_fn))

        listbox_button.set_mouse_pressed_fn(
            lambda x, y, b, m, f=name_field: self._show_material_popup(f, material_index, bind_material_fn)
        )

        if material_index > 0 and goto_button:
            goto_button.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: on_goto_fn(f.model))

        if self._collapsable_frame:

            def mouse_clicked(b, f):
                if b == 0:
                    on_goto_fn(f.model)
                elif b == 1:
                    show_context_menu(self._payload.get_stage(), f.model.get_value_as_string(), bound_prim_list)

            thumbnail_image.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: mouse_clicked(b, f))

        thumbnail_image.set_accept_drop_fn(drop_accept)
        thumbnail_image.set_drop_fn(partial(dropped_mtl, bind_material_fn=on_dragdrop_fn))

    def _build_combo(self, material_list: List[str], material_index: int, on_fn: callable):
        def set_visible(widget, visible):
            widget.visible = visible

        with ui.ZStack():
            combo = ui.ComboBox(material_index, *material_list)
            combo.model.add_item_changed_fn(on_fn)
            if material_index == -1:
                placeholder = ui.Label(
                    "Mixed",
                    height=LABEL_HEIGHT,
                    name="combo_mixed",
                )
                self._combo_subscription.append(
                    combo.model.get_item_value_model().subscribe_value_changed_fn(
                        lambda m, w=placeholder: set_visible(w, m.as_int < 0)
                    )
                )
            return combo

    def _get_type_label_and_bounded_prims(self, bound_prim_list: Set[str]):
        prim_style = "prims"
        type_label = "Prim"
        if len(bound_prim_list) == 1:

            if isinstance(bound_prim_list[0], Usd.Prim):
                bound_prims = bound_prim_list[0].GetPath().pathString
            elif isinstance(bound_prim_list[0], Usd.CollectionAPI):  # pragma: no cover
                bound_prims = bound_prim_list[0].GetCollectionPath().pathString
                type_label = "Collection"
            else:
                bound_prims = bound_prim_list[0]
        elif len(bound_prim_list) > 1:
            bound_prims = Constant.MIXED
            prim_style = "prims_mixed"
        else:
            bound_prims = "None"
        return prim_style, type_label, bound_prims

    def build_thumbnail_widget(self, style_name, material_path, index):
        """Builds a thumbnail widget.

        Args:
            style_name (str): Style name for the thumbnail widget.
            material_path (str): Path of the material for the thumbnail.
            index (int): Index of the thumbnail in the list.

        Returns:
            ui.Button: A UI button with the thumbnail image."""
        with ui.ZStack(width=0):
            image_button = ui.Button(
                "",
                width=Constant.ICON_SIZE,
                height=Constant.ICON_SIZE,
                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                name=style_name,
                identifier="preview_drop_target",
            )

            if index != -1:
                material_prim = self._get_prim(material_path)
                if material_prim:

                    def on_image_progress(button: ui.Button, image: ui.Image, progress: float):
                        if progress > 0.999:
                            button.image_url = image.source_url
                            image.visible = False

                    thumbnail_image = ui.Image(
                        width=Constant.ICON_SIZE,
                        height=Constant.ICON_SIZE,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        name="material",
                    )
                    self._thumbnail_loader.load(material_prim, thumbnail_image)
                    # callback when image is loading
                    thumbnail_image.set_progress_changed_fn(
                        lambda p, b=image_button, i=thumbnail_image: on_image_progress(b, i, p)
                    )
            return image_button

    def build_bound_widget(self, type_label, prim_style, bound_prims):
        """Builds a widget showing the bound type and prims.

        Args:
            type_label (str): Label indicating the type (Prim or Collection).
            prim_style (str): Style of the primary label.
            bound_prims (str): Label showing the bound prims or collections."""
        with ui.HStack(height=0):
            HighlightLabel(
                type_label,
                width=Constant.BOUND_LABEL_WIDTH,
                height=LABEL_HEIGHT,
                name="prim",
                highlight=self._filter.name,
            )
            ui.StringField(
                name=prim_style, identifier="bound_prim_field", height=LABEL_HEIGHT, enabled=False
            ).model.set_value(bound_prims)

    def build_strength_widget(self, strength_value, on_strength_fn):
        """Builds a widget for adjusting material binding strength.

        Args:
            strength_value (str): Initial strength value.
            on_strength_fn (callable): Function to call when strength is changed."""
        with ui.HStack(height=0):
            HighlightLabel(
                "Strength",
                width=Constant.BOUND_LABEL_WIDTH,
                height=LABEL_HEIGHT,
                name="prim",
                highlight=self._filter.name,
            )
            index = self._get_index(list(self._strengths.values()), strength_value, -1)
            self._build_combo(list(self._strengths.keys()), index, on_strength_fn)

    def _build_binding_info(
        self,
        inherited: bool,
        style_name: str,
        material_list: List[str],
        material_path: str,
        strength_value: str,
        bound_prim_list: Set[str],
        material_missing: bool,
        on_material_fn: callable,
        on_strength_fn: callable,
        on_goto_fn: callable,
        on_dragdrop_fn: callable,
    ):
        ## fixup Constant.SDF_PATH_INVALID vs "None"
        material_list = copy.copy(material_list)
        if material_list[0] == Constant.SDF_PATH_INVALID:
            material_list[0] = "None"
        if material_path == Constant.SDF_PATH_INVALID:
            material_path = "None"

        prim_style, type_label, bound_prims = self._get_type_label_and_bounded_prims(bound_prim_list)

        if not self._first_row:
            ui.Separator(height=10)
        self._first_row = False

        index = self._get_index(material_list, material_path, -1)

        with ui.HStack(style=self._style):
            image_button = self.build_thumbnail_widget(style_name, material_path, index)

            with ui.VStack(spacing=10):
                if self._enable_bound_widget and self._filter.matches(type_label):
                    self._any_item_visible = True
                    self.build_bound_widget(type_label, prim_style, bound_prims)

                if index != -1 and inherited:
                    inherited_list = copy.copy(material_list)
                    inherited_list[index] = f"{inherited_list[index]} (inherited)"
                    self._build_material_popup(
                        inherited_list,
                        index,
                        image_button,
                        bound_prim_list,
                        material_missing,
                        on_material_fn,
                        on_goto_fn,
                        on_dragdrop_fn,
                    )
                else:
                    self._build_material_popup(
                        material_list,
                        index,
                        image_button,
                        bound_prim_list,
                        material_missing,
                        on_material_fn,
                        on_goto_fn,
                        on_dragdrop_fn,
                    )

                if self._enable_strength_widget and self._filter.matches("Strength"):
                    self._any_item_visible = True
                    self.build_strength_widget(strength_value, on_strength_fn)

    def bind_material_to_prims(self, bind_material_path, items):
        """Binds a material to prims.

        Args:
            bind_material_path (str): Path of the material to bind.
            items (List[Tuple]): List of items to bind the material to."""
        prim_path_list = []
        strength_list = []
        for prim_path, material_name, strength in items:
            if str(material_name) != str(bind_material_path):
                prim_path_list.append(prim_path)
                strength_list.append(strength)

        if str(bind_material_path) == Constant.SDF_PATH_INVALID:
            bind_material_path = None

        omni.kit.commands.execute(
            "BindMaterial",
            material_path=bind_material_path,
            prim_path=prim_path_list,
            strength=strength_list,
            material_purpose=self._material_purpose,
        )

    def get_on_material_changed_callback(self, material_list):
        """Gets a callback for when the material selection changes.

        Args:
            material_list (List[str]): List of available materials.

        Returns:
            callable: A callback function."""

        def on_material_changed(model, item, items):
            if isinstance(model, omni.ui.AbstractItemModel):
                index = model.get_item_value_model().as_int
                if index < 0:  # pragma: no cover
                    carb.log_error(f"on_material_changed with invalid index {index}")
                    return
                bind_material_path = material_list[index] if material_list[index] != Constant.SDF_PATH_INVALID else None
            elif isinstance(model, omni.ui.SimpleStringModel):
                bind_material_path = model.get_value_as_string()
                if bind_material_path == "None":
                    bind_material_path = None
            else:  # pragma: no cover
                carb.log_error(f"on_material_changed model {type(model)} unsupported")
                return

            self.bind_material_to_prims(bind_material_path, items)
            self.request_rebuild()

        return on_material_changed

    def get_on_strength_changed_callback(self):
        """Gets a callback for when the material strength changes.

        Returns:
            callable: A callback function."""

        def on_strength_changed(model, item, relationships):
            index = model.get_item_value_model().as_int
            if index < 0:
                carb.log_error(f"on_strength_changed with invalid index {index}")
                return
            bind_strength = list(self._strengths.values())[index]
            omni.kit.undo.begin_group()
            for relationship in relationships:
                omni.kit.commands.execute("SetMaterialStrength", rel=relationship, strength=bind_strength)
            omni.kit.undo.end_group()

            self.request_rebuild()

        return on_strength_changed

    def get_on_material_goto_callback(self):
        """Gets a callback for navigating to a material.

        Returns:
            callable: A callback function."""

        def on_material_goto(model, items):
            prim_list = sorted(set({item[1] for item in items if item[1] != Constant.SDF_PATH_INVALID}))
            if prim_list:
                omni.usd.get_context().get_selection().set_selected_prim_paths(prim_list, True)
            else:
                carb.log_warn("on_material_goto failed. No materials in list")

        return on_material_goto

    def get_on_dragdrop_callback(self):
        """Gets a callback for handling drag and drop operations.

        Returns:
            callable: A callback function."""

        def on_dragdrop(url, items, subid=""):
            if len(url.split("\n")) > 1:  # pragma: no cover
                carb.log_warn("build_binding_info multi-file drag/drop not supported")
                return

            def on_create_func(mtl_prim):
                self.bind_material_to_prims(mtl_prim.GetPath(), items)
                self.request_rebuild()

            def reload_frame(prim):
                self._materials_changed()

            stage = self._payload.get_stage()
            mtl_name, _ = os.path.splitext(os.path.basename(url))

            def loaded_mdl_subids(mtl_list, mdl_path, filename, subid):
                if not mtl_list:  # pragma: no cover
                    return

                if subid:
                    omni.kit.material.library.create_mdl_material(
                        stage=stage, mtl_url=mdl_path, mtl_name=subid, on_create_fn=on_create_func, mtl_real_name=subid
                    )
                    return

                if len(mtl_list) > 1:
                    prim_paths = [prim_path for prim_path, material_name, strength in items]
                    omni.kit.material.library.custom_material_dialog(
                        mdl_path=mdl_path, bind_prim_paths=prim_paths, on_complete_fn=reload_frame
                    )
                    return

                omni.kit.material.library.create_mdl_material(
                    stage=stage,
                    mtl_url=mdl_path,
                    mtl_name=mtl_name,
                    on_create_fn=on_create_func,
                    mtl_real_name=mtl_list[0].name if len(mtl_list) > 0 else "",
                )

            # get subids from material
            self._task_or_future = run_coroutine(
                omni.kit.material.library.get_subidentifier_from_mdl(
                    mdl_file=url,
                    on_complete_fn=lambda mlst, p=url, n=mtl_name: loaded_mdl_subids(
                        mtl_list=mlst, mdl_path=p, filename=n, subid=subid
                    ),
                    show_alert=True,
                )
            )

        return on_dragdrop

    def build_items(self):
        """Builds the items for the widget based on the current payload."""
        if not self._payload:  # pragma: no cover
            return
        binding = get_binding_from_prims(self._payload.get_stage(), self._payload, self._material_purpose)
        if binding is None:  # pragma: no cover
            return
        material_list = [Constant.SDF_PATH_INVALID] + list(binding["material"])

        stage = self._payload.get_stage()
        if not stage or len(self._payload) == 0:  # pragma: no cover
            return

        if not self._listener:
            self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)

        self._combo_subscription = []
        self._first_row = True

        data = binding["material"]

        # show mixed material for all selected prims
        if len(data) > 1:
            self._build_binding_info(
                inherited=False,
                style_name="material_mixed",
                material_list=material_list,
                material_path=Constant.MIXED,
                strength_value=binding["strength"],
                bound_prim_list=list(binding["bound"]),
                material_missing=binding["missing"],
                on_material_fn=partial(
                    self.get_on_material_changed_callback(material_list), items=list(binding["bound_info"])
                ),
                on_strength_fn=partial(
                    self.get_on_strength_changed_callback(), relationships=list(binding["relationship"])
                ),
                on_goto_fn=partial(
                    self.get_on_material_goto_callback(), items=list(binding["bound_info"] | binding["inherited_info"])
                ),
                on_dragdrop_fn=partial(self.get_on_dragdrop_callback(), items=list(binding["bound_info"])),
            )

        for material_path, item in data.items():
            if item["bound"]:
                self._build_binding_info(
                    inherited=False,
                    style_name="material_solo",
                    material_list=material_list,
                    material_path=material_path,
                    strength_value=item["strength"],
                    bound_prim_list=list(item["bound"]),
                    material_missing=binding["missing"],
                    on_material_fn=partial(
                        self.get_on_material_changed_callback(material_list), items=list(binding["bound_info"])
                    ),
                    on_strength_fn=partial(
                        self.get_on_strength_changed_callback(), relationships=list(item["relationship"])
                    ),
                    on_goto_fn=partial(self.get_on_material_goto_callback(), items=list(item["bound_info"])),
                    on_dragdrop_fn=partial(self.get_on_dragdrop_callback(), items=list(item["bound_info"])),
                )

        for material_path, item in data.items():
            if item["inherited"]:
                self._build_binding_info(
                    inherited=True,
                    style_name="material_solo",
                    material_list=material_list,
                    material_path=material_path,
                    strength_value=item["strength"],
                    bound_prim_list=list(item["inherited"]),
                    material_missing=binding["missing"],
                    on_material_fn=partial(
                        self.get_on_material_changed_callback(material_list), items=list(binding["inherited_info"])
                    ),
                    on_strength_fn=partial(
                        self.get_on_strength_changed_callback(), relationships=list(item["relationship"])
                    ),
                    on_goto_fn=partial(self.get_on_material_goto_callback(), items=list(item["inherited_info"])),
                    on_dragdrop_fn=partial(self.get_on_dragdrop_callback(), items=list(item["inherited_info"])),
                )

    def reset(self):
        """Resets the widget to its initial state."""
        if self._listener:
            self._listener.Revoke()
            self._listener = None
        super().reset()

    def _on_usd_changed(self, notice, stage):
        if self._pending_rebuild_task:
            return
        items = set(notice.GetResyncedPaths() + notice.GetChangedInfoOnlyPaths())
        if any(path.elementString == ".material:binding" for path in items):
            self.request_rebuild()
