__all__ = ['DropMaterialMenuDelegate', 'DropMaterialMenu', 'DropMaterialMenuItem']

from pathlib import Path

import carb
import omni.ui as ui
from omni.ui import color as cl
import omni.usd
from pxr import Tf, Sdf, Usd, UsdShade, UsdGeom
from . import material_utils


SELECTION_GROUP_ID = 255
CUSTOM_OUTLINE_COLOR = (0.2, 0.78, 1.0, 1.0)
SETTINGS_OUTLINE_COLOR = "/persistent/app/viewport/outline/color"


def _get_ui_style():
    """Workaround for document build."""

    EXT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.material.library}"))
    ICON_PATH = EXT_PATH.joinpath("data").joinpath("icons").absolute()

    UI_STYLE = {
        "Menu.Item.Icon::Prim": {"image_url": "${glyphs}/menu_prim.svg"},
        "Menu.Item.Icon::Xform": {"image_url": "${glyphs}/menu_xform.svg"},
        "Menu.Item.Icon::GeomSubset": {"image_url": f"{ICON_PATH}/GeomSubset.svg"},
        "Menu.Item.Label.Kind": {"color": 0xff6f6f6f},
        "Menu.Item.Triangle": {"background_color": cl.viewport_menubar_light}
    }

    return UI_STYLE


class DropMaterialMenuDelegate(ui.MenuDelegate):
    def __init__(
        self,
        icon_type="Prim",
        with_triangle=False
    ):
        super().__init__(propagate=False)
        self._icon_type = icon_type
        self._with_triangle = with_triangle

    def build_item(self, item):
        with ui.HStack(style={"margin": 3}):
            self.icon = ui.ImageWithProvider(
                style_type_name_override="Menu.Item.Icon",
                width=20,
                height=20
            )
            self.icon.name = self._icon_type

            ui.Label(item.text)

            if hasattr(item, "kind_text") and item.kind_text:
                label_text = f"(Kind: {item.kind_text})"
                ui.Label(label_text, style_type_name_override="Menu.Item.Label.Kind")

            if self._with_triangle:
                ui.Spacer(width=10)
                with ui.VStack(style={"margin": 0}):
                    ui.Spacer()
                    ui.Triangle(
                        width=4,
                        height=8,
                        alignment=ui.Alignment.RIGHT_CENTER,
                        style_type_name_override="Menu.Item.Triangle"
                    )
                    ui.Spacer()
                ui.Spacer(width=3)


class DropMaterialMenu(ui.Menu):
    def __init__(self, prim_path, icon_type):
        self._delegate = DropMaterialMenuDelegate(icon_type=icon_type, with_triangle=True)

        super().__init__(
            prim_path,
            delegate=self._delegate,
            style=_get_ui_style(),
            menu_compatibility=False
        )


class DropMaterialMenuItem(ui.MenuItem):
    def __init__(self, prim_path, icon_type, kind_text="", triggered_fn=None):
        self._usd_context = omni.usd.get_context()

        self._prim_path = prim_path 
        self._kind_text = kind_text
        self._children = material_utils.get_prim_children_paths(prim_path)
        self._delegate = DropMaterialMenuDelegate(icon_type=icon_type)
        self._original_outline_color = self._get_original_outline_color()

        super().__init__(
            prim_path,
            delegate=self._delegate,
            style=_get_ui_style(),
            style_type_name_override="Menu.Item",
            menu_compatibility=False,
            triggered_fn=triggered_fn,
            mouse_hovered_fn=self._on_mouse_hovered,
            mouse_pressed_fn=self._on_mouse_pressed
        )

    @property
    def kind_text(self):
        return self._kind_text
    
    @kind_text.setter
    def kind_text(self, text):
        self._kind_text = text

    def _on_mouse_hovered(self, hovered):
        if hovered:
            self._set_selection_group_and_outline()
        else:
            self._set_selection_group_and_outline(restore=True)

    def _on_mouse_pressed(self, x, y, button, modifier):
        self._set_selection_group_and_outline(restore=True)

    def _get_original_outline_color(self):
        base_index = SELECTION_GROUP_ID * 4
        outline_colors = carb.settings.get_settings().get(SETTINGS_OUTLINE_COLOR)
        outline_color = (
            outline_colors[base_index],
            outline_colors[base_index + 1],
            outline_colors[base_index + 2],
            outline_colors[base_index + 3]
        )
        return outline_color

    def _set_selection_group_and_outline(self, restore=False):
        color = self._original_outline_color if restore else CUSTOM_OUTLINE_COLOR
        self._usd_context.set_selection_group_outline_color(SELECTION_GROUP_ID, color)

        gid = 0 if restore else SELECTION_GROUP_ID  # 0 for unset
        self._usd_context.set_selection_group(gid, self._prim_path)
        for child in self._children:
            self._usd_context.set_selection_group(gid, child)


def _get_subsets(prim_path: str):
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    mesh = UsdGeom.Mesh(prim)

    if mesh:
        return UsdGeom.Subset.GetGeomSubsets(mesh)
    else:
        return []


def _drop_material(prim_path: str, model_path: str, apply_material_fn: callable):
    if not prim_path and not model_path:
        apply_material_fn(Sdf.Path(""))
        return
    
    # "Type" select mode or no Kind found
    if not model_path:
        apply_material_fn(prim_path)
        return

    # "Kind" select mode
    stage = omni.usd.get_context().get_stage()
    model_prim = stage.GetPrimAtPath(model_path)
    kind = Usd.ModelAPI(model_prim).GetKind()
    subsets = _get_subsets(prim_path)

    menu = ui.Menu(menu_compatibility=False)
    with menu:
        if subsets:
            with DropMaterialMenu(
                prim_path,
                icon_type="Prim"
            ):
                for subset in subsets:
                    subset_path = subset.GetPath().pathString
                    DropMaterialMenuItem(
                        subset_path,
                        icon_type="GeomSubset",
                        triggered_fn=lambda w=menu, p=subset_path: apply_material_fn(p)
                    )
        else:
            DropMaterialMenuItem(
                prim_path,
                icon_type="Prim",
                triggered_fn=lambda w=menu, p=prim_path: apply_material_fn(p)
            )

        ui.Separator(style={"padding": 2})  # need tiny gap between items for hover events

        DropMaterialMenuItem(
            model_path,
            icon_type="Xform",
            kind_text=kind,
            triggered_fn=lambda w=menu, p=model_path: apply_material_fn(p)
        )

    menu.show()
