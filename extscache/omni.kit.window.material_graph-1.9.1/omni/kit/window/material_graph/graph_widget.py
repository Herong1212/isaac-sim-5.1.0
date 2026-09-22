# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["GraphWidget"]

import asyncio
import json
import traceback
import webbrowser
from functools import partial
from pathlib import Path
from typing import List, Optional, Tuple

import carb
import omni.client
import omni.kit.app
import omni.kit.commands
import omni.ui as ui
import omni.usd
from omni.kit.graph.delegate.default.backdrop_delegate import BackdropDelegate
from omni.kit.graph.editor.core import GraphEditorCoreWidget
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.widget.graph import GraphModel
from omni.kit.widget.material_preview import MaterialPreviewProducer
from omni.kit.window.filepicker import FilePickerDialog
from omni.ui import color as cl
from pxr import Sdf, Tf, UsdShade

from .compound_node_delegate import CompoundInputOutputNodeDelegate, CompoundNodeDelegate
from .graph_extension import COMPOUND_PATH_SETTING
from .graph_view import MaterialGraphView
from .graphnode_delegate import GraphNodeDelegate
from .mdl_node_tree_delegate import MdlNodeTreeDelegate
from .mdl_node_tree_model import MdlNodeItem, MdlNodeTreeModel
from .usdshade_graph_model import UsdShadeGraphModel

CURRENT_PATH = Path(__file__).parent
EXT_PATH = CURRENT_PATH.parent.parent.parent.parent
ICON_PATH = EXT_PATH.joinpath("icons")
TOOLBAR_ICON_PATH = ICON_PATH.joinpath("toolbar")

BACKGROUND = cl("#1F2123")
ICON_BACKGROUND = cl("#2A3034")
NODE_BACKGROUND = cl("#3C404B")
BORDER_SELECTED = cl("#FFFFFF")
NODE_BACKGROUND_SELECTED = cl("#666C7F")

BORDER_MATERIAL = cl("#9C7EB9")
BORDER_TEXTURE = cl("#5C66C2")
BORDER_MATH = cl("#4A8A53")
BORDER_CONSTANT = cl("#927049")
BORDER_CONSTRUCTOR = cl("#737055")
BORDER_CUSTOM = cl("#5F7B83")
BORDER_MISCELLANEOUS = cl("#207C98")
BORDER_NODEGRAPH = 0xFFE2DEB3
BORDER_SHADER = 0xFFB77072


def omni_client_exists(path):
    try:
        result, entry = omni.client.stat(path)
        return result == omni.client.Result.OK
    except Exception as e:
        traceback.print_exc()
        carb.log_error(str(e))
        return False


class GraphWidget(GraphEditorCoreWidget):
    # TODO: Separate file
    def __init__(self, **kwargs):
        self._graph_model = None
        self._graph_delegate = GraphNodeDelegate()
        self._mdl_node_model = MdlNodeTreeModel()
        self._mdl_node_model_delegate = MdlNodeTreeDelegate()
        self._mdl_node_model.reload()

        self.__material_preview_producer: Optional[MaterialPreviewProducer] = None
        self.__material_preview_subscription = None

        # The standard set to watch the Kit selection
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()

        self.__has_file_in_drop = False
        self._pick_folder_dialog = None
        self._selected_folder = None

        # Live swatch
        self.__material_preview_producer: Optional[MaterialPreviewProducer] = None
        self.__material_preview_subscription = None

        # Subscribe to external drag/drop events
        # TODO: Use omni.kit.window.drop_support when it's in release
        app_window = omni.appwindow.get_default_app_window()
        self.__external_drop_sub = app_window.get_window_drop_event_stream().create_subscription_to_pop(
            self._on_drag_drop_external, name="Material Graph"
        )

        self._event = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop(self._on_stage_event, name="Material Graph stage update")
        )

        self._graph_delegate.add_route(BackdropDelegate(), type="Backdrop")
        self._graph_delegate.add_route(CompoundNodeDelegate(), expression=lambda m, n: m.is_compound(n))
        self._graph_delegate.add_route(CompoundInputOutputNodeDelegate(), type="InputNode")
        self._graph_delegate.add_route(CompoundInputOutputNodeDelegate(), type="OutputNode")

        self._context_menu = ui.Menu("Toolbar Context")
        self.__right_click_context_menu = ui.Menu("Context menu")

        app = omni.kit.app.acquire_app_interface()
        self.__add_pause_button = float(app.get_kit_version_short()) >= 105

        super().__init__(
            delegate=self._graph_delegate,
            style=self.get_specialized_style(),
            catalog_model=self._mdl_node_model,
            catalog_delegate=self._mdl_node_model_delegate,
            toolbar_items=self.get_toolbar_items(),
            view_type=MaterialGraphView,
            **kwargs,
        )

        self._nodegraph_menu = None

    def destroy(self):
        self._context_menu = None
        self.__right_click_context_menu = None

        if self._pick_folder_dialog:
            self._pick_folder_dialog.destroy()
        self._pick_folder_dialog = None

        self.__external_drop_sub = None

        self.__material_preview_subscription = None
        if self.__material_preview_producer is not None:
            self.__material_preview_producer.destroy()
        self.__material_preview_producer = None

        self.__context_menu = None

        self._selection = None
        self._usd_context = None

        self.__material_preview_subscription = None
        if self.__material_preview_producer is not None:
            self.__material_preview_producer.destroy()
        self.__material_preview_producer = None

        self._mdl_node_model.destroy()
        self._mdl_node_model = None

        self._graph_delegate.destroy()
        self._graph_delegate = None

        if self._graph_model:
            self._graph_model.destroy()
        self._graph_model = None

        super().destroy()

    def on_build_startup(self):
        with ui.ZStack():
            # Background
            ui.Rectangle(style_type_name_override="Graph")
            # Two buttons
            with ui.VStack(content_clipping=True):
                ui.Spacer()
                with ui.HStack(height=0):
                    ICON_SIZE = 120
                    ui.Spacer()
                    ui.Button(
                        "Open Material From\n\t\t\tSelection",
                        name="Import",
                        width=0,
                        image_width=ICON_SIZE,
                        image_height=ICON_SIZE,
                        spacing=5,
                        clicked_fn=self.import_material_prim_from_selection,
                    )
                    # 20 because the button's padding is 10
                    ui.Label("OR", name="OR", width=0, height=ICON_SIZE + 20)
                    ui.Button(
                        "Create New Material\n\t",
                        name="New",
                        width=0,
                        image_width=ICON_SIZE,
                        image_height=ICON_SIZE,
                        spacing=5,
                        clicked_fn=self._create_new,
                    )
                    ui.Spacer()
                ui.Spacer()

    def get_specialized_style(self):
        # It's optional. It's here in case we have colors different from colors
        # of omni.kit.graph.editor.core.
        style = self._graph_delegate.get_style(
            border=BORDER_MISCELLANEOUS,
            background=BACKGROUND,
            node_background=NODE_BACKGROUND,
            icon_background=ICON_BACKGROUND,
            border_selected=BORDER_SELECTED,
            node_background_selected=NODE_BACKGROUND_SELECTED,
        )

        # Node types
        style.update(
            self._graph_delegate.specialized_color_style(
                "Material", BORDER_MATERIAL, f"{ICON_PATH}/mdl-thumbnails/Materials_category_dark.png", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style("Shader", BORDER_SHADER, f"{ICON_PATH}/Shader.svg", 0xFFFFFFFF)
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "NodeGraph",
                BORDER_MISCELLANEOUS,
                f"{ICON_PATH}/mdl-thumbnails/Custom_user_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "InputNode", BORDER_MISCELLANEOUS, f"{ICON_PATH}/mdl-thumbnails/Materials_category_dark.png", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "OutputNode",
                BORDER_MISCELLANEOUS,
                f"{ICON_PATH}/mdl-thumbnails/Materials_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Materials", BORDER_MATERIAL, f"{ICON_PATH}/mdl-thumbnails/Materials_category_dark.png", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Materials, modifiers",
                BORDER_MATERIAL,
                f"{ICON_PATH}/mdl-thumbnails/Materials_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Texturing, high level",
                BORDER_TEXTURE,
                f"{ICON_PATH}/mdl-thumbnails/Texture_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Texturing, basic", BORDER_TEXTURE, f"{ICON_PATH}/mdl-thumbnails/Texture_category_dark.png", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Math functions", BORDER_MATH, f"{ICON_PATH}/mdl-thumbnails/Math_category_dark.png", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Constants, State and Primvars",
                BORDER_CONSTANT,
                f"{ICON_PATH}/mdl-thumbnails/State_Data_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Material Graphs",
                BORDER_CUSTOM,
                f"{ICON_PATH}/mdl-thumbnails/Custom_user_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Constructors, conversions and swizzles",
                BORDER_CONSTRUCTOR,
                f"{ICON_PATH}/mdl-thumbnails/Conversions_category_dark.png",
                0xFFFFFFFF,
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Advanced", BORDER_TEXTURE, f"{ICON_PATH}/mdl-thumbnails/Texture_category_dark.png", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Miscellaneous", BORDER_MISCELLANEOUS, f"{ICON_PATH}/Custom_user_category_dark.svg", 0xFFFFFFFF
            )
        )
        style.update(
            self._graph_delegate.specialized_color_style(
                "Backdrop", BORDER_MISCELLANEOUS, f"{ICON_PATH}/Custom_user_category_dark.svg", 0xFFFFFFFF
            )
        )

        # Plug types
        style.update(self._graph_delegate.specialized_port_style("asset", 0xFFB874C0))
        style.update(self._graph_delegate.specialized_port_style("bool", 0xFFA37FFC))
        style.update(self._graph_delegate.specialized_port_style("color", cl("#FF9C83")))
        style.update(self._graph_delegate.specialized_port_style("color3f", 0xFF839CFF))
        style.update(self._graph_delegate.specialized_port_style("float", 0xFF69C8FF))
        style.update(self._graph_delegate.specialized_port_style("float2", 0xFF71F8F9))
        style.update(self._graph_delegate.specialized_port_style("float3", 0xFF71D899))
        style.update(self._graph_delegate.specialized_port_style("int", 0xFF658C00))
        style.update(self._graph_delegate.specialized_port_style("material", cl("#80C280")))
        style.update(self._graph_delegate.specialized_port_style("texture_2d", cl("#C074B8")))
        style.update(self._graph_delegate.specialized_port_style("texture_return", cl("#464BF9")))
        style.update(self._graph_delegate.specialized_port_style("::base::texture_return", cl("#464BF9")))

        # Import/New Buttons
        style.update(
            {
                "Label::OR": {"margin": 25},
                "Button::New": {"stack_direction": ui.Direction.TOP_TO_BOTTOM, "background_color": cl(0, 0, 0, 0)},
                "Button::Import": {"stack_direction": ui.Direction.TOP_TO_BOTTOM, "background_color": cl(0, 0, 0, 0)},
                "Button.Image::New": {"image_url": f"{ICON_PATH}/CreateNewMaterial.png"},
                "Button.Image::Import": {"image_url": f"{ICON_PATH}/ImportMaterialFromSelection.png"},
            }
        )

        # ToolBar
        style.update(
            {
                "ToolBar": {"margin_height": 0},
                "ToolBar.Button.Pause": {"padding": 4, "background_color": 0xFF252525},
            }
        )

        return style

    def on_toolbar_create_graph_clicked(self):
        self._create_new()

    def on_toolbar_edit_graph_clicked(self):
        self.import_material_prim_from_selection()

    def get_material_prim(self, prim_path: Sdf.Path):
        if not prim_path:
            return None

        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return None

        if prim.IsA(UsdShade.Material):
            return prim

        if prim.IsA(UsdShade.NodeGraph) or prim.IsA(UsdShade.Shader):
            return get_material_prim(stage, prim_path.GetParentPath())

        api = UsdShade.MaterialBindingAPI(prim)
        if api:
            mat = api.ComputeBoundMaterial()
            if mat and mat[0]:
                return mat[0].GetPrim()

        return None

    def import_material_prim_from_selection(self):
        # Edit what is currently selected, or prompt for selection
        selection = self._selection.get_selected_prim_paths()
        if selection:
            stage = self._usd_context.get_stage()
            prim = self.get_material_prim(Sdf.Path(selection[0]))
            if prim:
                asyncio.ensure_future(self._import_prims(None, [prim]))

    def on_toolbar_expansion_state_clicked(self, state):
        if not self.model or not self.model.nodes:
            return

        with omni.kit.undo.group():
            for node in self.model.nodes:
                self.model[node].expansion_state = state

    def on_toolbar_edit_clicked(self):
        from omni.kit.window.preferences import PreferenceBuilder, get_page_list, select_page, show_preferences_window

        def show_material_preference():
            pages = get_page_list()
            omni_page = [page for page in pages if page.get_title() == "Material"]
            if len(omni_page) == 1:

                async def show_window_and_focus():
                    select_page(omni_page[0])
                    show_preferences_window()
                    preferenceWindow = ui.Workspace.get_window(PreferenceBuilder.WINDOW_NAME)
                    if preferenceWindow:
                        preferenceWindow.focus()

                self.__show_prefs_task = asyncio.ensure_future(show_window_and_focus())

        self._context_menu.clear()
        with self._context_menu:
            ui.MenuItem("Preferences...", triggered_fn=show_material_preference)
        self._context_menu.show()

    def on_toolbar_view_clicked(self):
        self._context_menu.clear()
        with self._context_menu:
            ui.MenuItem("Layout Nodes", triggered_fn=self.on_layout_clicked, enabled=True if self.model else False)
            ui.Separator()
            ui.MenuItem(
                "Frame Selected" if self.model and self.model.selection else "Frame All",
                triggered_fn=self.on_frame_selected_clicked,
                enabled=True if self.model else False,
            )  # hotkey_text="F")

        self._context_menu.show()

    def on_frame_selected_clicked(self):
        self._graph_view.focus_on_nodes(self.model.selection)

    def on_layout_clicked(self):
        with omni.kit.undo.group():
            self._graph_view.layout_all()

    def on_toolbar_help_clicked(self):
        OMNIGRAPH_TUTORIAL_URL = (
            "https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_material/ext_material-graph.html"
        )
        webbrowser.open(OMNIGRAPH_TUTORIAL_URL)

    def get_toolbar_items(self, add_pause_button=False):
        toolbar_items = [
            {
                "name": "CreateMaterial",
                "icon": f"{TOOLBAR_ICON_PATH}/create_graph_dark.svg",
                "on_clicked": self.on_toolbar_create_graph_clicked,
                "tooltip": "Create a new material",
            },
            {
                "name": "EditSelectedMaterial",
                "icon": f"{TOOLBAR_ICON_PATH}/edit_graph_dark.svg",
                "on_clicked": self.on_toolbar_edit_graph_clicked,
                "tooltip": "Edit the selected material",
            },
            {"name": "-"},
            {
                "name": "Expansion_Open",
                "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_state_0_toggle_dark.svg",
                "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.OPEN),
                "tooltip": "Expand all nodes",
            },
            {
                "name": "Expansion_Minimized",
                "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_state_1_toggle_dark.svg",
                "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.MINIMIZED),
                "tooltip": "Minimize all nodes",
            },
            {
                "name": "Expansion_Closed",
                "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_state_2_toggle_dark.svg",
                "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.CLOSED),
                "tooltip": "Close all nodes",
            },
            {"name": "-"},
            {"name": "Edit", "label": "Edit", "on_clicked": self.on_toolbar_edit_clicked},
            {"name": "View", "label": "View", "on_clicked": self.on_toolbar_view_clicked},
            {"name": " "},
        ]

        if self.__add_pause_button and add_pause_button:
            if self.model.pause:
                toolbar_items.append(
                    {
                        "name": "Recompile",
                        "enabled": True,
                        "tooltip": "Refresh material, allowing it to compile and then immediately pausing.\n(CTRL+R)",
                        "on_clicked": self.unpause_and_pause,
                        "icon": f"{TOOLBAR_ICON_PATH}/reload_dark.svg",
                    }
                )

            icon = f"{TOOLBAR_ICON_PATH}/pause_dark_a.svg"
            tooltip_prefix = "Pause"
            style_type_name_override = "ToolBar.Button"

            if self.model.pause:
                icon = f"{TOOLBAR_ICON_PATH}/pause_red_dark_a.svg"
                tooltip_prefix = "Resume"
                style_type_name_override = "ToolBar.Button.Pause"

            toolbar_items.append(
                {
                    "name": "Pause",
                    "enabled": True,
                    "tooltip": f"{tooltip_prefix} material compilation.",
                    "on_clicked": self.toggle_material_compilation,
                    "icon": icon,
                    "style_type_name_override": style_type_name_override,
                }
            )

        toolbar_items.append(
            {
                "name": "Help",
                "enabled": True,
                "tooltip": "MaterialGraph documentation",
                "on_clicked": self.on_toolbar_help_clicked,
                "icon": f"{TOOLBAR_ICON_PATH}/help_dark.svg",
            }
        )

        return toolbar_items

    def on_accept_drop(self, drop_data: str):
        """Called to check if drop_data has the acceptable shading node description"""
        if isinstance(drop_data, str):
            # Check if it's a file
            self.__has_file_in_drop = not drop_data.startswith("{") and omni_client_exists(drop_data)
            if self.__has_file_in_drop:
                # List of available formats: carb/source/plugins/carb.imaging/Imaging.cpp
                for ext in ["bmp", "dds", "exr", "gif", "hdr", "jpeg", "jpg", "png", "psd", "svg", "tga"]:
                    if drop_data.endswith(f".{ext}"):
                        return True
                return False

            try:
                data = json.loads(drop_data)
            except ValueError:
                # It's not a json
                return False

            prim_type = data.get("prim_type", None)

            if self._graph_view.model:
                return prim_type in ["Shader", "Backdrop", "NodeGraph", "CompoundComponent", "ImportCompound"]
            else:
                # Check if we need to create a new material
                return prim_type == "CompoundComponent"

    def on_drop(self, event: ui.WidgetMouseDropEvent):
        """Called to create a node that was droppped to the window"""
        if event.x is None and event.y is None:
            # It happens when calling add_node directly, not by omni.ui
            self.__has_file_in_drop = False
            # Middle of the canvas
            event.x = self._graph_view.screen_position_x + self._graph_view.computed_width / 2
            event.y = self._graph_view.screen_position_y + self._graph_view.computed_height / 2

        if self.__has_file_in_drop:
            return self._add_image(event)

        # {
        # 'prim_type': 'Shader',
        # 'sub_identifier': 'NodeGraph',
        # 'source_asset': 'c:\\dev\\...\\texture.usda',
        # 'inputs': [],
        # 'outputs': [{'name': 'out', 'type': 'token'}]
        # }
        data = json.loads(event.mime_data)
        prim_type = data["prim_type"]

        if not self._graph_view or not self._graph_view.model:
            # Check if we need to create a new material
            if prim_type == "CompoundComponent":
                self._create_new()
            else:
                return

        sub_identifier = data["sub_identifier"]
        position = self._graph_view.screen_to_canvas(event.x, event.y)

        if prim_type == "CompoundComponent":
            # Special case: input or output node for the compound
            # TODO: It will be changed once we are able to group them
            self._isolation_model.add_input_or_output(position, sub_identifier == "InputNode")
            return

        source_asset = data["source_asset"]

        parent = self.get_current_graph_item()

        # Don't use self._graph_model to place the node to the correct root
        self._graph_view.model.create_node(parent, prim_type, sub_identifier, source_asset, position)

    def on_right_mouse_button_pressed(self, items):
        # Create a context menu
        self.__context_menu = ui.Menu("Context menu")
        with self.__context_menu:
            ui.MenuItem("Open All", triggered_fn=lambda: self._graph_view.set_expansion(GraphModel.ExpansionState.OPEN))
            ui.MenuItem(
                "Minimize All", triggered_fn=lambda: self._graph_view.set_expansion(GraphModel.ExpansionState.MINIMIZED)
            )
            ui.MenuItem(
                "Close All", triggered_fn=lambda: self._graph_view.set_expansion(GraphModel.ExpansionState.CLOSED)
            )
            ui.MenuItem("Layout All", triggered_fn=lambda: self._graph_view.layout_all())
            ui.MenuItem("Import From Selection", triggered_fn=self.import_material_prim_from_selection)
            with ui.Menu("Filter Selection"):
                ui.MenuItem(
                    "Filter Upstream", triggered_fn=lambda: self._graph_view.filter_upstream(self._graph_view.selection)
                )

            ui.MenuItem("Clear All", triggered_fn=lambda: self.clear_all())
            ui.Separator()
            self.__nodegraph_menu = ui.MenuItem("Export Nodegraph", triggered_fn=lambda: self.__export_node())
            ui.MenuItem("Export Material", triggered_fn=lambda: self.__export_material())

        self.__context_menu.show()
        if self.__nodegraph_menu:
            self.__nodegraph_menu.visible = self.__can_export_node()

    def on_left_mouse_button_double_clicked(self, items):
        if not items:
            return

        # Open compound
        self.set_current_compound(items[0])

    def on_catalog_context_menu(self, items: List[ui.AbstractItem]):
        self.__context_menu = ui.Menu("Left Pannel Context Menu")

        with self.__context_menu:
            ui.MenuItem("Refresh Compounds", triggered_fn=self._refresh_compounds)
            ui.MenuItem("Add Compounds Directory", triggered_fn=self._pick_folder)
            ui.MenuItem("Clear Compounds Directories", triggered_fn=self._clear_compounds_dirs)
            ui.MenuItem("Reload", triggered_fn=self._reload)

        self.__context_menu.show()

    def _add_image(self, event: ui.WidgetMouseDropEvent):
        """
        Called to create a texture node with the image that was droppped
        to the window.
        """
        if not self._graph_view or not self._graph_view.model:
            return

        parent = self.get_current_graph_item()
        position = self._graph_view.screen_to_canvas(event.x, event.y)
        self._graph_view.model.create_node(
            parent,
            "ImportCompound",
            "file_texture",
            f"{EXT_PATH}/data/shaders/texture_return.usda",
            position=position,
            attributes_to_set={Sdf.Path(".inputs:texture"): event.mime_data},
        )

    def _on_drag_drop_external(self, e: carb.events.IEvent):
        """Called when external drop to Kit"""

        # need to wait until next frame as otherwise mouse coords can be wrong
        async def do_drag_drop():
            await omni.kit.app.get_app().next_update_async()

            mouse_position = self._get_graph_view_hovered_position()
            if not mouse_position:
                return

            paths = e.payload["paths"]
            if not paths:
                return

            class ExternalDropEvent:
                def __init__(self, mime_data, mouse_position):
                    self.mime_data = mime_data
                    self.x = mouse_position[0]
                    self.y = mouse_position[1]

            self.__has_file_in_drop = True
            self.on_drop(ExternalDropEvent(paths[0], mouse_position))

        asyncio.ensure_future(do_drag_drop())

    def _get_graph_view_hovered_position(self) -> Optional[Tuple[float]]:
        """Return the position of mouse if self._graph_view is hovered"""
        # TODO: Check if the window is visible
        if not self._graph_view or not self._graph_view.visible:
            return

        zoom = self._graph_view.zoom

        app_window = omni.appwindow.get_default_app_window()
        input = carb.input.acquire_input_interface()
        dpi_scale = ui.Workspace.get_dpi_scale()
        pos_x, pos_y = input.get_mouse_coords_pixel(app_window.get_mouse())
        pos_x = pos_x / dpi_scale / zoom
        pos_y = pos_y / dpi_scale / zoom

        screen_x = self._graph_view.screen_position_x
        screen_y = self._graph_view.screen_position_y
        screen_w = self._graph_view.computed_width
        screen_h = self._graph_view.computed_height

        if pos_x > screen_x and pos_y > screen_y and pos_x < screen_x + screen_w and pos_y < screen_y + screen_h:
            return pos_x, pos_y

    def clear_all(self):
        super().clear_all()
        self.set_toolbar_items(self.get_toolbar_items())

    def toggle_material_compilation(self):
        if not self.model:
            return

        self.model.pause = not self.model.pause
        self.set_toolbar_items(self.get_toolbar_items(True))

    def unpause_and_pause(self):
        async def toggle_pause():
            self.model.pause = not self.model.pause
            for _ in range(100):
                await omni.kit.app.get_app().next_update_async()

            self.model.pause = not self.model.pause

        if not self.model or not self.model.pause:
            return

        asyncio.ensure_future(toggle_pause())

    async def _import_prims(self, _, prims, focus=True):
        """Create a model and set it to the graph view"""
        prims = list(prims)
        if self._graph_model:
            self._graph_model.destroy()
            self._graph_model = None

        if not prims:
            return

        material_prim = self.get_material_prim(prims[0].GetPath())
        if not material_prim:
            return

        self._graph_model = UsdShadeGraphModel([material_prim])

        if self.__material_preview_producer is None:
            self.__material_preview_producer = MaterialPreviewProducer()
            self.__material_preview_subscription = self.__material_preview_producer.set_on_drawable_changed_fn(
                self.__on_material_preview_drawable_changed
            )

        if hasattr(self._graph_model, "set_material_preview_producer"):
            self._graph_model.set_material_preview_producer(self.__material_preview_producer)

        self.model = self._graph_model

        # If we don't wait here then when the graph is loaded a
        # second time by self.set_current_compound the initial zoom state
        # of the graph will be inconsistent.
        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        self.set_current_compound(material_prim, focus)
        self.set_toolbar_items(self.get_toolbar_items(True))

    def _import_selection(self):
        """Import selected prims"""
        selection = self._selection.get_selected_prim_paths()
        if not selection:
            self.model = None
            return

        stage = self._usd_context.get_stage()
        prims = [stage.GetPrimAtPath(s) for s in selection]
        if not prims:
            self.model = None
            return

        asyncio.ensure_future(self._import_prims(None, [prim for prim in prims if prim]))

    def _create_new(self):
        """Create new material"""
        stage = self._usd_context.get_stage()

        # Get /Looks path
        if stage.HasDefaultPrim():
            looks_path = stage.GetDefaultPrim().GetPath()
        else:
            looks_path = Sdf.Path.absoluteRootPath
        looks_path = looks_path.AppendChild("Looks")

        # Create a new material
        omni.kit.commands.execute(
            "NewUsdShadeMaterialCommand", parent_path=looks_path, identifier="Material", select_new_prim=True
        )

        # Import it to the GraphView
        self._import_selection()

    def _refresh_compounds(self):
        """Refresh left panel"""
        from .graph_extension import GraphExtension

        # Refresh registered compounds
        GraphExtension.refresh_compounds()

        # Refresh compounds in the model
        self._mdl_node_model.refresh()

    def _clear_compounds_dirs(self):
        settings = carb.settings.get_settings()
        settings.set(COMPOUND_PATH_SETTING, [])
        self._refresh_compounds()

    def _reload(self):
        self._mdl_node_model.reload()

    def _pick_folder(self):
        """Open Pick Folder dialog to add compounds"""
        if self._pick_folder_dialog:
            self._pick_folder_dialog.destroy()

        self._pick_folder_dialog = FilePickerDialog(
            "Pick Compounds Folder",
            apply_button_label="Use This Folder",
            selection_changed_fn=self.__on_selection_changed,
            click_apply_handler=self.__on_apply_folder,
            item_filter_options=["All Folders (*)"],
            item_filter_fn=self.__on_filter_folder,
        )

    def __on_material_preview_drawable_changed(self):
        """Called by MaterialPreviewProducer when the resolution is changed"""

        # TODO: Express this as a proper API to funnel the render to anything that needs it
        # omni.kit.graph.delegate.default\omni\kit\graph\delegate\default\delegate_full.py@304
        #  self._viewport_provider = ui.ImageProvider()
        #
        image_provider = getattr(self._graph_delegate, "_viewport_provider", None)
        if image_provider:
            gpu_reference = self.__material_preview_producer.gpu_reference
            if gpu_reference:
                image_provider.set_data(gpu_reference)

        if self._graph_model:
            self._graph_model._item_changed(None)

    @staticmethod
    def __on_filter_folder(item: FileBrowserItem) -> bool:
        """Used by pick folder dialog to hide all the files"""
        return item.is_folder

    def __on_selection_changed(self, items):
        if items:
            self._selected_folder = items[0].path

    def __on_apply_folder(self, filename: str, dir: str):
        """Called when the user press "Use This Folder" in the pick folder dialog"""
        # not use `filename` due to a bug in FilePickerDialog that the `filename`
        # does not get updated when user selects a folder
        path = omni.client.combine_urls(dir, self._selected_folder)
        self._pick_folder_dialog.hide()

        # Save the folder to the settings
        settings = carb.settings.get_settings()
        compound_custom_paths: List[str] = settings.get(COMPOUND_PATH_SETTING) or []
        compound_custom_paths.append(path)
        compound_custom_paths = list(set(compound_custom_paths))
        settings.set_string_array(COMPOUND_PATH_SETTING, compound_custom_paths)

        # Refresh left panel
        self._refresh_compounds()

    def __can_export_node(self):
        from pxr import UsdShade

        if self._isolation_model:
            selection = self._isolation_model.selection
            if len(selection) != 1:
                return False
            prim = selection[0]
            return prim.IsA(UsdShade.NodeGraph) and not prim.IsA(UsdShade.Material)
        return False

    def __export_node(self):
        from omni.kit.widget.stage.export_utils import ExportPrimUSD

        if self._isolation_model:
            selection = self._isolation_model.selection
            if len(selection) != 1:
                return False
            prim = selection[0]
            ExportPrimUSD(
                select_msg=f'Export NodeGraph "{prim.GetName()}" As...', save_msg="Export", postfix_name="NodeGraph"
            ).export([prim])

    def __export_material(self):
        from omni.kit.widget.stage.export_utils import ExportPrimUSD

        if self._isolation_model:
            prim = self._isolation_model._root
            ExportPrimUSD(
                select_msg=f'Export Material "{prim.GetName()}" As...', save_msg="Export", postfix_name="Material"
            ).export([prim])

    def _on_stage_event(self, event):
        """When a new stage is opened, reset the model"""
        if event.type == int(omni.usd.StageEventType.OPENING):
            self.model = None
