"""Bind material to prim dialog class"""
_all__ = ["MaterialDialogs"]

import weakref
import omni.kit.material.library
import omni.kit.app
from typing import List
from omni import ui
from pxr import Usd, UsdShade
from .search_widget import SearchWidget
from .listbox_widget import MaterialListBoxWidget

LABEL_HEIGHT = 18


class MaterialDialogs():
    """Bind material to prim dialog class"""
    def __init__(self):
        """Initialize class function."""
        import carb.settings

        self._theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._search_widget = SearchWidget(theme=self._theme, icon_path=None)
        self._listbox_widget = None
        self._dialog_window = None
        self.strengths = {
            "Weaker than Descendants": UsdShade.Tokens.weakerThanDescendants,
            "Stronger than Descendants": UsdShade.Tokens.strongerThanDescendants,
        }

    def destroy(self):
        """Destroy function. Class cleanup function."""
        self._listbox_widget = None
        if self._search_widget:
            self._search_widget.destroy()
        self._search_widget = None
        self._theme = None
        self.strengths = None
        del self._dialog_window

    def bind_material_to_prims_dialog(self, stage: Usd.Stage, prims: list) -> None:
        """
        Show dialog to user, so they an select material and bind to prims.

        Args:
            stage (Usd.Stage): stage
            prims (list): list of prims to bind to.
        """
        if len(prims) == 1:
            window_name = f"Bind material to {prims[0].GetPath().name}"
        else:
            window_name = f"Bind material to {len(prims)} selected models"

        self._dialog_window = ui.Window(
            window_name + "###context_menu_bind",
            width=500,
            height=0,
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR,
        )
        with self._dialog_window.frame:
            with ui.VStack(
                height=0,
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
            ):

                class ComboListItem(ui.AbstractItem):
                    def __init__(self, model):
                        super().__init__()
                        self.model = ui.SimpleStringModel(model)

                class ComboListModel(ui.AbstractItemModel):
                    def __init__(self, materials_list, default_index):
                        super().__init__()

                        self._default_index = default_index
                        self._current_index = ui.SimpleIntModel(default_index)
                        self._current_index.add_value_changed_fn(lambda a: self._item_changed(None))
                        self._items = [ComboListItem(text) for text in materials_list]

                    def get_item_children(self, item):
                        return self._items

                    def get_item_value_model(self, item, column_id):
                        if item is None:
                            return self._current_index
                        return item.model

                    def get_current_index(self):
                        return self._current_index.get_value_as_int()

                    def get_current_string(self):
                        return self._items[self._current_index.get_value_as_int()].model.get_value_as_string()

                    def is_default(self):
                        return self.get_current_index() == self._default_index

                    def set_value(self, index):
                        self._current_index.set_value(index)

                materials_list = ["$NONE$"]

                for prim in prims:
                    if isinstance(prim, Usd.Prim):
                        materials_index, strength_index = self._get_bound_material_info(prim, materials_list)
                    else:
                        actual_prim = prim.GetPrim()
                        materials_index, strength_index = self._get_bound_material_info(actual_prim, materials_list)
                    # use 1st bound material as source
                    if materials_index > 0:
                        break

                with ui.VStack(spacing=5):
                    def update_material(model, b):
                        self._search_widget.set_text(model.get_value_as_string())

                    self._build_material_popup(materials_list, materials_index, update_material)
                    combo_widget_strength = ui.ComboBox(ComboListModel(self.strengths.keys(), strength_index))

                ui.Spacer(width=5, height=5)
                with ui.HStack(spacing=5):
                    ui.Button(
                        "Ok",
                        clicked_fn=lambda w=weakref.ref(self._dialog_window), s=self._search_widget, sm=weakref.ref(combo_widget_strength.model):
                            self._bind_material_to_prim(
                                stage,
                                prims,
                                w,
                                s.get_text(),
                                sm
                            ),
                        identifier="assign_material_ok_button"
                    )
                    ui.Button(
                        "Cancel",
                        clicked_fn=lambda w=weakref.ref(self._dialog_window), s=self._search_widget, sm=weakref.ref(combo_widget_strength.model):
                            self._bind_material_to_prim(
                                stage,
                                None,
                                w,
                                s.get_text(),
                                sm
                            ),
                        identifier="assign_material_cancel_button"
                    )

    def _build_material_popup(self, material_list: List[str], material_index: int, bind_material_fn: callable):
        name_field, listbox_button, goto_button = self._search_widget.build_ui_popup(search_size=LABEL_HEIGHT,
                                                                                popup_text=material_list[material_index] if material_index >= 0 else "Mixed",
                                                                                index=material_index,
                                                                                update_fn=bind_material_fn,
                                                                                widget_flags=SearchWidget.WidgetFlags.SHOW_OPEN_BUTTON)

        name_field.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: self._show_material_popup(f, material_index, bind_material_fn))
        listbox_button.set_mouse_pressed_fn(lambda x, y, b, m, f=name_field: self._show_material_popup(f, material_index, bind_material_fn))

    def _show_material_popup(self, name_field: ui.StringField, material_index: int, bind_material_fn: callable):
        if self._listbox_widget:
            self._listbox_widget.clean()
            del self._listbox_widget
            self._listbox_widget = None

        self._listbox_widget = MaterialListBoxWidget(icon_path=None, index=material_index, on_click_fn=bind_material_fn, theme=self._theme)
        self._listbox_widget.set_parent(name_field)
        self._listbox_widget.set_selection_on_loading_complete(name_field.model.get_value_as_string() if material_index >= 0 else None)
        self._listbox_widget.build_ui()

    def _bind_material_to_prim(
        self,
        stage: Usd.Stage,
        prims: list,
        window: weakref,
        material_path: str,
        model_strength: ui.AbstractItemModel,
    ):
        model_strength = model_strength()
        if prims and model_strength:
            material_strength = None
            if not model_strength.is_default():
                material_strength = (
                    UsdShade.Tokens.weakerThanDescendants
                    if model_strength.get_current_index() == 0
                    else UsdShade.Tokens.strongerThanDescendants
                )
            prim_list = [i.GetPath() for i in prims]
            omni.kit.commands.execute(
                "BindMaterial", prim_path=prim_list, material_path=material_path, strength=material_strength
            )
            if not model_strength.is_default():
                omni.kit.undo.begin_group()
                for prim in prims:
                    material_path = None
                    mat, rel = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                    if mat:
                        material_path = mat.GetPath().pathString
                        if rel and rel.GetPrim() != prim:
                            material_path = None
                    material_strength = (
                        UsdShade.Tokens.weakerThanDescendants
                        if model_strength.get_current_index() == 0
                        else UsdShade.Tokens.strongerThanDescendants
                    )
                    omni.kit.commands.execute(
                        "BindMaterial",
                        prim_path=prim.GetPath(),
                        material_path=material_path,
                        strength=material_strength,
                    )
                omni.kit.undo.end_group()

        if window():
            window().visible = False

    def _get_bound_material_info(self, prim: Usd.Prim, materials_list: list) -> List[str]:
        materials_index = 0
        strength_index = 0
        mat, rel = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        if mat:
            try:
                mat_path = mat.GetPath().pathString
                if not mat_path in materials_list:
                    materials_list.append(mat_path)
                materials_index = materials_list.index(mat_path)
            except Exception:
                pass
        if rel:
            if UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel) == UsdShade.Tokens.strongerThanDescendants:
                strength_index = 1
            if rel.GetPrim() != prim:
                materials_list[materials_index] += " (inherited)"

        return materials_index, strength_index
