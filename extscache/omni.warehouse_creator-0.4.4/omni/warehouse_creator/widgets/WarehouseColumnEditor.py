import asyncio
from enum import Enum
from functools import partial

import omni
import omni.ui as ui
from omni.warehouse_creator.utils import (
    GHOST_MAT_NAME,
    WAREHOUSE_SHAPE,
    get_ghost_column_status,
    get_variant_from_prim_name,
    make_ghost_columns,
    toggle_ghost_column,
)
from pxr import Gf, Sdf, Usd, UsdGeom

WAREHOUSE_COLUMN_VARIANTS = ["Column_a01", "Column_a02", "Column_a03", "Column_a04", "Column_a05"]


class WarehouseColumnEditorWidget:
    def __init__(self):
        self._warehouse_grid_map = None
        self._warehouse_base = None
        self._selection = omni.usd.get_context().get_selection()
        self._events = omni.usd.get_context().get_stage_event_stream()
        self._stage_event_subscription = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Warehouse Column Editor"
        )
        self.edit_mode = False
        self.edit_button_frame = None
        self.editing_frame = None
        self.columns_prim = None
        self.columns_map = None
        self.warehouse_prim = None
        self.build_ui()

    def shutdown(self):
        self._stage_event_subscription = None
        self._toggle_edit_mode(False)

    def build_ui(self):
        self.top_frame = ui.CollapsableFrame("Column Editor", height=0, tooltip="Select the floorplan prim to enable")
        with self.top_frame:
            with ui.VStack():
                self.edit_button_frame = ui.Frame()
                self.editing_frame = ui.Frame()
            with self.edit_button_frame:
                ui.Button(
                    "Edit Column Placement",
                    clicked_fn=partial(
                        self._toggle_edit_mode,
                    ),
                    style={
                        ":disabled": {
                            "background_color": 0xAA292929,
                        },
                        ":hovered": {"background_color": 0x6600B976},
                        "background_color": 0xAA00B976,
                    },
                )
            with self.editing_frame:
                with ui.VStack(height=0):
                    ui.Label("Click or select columns to toggle")
                    with ui.HStack():
                        ui.Button("Enable All", clicked_fn=partial(self.on_switch_all, True))
                        ui.Button("Flip All", clicked_fn=partial(self.on_switch_all, None))
                        ui.Button("Disable All", clicked_fn=partial(self.on_switch_all, False))
                    with ui.HStack():
                        ui.Button(
                            "Cancel",
                            clicked_fn=partial(
                                self._toggle_edit_mode,
                            ),
                        )
                        ui.Button("confirm", clicked_fn=partial(self._toggle_edit_mode, None, True))

            self.edit_button_frame.visible = not self.edit_mode
            self.editing_frame.visible = self.edit_mode
        self._on_kit_selection_changed(omni.usd.get_context().get_stage())
        # asyncio.ensure_future(self._on_kit_selection_changed(omni.usd.get_context().get_stage()))

    def on_switch_all(self, value=None):
        stage = self.columns_prim.GetStage()
        session_layer = stage.GetSessionLayer()
        with Usd.EditContext(stage, stage.GetRootLayer()):
            with Sdf.ChangeBlock():
                toggle_ghost_column(
                    [c for c in self.columns_prim.GetChildren() if c.GetName() != GHOST_MAT_NAME], value
                )

    def _toggle_edit_mode(self, value=None, confirm_changes=False):
        if value is None:
            value = not self.edit_mode
        self.edit_mode = value
        self.edit_button_frame.visible = not self.edit_mode
        self.editing_frame.visible = self.edit_mode
        if self.edit_mode:
            self.warehouse_prim = self.get_warehouse_prim()
            # print(self.warehouse_prim)
            self.columns_prim, self.columns_map = make_ghost_columns(self.warehouse_prim)
            # print(self.columns_map)
            stage = self.warehouse_prim.GetStage()
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, session_layer):
                for t in self.warehouse_prim.GetChildren():
                    for p in t.GetChildren():
                        if "wall" in p.GetName():
                            for c in [
                                c for c in p.GetChildren() if c.GetName().split("_")[3] not in ["floor", "exteriorwall"]
                            ]:
                                imageable = UsdGeom.Imageable(c)
                                visibility_attr = imageable.GetVisibilityAttr().Set("invisible")
                        else:
                            imageable = UsdGeom.Imageable(p)
                            visibility_attr = imageable.GetVisibilityAttr().Set("invisible")

        else:
            if self.columns_prim:
                stage = self.columns_prim.GetStage()
                session_layer = stage.GetSessionLayer()
                if confirm_changes:
                    with Usd.EditContext(stage, stage.GetRootLayer()):
                        with Sdf.ChangeBlock():
                            for child in [c for c in self.columns_prim.GetChildren() if c.GetName() != GHOST_MAT_NAME]:
                                # print(child)
                                self.toggle_column(child)
                    omni.kit.commands.execute(
                        "RemovePrimSpec",
                        layer_identifier=session_layer.identifier,
                        prim_spec_path=[self.warehouse_prim.GetPath()],
                    )
                with Usd.EditContext(stage, session_layer):
                    stage.RemovePrim(self.columns_prim.GetPath())
            if self.warehouse_prim:
                stage = self.warehouse_prim.GetStage()
                session_layer = stage.GetSessionLayer()
                with Usd.EditContext(stage, session_layer):
                    for t in self.warehouse_prim.GetChildren():
                        for p in t.GetChildren():
                            if "wall" in p.GetName():
                                for c in [
                                    c
                                    for c in p.GetChildren()
                                    if c.GetName().split("_")[3] not in ["floor", "exteriorwall"]
                                ]:
                                    imageable = UsdGeom.Imageable(c)
                                    visibility_attr = imageable.GetVisibilityAttr().Set("inherited")
                            else:
                                imageable = UsdGeom.Imageable(p)
                                visibility_attr = imageable.GetVisibilityAttr().Set("inherited")
            self.warehouse_prim = None
            self.columns_prim = None
            self.columns_map = None
        self._selection.set_selected_prim_paths([], False)
        self._on_kit_selection_changed(omni.usd.get_context().get_stage())
        # asyncio.ensure_future(self._on_kit_selection_changed(omni.usd.get_context().get_stage()))

    def toggle_column(self, ghost_column_prim, enabled=None):
        stage = omni.usd.get_context().get_stage()
        column_index = Gf.Vec2i(*[int(s) for s in ghost_column_prim.GetName().split("_") if s])
        if enabled is None:
            enabled = get_ghost_column_status(ghost_column_prim)
        with Usd.EditContext(stage, stage.GetRootLayer()):
            for column in self.columns_map[column_index]:
                parent = stage.GetPrimAtPath(column).GetParent()
                column_variant = get_variant_from_prim_name(column.name)
                vset = parent.GetVariantSet(get_variant_from_prim_name(column.name))
                if enabled:
                    vset.ClearVariantSelection()
                else:
                    vset.SetVariantSelection("Disabled")

    def get_warehouse_prim(self):
        stage = omni.usd.get_context().get_stage()
        selection = self._selection.get_selected_prim_paths()
        for sel in selection:
            prim = stage.GetPrimAtPath(sel)
            if prim:
                attr = prim.GetAttribute(WAREHOUSE_SHAPE)
                if attr:
                    return prim

    def _on_stage_event(self, event):
        if event.type in [
            int(omni.usd.StageEventType.CLOSED),
            int(omni.usd.StageEventType.OPENED),
            int(omni.usd.StageEventType.SIMULATION_START_PLAY),
            int(omni.usd.StageEventType.SIMULATION_STOP_PLAY),
        ]:
            self._toggle_edit_mode(False)
            self._on_kit_selection_changed(omni.usd.get_context().get_stage())
            # asyncio.ensure_future(self._on_kit_selection_changed(omni.usd.get_context().get_stage()))
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            # print(self, "selection changed")
            self._on_kit_selection_changed(omni.usd.get_context().get_stage())
            # asyncio.ensure_future(self._on_kit_selection_changed(omni.usd.get_context().get_stage()))

    def _on_kit_selection_changed(self, stage):
        selection = self._selection.get_selected_prim_paths()
        if self.edit_mode:
            columns = []
            for sel in selection:
                if sel.startswith(str(self.columns_prim.GetPath())) and len(sel.split("/")) > 2:
                    column = Gf.Vec2i(*[int(s) for s in sel.split("/")[2].split("_") if s])
                    columns.append(column)
            columns = list(set(columns))
            column_prims = [
                stage.GetPrimAtPath(self.columns_prim.GetPath().AppendPath(f"_{c[0]}__{c[1]}_")) for c in columns
            ]
            # print(column_prims)
            if column_prims:
                toggle_ghost_column(column_prims)
            self._selection.set_selected_prim_paths([], False)
        else:
            self.top_frame.enabled = False
            if self.get_warehouse_prim():
                self.top_frame.enabled = True

    def _get_prim(self, prim_path):
        if prim_path:
            stage = self._payload.get_stage()
            if stage:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if "column" in prim_path[-prim_path.rfind("/")]:  # asset is the subcomponent
                        return prim.parent()
                    else:
                        vsets = prim.GetVariantSets().GetNames()
                        for vset in WAREHOUSE_COLUMN_VARIANTS:
                            if vset in vsets:
                                return prim
        return None
