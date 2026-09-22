# Public API for module omni.kit.xr.ui.stage:

## Classes

- class XRTransformPrimCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: str, layer_identifier: Optional[str], new_transform: Gf.Matrix4d, old_transform: Gf.Matrix4d, remove_from_layer: bool)
  - def do(self)
  - def undo(self)

- class XRShutdown
  - class def add_shutdown_function(cls, fn: Callable[[], Any], module: str, description: str)
  - class def assert_object_deletion_upon_shutdown(cls, obj: Any)
  - class def run_shutdown_functions(cls, module: str)

- class XRControllerGuiLayer(XRGuiLayerComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def update_all_controllers(self)
  - def clear_controller_model(self, hand: str)
  - def clear_attachment_points(self, hand: str)
  - def update_controller_model(self, hand: str)
  - def on_changed(self, event: XRInputDeviceEvent)
  - def on_disabled(self, event: XRInputDeviceEvent)

- class XRHandGuiLayer(XRGuiLayerComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def update_all_hands(self)
  - def clear_hand_model(self, hand: str)
  - def clear_attachment_points(self, hand: str)
  - def update_hand_model(self, hand: str)
  - def on_changed(self, event: XRInputDeviceEvent)
  - def on_disabled(self, event: XRInputDeviceEvent)

- class XRTooltipsGuiLayer(XRGuiLayerComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def on_inputs_changed(self, event: XRInputDeviceEvent)
  - def update_both_hands(self)
  - def update_components(self, hand: str)
  - def clear_tooltip(self, hand: str, input: str)
  - def build_trackpad_thumbstick_tooltip(self, hand: str, input: str)
  - def build_button_tooltip(self, hand: str, input: str)
  - def on_update_tooltip(self, event: XRTooltipEvent)
  - def update_tooltip(self, hand: str, input: str)
  - def on_inputs_disabled(self, event: XRInputDeviceEvent)
  - def add_tooltip(self, usd_path: Optional[str], body: Union[List[XRTextIcon], XRTextIcon, None], title: Union[XRTextIcon, None]) -> Optional[UiContainer]
  - def get_tooltip_usd_path(self, hand: str, component: str) -> Optional[str]
  - def get_tooltip_prefix_text(self, component: str) -> Optional[str]
  - def get_tooltip_icon(self, component: str) -> Optional[str]
  - def get_icon_file_path(self, icon: str) -> Optional[str]

- class XRGrabTool(XRToolComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def grab_press(self, event: XRInputDeviceGeneratorEvent)
  - def grab_release(self, event: XRInputDeviceGeneratorEvent, commit: bool = True)
  - def grab_suspend(self, event: XRInputDeviceGeneratorEvent)
  - def grab_info_to_make_undo(self, hand: str, grabbed_prim: str)
  - def clear_undo_info(self, hand: str)

- class XRMenuTool(XRToolComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def toggle_menu(self)
  - def hide_settings_menu(self)
  - def place_settings_menu(self)
  - def on_update(self)

- class XRMoveTool(XRToolComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def move(self, event: XRInputDeviceGeneratorEvent)
  - def start_move(self, ev: XRSelectionEvent)
  - def end_move(self, ev: XRSelectionEvent)
  - def grab_info_to_make_undo(self, hand: str, grabbed_prim: str)
  - def clear_undo_info(self, hand: str)

- class XRNavigationTool(XRToolComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def rotate(self, amount: float)
  - def rotate_left(self)
  - def rotate_right(self)
  - def fly_accelerate(self, event)
  - def fly_accelerate_suspend(self)
  - def fly(self, event: XRInputDeviceGeneratorEvent)

- class XRSelectTool(XRToolComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def update_beam(self)
  - def on_disable(self)
  - def on_update(self)
  - def setup_beam(self, hand: str)
  - def remove_beams(self)
  - def toggle_beam_enable(self, event: XRInputDeviceGeneratorEvent)
  - def beam_select_press(self, event: XRInputDeviceGeneratorEvent)
  - def beam_select_release(self, event: XRInputDeviceGeneratorEvent)
  - def default_action_select_object(self, ev: XRSelectionEvent)
  - def action_gui_press(self, event: XRSelectionEvent)
  - def action_gui_release(self, event: XRSelectionEvent)
  - def action_gui_hover_enter(self, event: XRSelectionEvent)
  - def action_gui_hover_leave(self, event: XRSelectionEvent)
  - def action_gui_hover(self, event: XRSelectionEvent)
  - def action_gui_update(self, event: XRSelectionEvent)

- class XRTeleportTool(XRToolComponentBase)
  - def __init__(self)
  - def on_enable(self)
  - def update_teleport(self)
  - def on_disable(self)
  - def remove_teleporters(self)
  - def build_teleporters(self)
  - def arc_height_change(self, *args)
  - def load_models(self)
  - def setup_teleport(self, hand: str) -> Optional[XRTeleporterBeam]
  - def teleport_forward_press(self, event: XRInputDeviceGeneratorEvent)
  - def teleport_backward_press(self, event: XRInputDeviceGeneratorEvent)
  - def teleport_press(self, event: XRInputDeviceGeneratorEvent, direction: str)
  - def teleport_update(self, event: XRInputDeviceGeneratorEvent)
  - def teleport_release(self, event: XRInputDeviceGeneratorEvent)
  - def teleport_suspend(self, event: XRInputDeviceGeneratorEvent)

- class XRUIStageCommonExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def register_tools(self)

## Functions

- def warm_up_ui_material()

## Other

- omni.ext: public module
