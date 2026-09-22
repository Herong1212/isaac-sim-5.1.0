__all__ = ["_multi_descendents_dialog"]

import asyncio
import weakref
import omni.ui as ui
import omni.usd
from pxr import Tf, Sdf, Usd, UsdShade, UsdGeom


def _multi_descendents_dialog(prim_paths: list, on_click_fn: callable):
    # more that one target prim is not supported
    if len(prim_paths) != 1:
        on_click_fn(Sdf.Path(""))

    stage = omni.usd.get_context().get_stage()
    root_prim = stage.GetPrimAtPath(prim_paths[0])
    if not root_prim:
        return

    descendents = omni.usd.get_prim_descendents(root_prim)

    # skip if only root_prim
    if descendents == [root_prim]:
        on_click_fn(prim_paths[0])
        return

    dialog_window = ui.Window(
        "Target prim has multiple descendents",
        width=500,
        height=0,
        flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR,
    )
    with dialog_window.frame:
        with ui.VStack(
            height=0,
            spacing=5,
            name="top_level_stack",
            style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
        ):

            def get_bound_material_name(prim: Usd.Prim):
                name = "None"
                bound_material, rel = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                if bound_material and bound_material.GetPrim().IsValid():
                    name = bound_material.GetPrim().GetName()
                    if rel.GetPrim() != prim:
                        name = name + " - Inherited from " + rel.GetPrim().GetName()
                return name

            class ComboListItem(ui.AbstractItem):
                def __init__(self, prim):
                    super().__init__()
                    self.prim = prim
                    self.model = ui.SimpleStringModel(prim.GetPath().name + f" ({get_bound_material_name(prim)})")

            class ComboListModel(ui.AbstractItemModel):
                def __init__(self, prim_list, default_index):
                    super().__init__()

                    self._default_index = default_index
                    self._current_index = ui.SimpleIntModel(default_index)
                    self._current_index.add_value_changed_fn(lambda a: self._item_changed(None))
                    self._items = [ComboListItem(prim) for prim in prim_list]

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

                def set_current_index(self, index):
                    self._current_index.set_value(index)

            with ui.VStack(spacing=5):
                def combo_changed(model, item):
                    items = model.get_item_children(item)
                    prim_path = items[model.get_current_index()].prim.GetPrimPath().pathString
                    omni.usd.get_context().get_selection().set_selected_prim_paths([prim_path], True)

                combo_widget_prims = ui.ComboBox(ComboListModel(descendents, 0))
                combo_widget_prims.identifier="multi_descendents_combo"
                combo_widget_prims.model.add_item_changed_fn(combo_changed)
                omni.usd.get_context().get_selection().set_selected_prim_paths([descendents[0].GetPrimPath().pathString], True)

            def close_window(w: ui.Window, combo_widget_prim: ui.ComboBox, clicked_fn: callable):
                w.visible = False
                async def free_window(w):
                    w.frame.clear()
                    del w

                asyncio.ensure_future(free_window(w))

                if clicked_fn:
                    prim_path = None
                    if combo_widget_prim:
                        model = combo_widget_prim.model
                        items = model.get_item_children(None)
                        prim_path = items[model.get_current_index()].prim.GetPrimPath().pathString

                    on_click_fn(prim_path)

            ui.Spacer(width=5, height=5)
            with ui.HStack(spacing=5):
                ui.Button(
                    "Ok",
                    clicked_fn=lambda w=dialog_window, cw=combo_widget_prims: close_window(w, cw, on_click_fn),
                    identifier="multi_descendents_ok_button"
                )
                ui.Button(
                    "Cancel",
                    clicked_fn=lambda w=dialog_window, cw=combo_widget_prims: close_window(w, None, None),
                    identifier="multi_descendents_cancel_button"
                )
