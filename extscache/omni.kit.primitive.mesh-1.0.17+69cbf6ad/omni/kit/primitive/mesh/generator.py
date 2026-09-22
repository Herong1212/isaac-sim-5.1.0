import carb.settings
import omni
import omni.kit

from omni import ui
from .evaluators import _get_all_evaluators, get_geometry_mesh_prim_list
from omni.kit.menu.utils import MenuItemDescription, remove_menu_items, add_menu_items


class MeshGenerator:
    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._window = None
        self._mesh_setting_ui = {}
        self._current_setting_index = 0
        self._mesh_menu_list = []

    def destroy(self):
        self._window = None
        remove_menu_items(self._mesh_menu_list, "Create")

    def register_menu(self):
        sub_menu = []
        for prim in get_geometry_mesh_prim_list():
            sub_menu.append(MenuItemDescription(name=prim, onclick_action=("omni.kit.primitive.mesh", f"create_mesh_prim_{prim.lower()}")))

        sub_menu.append(MenuItemDescription())
        sub_menu.append(MenuItemDescription(name="Settings", onclick_action=("omni.kit.primitive.mesh", "show_setting_window")))

        self._mesh_menu_list = [
            MenuItemDescription(name="Mesh", glyph="menu_prim.svg", sub_menu=sub_menu)
        ]
        add_menu_items(self._mesh_menu_list, "Create")

    def on_primitive_type_selected(self, model, item):
        names = get_geometry_mesh_prim_list()
        old_mesh_name = names[self._current_setting_index]
        if old_mesh_name in self._mesh_setting_ui:
            self._mesh_setting_ui[old_mesh_name].visible = False

        idx = model.get_item_value_model().as_int
        mesh_name = names[idx]
        if mesh_name in self._mesh_setting_ui:
            self._mesh_setting_ui[old_mesh_name].visible = False
            self._mesh_setting_ui[mesh_name].visible = True

        self._current_setting_index = idx

    def show_setting_window(self):
        flags = ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR

        if not self._window:
            self._window = ui.Window(
                "Mesh Generation Settings",
                ui.DockPreference.DISABLED,
                width=400,
                height=260,
                flags=flags,
                padding_x=0,
                padding_y=0,
            )

            with self._window.frame:
                with ui.VStack(height=0):
                    ui.Spacer(width=0, height=20)
                    with ui.HStack(height=0):
                        ui.Spacer(width=20, height=0)
                        ui.Label("Primitive Type", name="text", height=0)
                        model = ui.ComboBox(0, *get_geometry_mesh_prim_list(), name="primitive_type").model
                        model.add_item_changed_fn(self.on_primitive_type_selected)
                        ui.Spacer(width=20, height=0)

                    ui.Spacer(width=0, height=10)
                    ui.Separator(height=0, name="text")
                    ui.Spacer(width=0, height=10)

                    with ui.ZStack(height=0):
                        mesh_names = get_geometry_mesh_prim_list()
                        for i in range(len(mesh_names)):
                            mesh_name = mesh_names[i]
                            stack = ui.VStack(spacing=0)
                            self._mesh_setting_ui[mesh_name] = stack
                            with stack:
                                ui.Spacer(height=20)
                                evaluator_class = _get_all_evaluators()[mesh_name]
                                evaluator_class.build_setting_ui()
                                ui.Spacer(height=5)
                            if i != 0:
                                stack.visible = False

                    ui.Spacer(width=0, height=20)
                    with ui.HStack(height=0):
                        ui.Spacer()
                        ui.Button(
                            "Create",
                            alignment=ui.Alignment.H_CENTER,
                            name="create",
                            width=120,
                            height=0,
                            mouse_pressed_fn=lambda *args: self._create_shape(),
                        )
                        ui.Button(
                            "Reset Settings",
                            alignment=ui.Alignment.H_CENTER,
                            name="reset",
                            width=120,
                            height=0,
                            mouse_pressed_fn=lambda *args: self._reset_settings(),
                        )
                        ui.Spacer()

            self._current_setting_index = 0
        self._window.visible = True

    def _create_shape(self):
        names = get_geometry_mesh_prim_list()
        mesh_type = names[self._current_setting_index]
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            omni.kit.commands.execute("CreateMeshPrimWithDefaultXform", prim_type=mesh_type, above_ground=True)

    def _reset_settings(self):
        names = get_geometry_mesh_prim_list()
        mesh_type = names[self._current_setting_index]
        evaluator_class = _get_all_evaluators()[mesh_type]
        evaluator_class.reset_setting()
