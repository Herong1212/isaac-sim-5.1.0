import carb
import omni.ui as ui
import omni.usd
from functools import partial
from pxr import Tf, Gf, UsdSkel, UsdGeom
import AnimGraphSchema
from .animation_graph_window import AnimationGraphWindow
from .create_animation_graph_dialog import CreateAnimationGraphDialog
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.window.popup_dialog import MessageDialog
from typing import List
import os
from .stage_picker_dialog import StagePickerDialog

MENU_NAME = "Animation"
MENU_GLYPH = "menu_animation.svg"
ANIMATION_GRAPH_GLYPH = "animation_graph.svg"
MENU_CREATE_ANIMATIONGRAPH = "Animation Graph"
MENU_OPEN_ANIMATIONGRAPH = "Open Animation Graph"


class AnimGraphMenu:
    def __init__(self, ext_id, graph_window: AnimationGraphWindow, create_graph_dialog: CreateAnimationGraphDialog):
        self._ext_id = ext_id
        self._graph_window = graph_window
        self._create_graph_dialog = create_graph_dialog
        self._main_menu_items = []
        self._context_menus = []
        self._context_menu = None
        self.on_startup()

    def prim_is_type(self, objects: dict, type: Tf.Type):
        prim_list = objects["prim_list"]
        for prim in prim_list:
            if not prim.IsA(type):
                return False
        return len(prim_list) > 0

    def _build_context_menu(self, objects):
        from omni.kit.context_menu import ContextMenuExtension
        # keep copy objects to prevent python GC
        objects["a_menu"] = ContextMenuExtension.uiMenu(
            MENU_NAME, glyph=MENU_GLYPH, submenu=True, tearable=True,
            style={"secondary_color": 0xFFFFFFFF})
        objects["a_menuitems"] = []
        with objects["a_menu"]:
            objects["a_menuitems"].append(
                ContextMenuExtension.uiMenuItem(
                    MENU_CREATE_ANIMATIONGRAPH,
                    triggered_fn=partial(self._on_menu_click, MENU_CREATE_ANIMATIONGRAPH, objects),
                    glyph=ANIMATION_GRAPH_GLYPH
                ))

    def _create_animation_graph(self):
        self._create_graph_dialog.open(self._graph_window.open_graph)

    def _open_animation_graph(self, objects):
        if objects is not None:
            if "prim_list" in objects:
                prim_list = objects["prim_list"]
                self._graph_window.open_graph(prim_list[0])

    def on_startup(self):
        self._register_actions()
        # setup the create main menus
        create_original_svg_color = carb.settings.get_settings().get("/exts/omni.kit.menu.create/original_svg_color")
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu is None:
            return

        main_sub_menu = []
        main_sub_menu.append(MenuItemDescription(
            f' {omni.kit.ui.get_custom_glyph_code("${glyphs}/animation_graph.svg")}   {MENU_CREATE_ANIMATIONGRAPH}',
            onclick_action=(self._ext_id, "create_animation_graph")
        ))

        self._main_menu_items = []
        self._main_menu_items.append(
            MenuItemDescription(
                name=MENU_NAME,
                glyph="menu_animation.svg",
                appear_after=["Xform", "Material"],
                sub_menu=main_sub_menu,
                original_svg_color=create_original_svg_color
            )
        )
        omni.kit.menu.utils.add_menu_items(self._main_menu_items, "Create", -9)

        # setup the context menus
        self._context_menus = []
        self._context_menu = omni.kit.context_menu.get_instance()
        context_menu_dict = {"name": "Animation Graph Context Menu", "populate_fn": self._build_context_menu}
        self._context_menus.append(omni.kit.context_menu.add_menu(context_menu_dict, "CREATE", "omni.kit.widget.stage"))

        context_menu_dict_list = [
            {
                "name": "",
                "show_fn": [
                    self._context_menu.is_prim_selected,
                    self._context_menu.is_one_prim_selected,
                    partial(self.prim_is_type, type=AnimGraphSchema.AnimationGraph),
                ],
            },
            {
                "name": MENU_OPEN_ANIMATIONGRAPH,
                "glyph": "folder_open.svg",
                "show_fn": [
                    self._context_menu.is_prim_selected,
                    self._context_menu.is_one_prim_selected,
                    partial(self.prim_is_type, type=AnimGraphSchema.AnimationGraph)
                ],
                "onclick_fn": self._open_animation_graph,
            }
        ]
        for context_menu_dict in context_menu_dict_list:
            self._context_menus.append(omni.kit.context_menu.add_menu(context_menu_dict, "MENU", "omni.kit.widget.stage"))

    def _on_menu_click(self, menu_item, objects: dict):
        if menu_item == MENU_CREATE_ANIMATIONGRAPH:
            self._create_animation_graph()
        elif menu_item == MENU_OPEN_ANIMATIONGRAPH:
            self._open_animation_graph(objects)

    def on_shutdown(self):
        omni.kit.menu.utils.remove_menu_items(self._main_menu_items, "Create")
        self._context_menu = None
        self._context_menus = None
        self._main_menu_items = None
        self._create_graph_dialog = None
        self._graph_window = None
        self._deregister_actions()

    def _register_actions(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "AnimGraph Actions"

        action_registry.register_action(
            self._ext_id,
            "create_animation_graph",
            self._create_animation_graph,
            display_name=f"Create->Animation->{MENU_CREATE_ANIMATIONGRAPH}",
            description=f"Create {MENU_CREATE_ANIMATIONGRAPH}",
            tag=actions_tag,
        )

    def _deregister_actions(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self._ext_id)
