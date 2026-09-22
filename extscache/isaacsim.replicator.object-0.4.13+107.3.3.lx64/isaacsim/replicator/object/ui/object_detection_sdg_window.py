import carb
import omni.ext
import omni.kit.commands
import omni.kit.ui
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
import asyncio, os
from ..simulate import on_simulate_dev, on_init_scene_randomization, on_randomize_scene
from .scene_editing import toggle_visibility_in_range
from ..utility.scene import (
    get_stage,
    create_or_get_prim_attribute,
    get_attribute_sdf_type,
    observe_event,
    iro_environment_setup,
)
from ..utility.xform import set_xform_ops, get_xform_op_type
from pxr import UsdGeom
from .visualization import update_range, initialize_visualizer_tentative
from omni.kit.property.usd import GfVecAttributeSingleChannelModel, UsdAttributeModel
from .visualization import is_geometry

VISUALIZER_UPDATE_INTERVAL = 10



class ObjectDetectionSDGWindow(MenuHelperWindow):
    def __init__(self, ext):
        super().__init__(
            title="Object SDG",
            width=300,
            height=1000,
            dockPreference=ui.DockPreference.RIGHT,
        )
        self.ext = ext
        # Build out the scene
        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        """Clean up window resources"""
        # Clear UI elements
        self._object_detection_sdg_frame = None
        self.description_field = None
        # Clear extension reference
        self.ext = None
        # Call parent destroy
        super().destroy()

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 4
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0):
                    self._object_detection_sdg_frame = ui.CollapsableFrame(
                        title="Object SDG",
                        collapsed=False,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    )
                    with self._object_detection_sdg_frame:
                        with ui.VStack(spacing=0):
                            ui.Label("Description File")

                            description_model = ui.SimpleStringModel()
                            self.description_field = ui.StringField(description_model, multiline=True)

                            progress_bar = ui.ProgressBar()
                            ui.Button(
                                "Simulate",
                                clicked_fn=lambda: asyncio.ensure_future(
                                    on_simulate_dev(
                                        self.ext,
                                        self.description_field.model.get_value_as_string(),
                                        progress_bar,
                                        False,
                                        *self.ext.default_values,
                                    )
                                ),
                            )

                            files = []
                            for i in os.listdir(f"{os.path.dirname(__file__)}/../configs"):
                                if i.endswith(".yaml"):
                                    files.append(i[: i.rfind(".")])
                            files = sorted(files)
                            desc_selection = ui.ComboBox("description selection", *files)
                            for file in files:
                                desc_selection.model.append_child_item(None, ui.SimpleStringModel(file))

                            def update_textbox(model, files, description_field):
                                value = files[model.get_item_value_model().as_int]
                                description_field.model.set_value(value)

                            desc_selection.model.add_item_changed_fn(
                                lambda model, item: update_textbox(model, files, self.description_field)
                            )
                            self.description_field.model.set_value(files[0])

                            ui.Label("Scene Editing")
                            ui.Button("Toggle visibility of selected region", clicked_fn=toggle_visibility_in_range)

                            ui.Label("Embedded Interface")
                            ui.Button(
                                "Initialize scene randomization",
                                clicked_fn=lambda: asyncio.ensure_future(
                                    on_init_scene_randomization(
                                        self.ext, self.description_field.model.get_value_as_string()
                                    )
                                ),
                            )
                            ui.Button(
                                "Randomize scene",
                                clicked_fn=lambda: asyncio.ensure_future(on_randomize_scene(self.ext)),
                            )


# dynamic xform ops ui

# constants
TEXT_WIDTH = 50  # noqa
HEIGHT_GAP = 4  # noqa
WIDTH_GAP = 10  # noqa
RANGE_MIN = -1000000  # noqa
RANGE_MAX = 1000000  # noqa

operator_metadata = {
    "translate": (("X", "Y", "Z")),
    "rotateX": (("X")),
    "rotateY": (("Y")),
    "rotateZ": (("Z")),
    "rotateXYZ": (("X", "Y", "Z")),
    "rotateXZY": (("X", "Z", "Y")),
    "rotateYXZ": (("Y", "X", "Z")),
    "rotateYZX": (("Y", "Z", "X")),
    "rotateZXY": (("Z", "X", "Y")),
    "rotateZYX": (("Z", "Y", "X")),
    "scale": (("X", "Y", "Z")),
    "orient": (("W", "X", "Y", "Z")),
}

colors = {"W": 0xFFAA5555, "X": 0xFF5555AA, "Y": 0xFF76A371, "Z": 0xFFA07D4F}


# ui utils
# a label for the axis, with corresponding color
def axis_label(axis):
    with ui.ZStack(width=15):
        ui.Rectangle(
            width=15,
            height=20,
            style={
                "background_color": colors[axis],
                "border_radius": 3,
                "corner_flag": ui.CornerFlag.LEFT,
            },
        )
        ui.Label(axis, name="transform_label", alignment=ui.Alignment.CENTER)




# create or get bounding attributes for an operator
# op: like xformOp:translate:local
# return like xformOpStart:translate:local, xformOpEnd:translate:local
def get_operator_bounds(selected_prim, op):
    op_attr = selected_prim.GetAttribute(op)
    if op_attr.Get() is None:
        return
    op_sdf_type = get_attribute_sdf_type(op_attr)
    op_attr_start = create_or_get_prim_attribute(selected_prim, op.replace("xformOp", "xformOpStart"), op_sdf_type)
    op_attr_end = create_or_get_prim_attribute(selected_prim, op.replace("xformOp", "xformOpEnd"), op_sdf_type)
    op_attr_start.Set(op_attr.Get())
    op_attr_end.Set(op_attr.Get())
    return op_attr_start, op_attr_end


# relate attributes to ui models
def get_operator_bounds_model(selected_prim, op_attr, channel_index, is_single_channel=False):
    if not is_single_channel:
        return GfVecAttributeSingleChannelModel(
            get_stage(),
            [selected_prim.GetPath().AppendProperty(op_attr.GetName())],
            channel_index,
            True,
            op_attr.GetAllMetadata(),
            False,
        )
    else:
        return UsdAttributeModel(
            get_stage(),
            [selected_prim.GetPath().AppendProperty(op_attr.GetName())],
            True,
            op_attr.GetAllMetadata(),
            False,
        )


def build_dynamic_xform_ops_ui(window):
    if not window._distribution_visualizer_frame:
        carb.log_error("No distribution visualizer frame found")
        return

    with window._distribution_visualizer_frame: # don't add clear() here, it will break the functionality [bad rabbit]
        with ui.VStack(spacing=0):

            ui.Button("Apply Preset xformOps", clicked_fn=window.apply_preset_xform_ops)

            ui.Label("xform ops")
            selected_prim = window.selected_prim
            if not selected_prim or not selected_prim.IsValid():
                carb.log_error("No valid prim selected")
                return

            xform = UsdGeom.Xform(selected_prim) # False is a valid bool conversion for xform; don't check False here, it will break the functionality [bad rabbit]

            op_order = xform.GetXformOpOrderAttr().Get()
            if op_order is None:
                carb.log_error("No xform op order found")
                return
            for op in op_order:
                op_type = get_xform_op_type(op)
                op_attr = selected_prim.GetAttribute(op)
                if op_attr is None:
                    carb.log_error(f"No attribute found for {op}")
                    continue
                if op_type not in ("orient", "transform"):
                    # create or get attributes and bounding attributes for an operator

                    op_bounds = get_operator_bounds(selected_prim, op)
                    if op_bounds is None:
                        # Skip operators without concrete values
                        continue
                    op_attr_start, op_attr_end = op_bounds

                    # update ui for an operator
                    # value    -1,     -1,     -1
                    # start     0,      0,      0
                    # end       1,      1,      1
                    axes = operator_metadata[op_type]
                    is_single_channel = len(axes) == 1
                    ui.Label(op)
                    with ui.VStack(height=80):
                        with ui.HStack():
                            with ui.VStack(width=TEXT_WIDTH):
                                ui.Label("Value")
                                ui.Spacer(height=HEIGHT_GAP)
                                ui.Label("Start")
                                ui.Spacer(height=HEIGHT_GAP)
                                ui.Label("End")
                            ui.Spacer(width=WIDTH_GAP)
                            for i, axis in enumerate(axes):
                                with ui.VStack():
                                    with ui.HStack(height=20):
                                        axis_label(axis)
                                        # model for value
                                        model = get_operator_bounds_model(
                                            selected_prim, op_attr, i, is_single_channel
                                        )
                                        ui.FloatDrag(min=RANGE_MIN, max=RANGE_MAX, step=1, model=model)
                                    ui.Spacer(height=HEIGHT_GAP)
                                    with ui.HStack(height=20):
                                        # model for start
                                        model = get_operator_bounds_model(
                                            selected_prim, op_attr_start, i, is_single_channel
                                        )
                                        ui.FloatDrag(min=RANGE_MIN, max=RANGE_MAX, step=1, model=model)
                                    ui.Spacer(height=HEIGHT_GAP)
                                    with ui.HStack(height=20):
                                        # model for end
                                        model = get_operator_bounds_model(
                                            selected_prim, op_attr_end, i, is_single_channel
                                        )
                                        ui.FloatDrag(min=RANGE_MIN, max=RANGE_MAX, step=1, model=model)
                                ui.Spacer(width=WIDTH_GAP)
                else:
                    ui.Label(f"{op} = {op_attr.Get()}")


# when selection changed, build the dynamic xform ops ui to reflect updates in transform operators
def on_selection_changed_event(e, window):
    prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
    if len(prim_paths) == 1 and is_geometry(get_stage().GetPrimAtPath(prim_paths[0])):
        window.selected_prim = get_stage().GetPrimAtPath(prim_paths[0])
        build_dynamic_xform_ops_ui(window)


def on_update_event(e, window):
    window.visualizer_counter += 1
    if window.visualizer_counter % VISUALIZER_UPDATE_INTERVAL == 0:
        if window.selected_prim is not None:
            update_range(window)
        window.visualizer_counter = 0


# --- distribution visualizer ---


class DistributionVisualizerWindow(MenuHelperWindow):
    def __init__(self, ext):
        super().__init__(
            title="Distribution Visualizer",
            width=300,
            height=1000,
            dockPreference=ui.DockPreference.RIGHT,
        )
        self.ext = ext

        self.stage_event_sub = None
        self.update_event_sub = None
        self.selected_prim = None

        self.visualizer_shader = None
        self.visualizer_points_prim = None
        self.visualizer_counter = 0

        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        """Clean up window resources"""
        # Clear UI elements
        self._distribution_visualizer_frame = None

        # Unsubscribe from events
        if self.stage_event_sub is not None:
            self.stage_event_sub = None
        if self.update_event_sub is not None:
            self.update_event_sub = None

        # Clear visualizer resources
        self.visualizer_points_prim = None
        self.selected_prim = None

        # Clear extension reference
        self.ext = None

        # Call parent destroy
        super().destroy()

    def _build_ui(self):
        iro_environment_setup(self.ext)
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 6
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0):
                    self._distribution_visualizer_frame = ui.CollapsableFrame(
                        title="Distribution Visualizer",
                        collapsed=False,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    )
                    with self._distribution_visualizer_frame:
                        with ui.VStack(spacing=0):
                            ui.Button("Apply Preset xformOps", clicked_fn=self.apply_preset_xform_ops)

        # point cloud visualizer
        self.stage_event_sub = observe_event(
            omni.usd.get_context().stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED),
            lambda e: on_selection_changed_event(e, self),
            observer_name="isaacsim.replicator.object/Stage"
        )
        self.update_event_sub = observe_event(
            omni.kit.app.GLOBAL_EVENT_UPDATE,
            lambda e: on_update_event(e, self),
            observer_name="isaacsim.replicator.object/Update"
        )

        initialize_visualizer_tentative(self)

    def apply_preset_xform_ops(self):
        if self.selected_prim is not None and is_geometry(self.selected_prim):
            set_xform_ops(self.selected_prim, [("rotateY", 40), ("rotateX", 30), ("translate:local", [0, 0, 300])])
