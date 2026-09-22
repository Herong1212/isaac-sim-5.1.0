import carb
import carb.eventdispatcher
import asyncio
import omni.usd
import omni.kit.app

from pxr import Usd
from functools import lru_cache
from pathlib import Path
from omni.kit import ui_test
import omni.ext

__all__ = [
    "get_test_data_path",
    "wait",
    "wait_stage_loading",
    "open_stage",
    "select_prims",
    "get_prims",
    "wait_for_window",
    "handle_assign_material_dialog",
    "handle_create_material_dialog",
    "delete_prim_path_children",
    "build_sdf_asset_frame_dictonary",
    "push_window_height",
    "pop_window_height",
    "handle_multiple_descendents_dialog",
    "arrange_windows",
    "wait_for_viewport_ready",
    "StageEventHandler",
    "TestSuiteHelpers"
]


class TestSuiteHelpers(omni.ext.IExt):

    stage_event_debug = False
    stage_loading_debug = False
    stage_debug = {}
    stage_state = {}

    def on_startup(self, ext_id):
        TestSuiteHelpers.stage_debug = {int(v): k for k, v in omni.usd.StageEventType.__dict__.items() if not k.startswith("_") and not k in ["name", "value"]}
        TestSuiteHelpers.stage_state = {}
        self._usd_context = omni.usd.get_context()
        self._stage_event_sub = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=self._usd_context.stage_event_name(omni.usd.StageEventType(i)),
                on_event=self._on_stage_event
            )
            for i in range(int(omni.usd.StageEventType.COUNT))
        ]

    def on_shutdown(self): # pragma: no cover
        self._stage_event_sub = None

    def _on_stage_event(self, event):
        stage_name = self._usd_context.get_stage_url() if self._usd_context else ""
        event_type = self._usd_context.stage_event_type(event.event_name)
        if stage_name:
            if not stage_name in TestSuiteHelpers.stage_state:
                TestSuiteHelpers.stage_state[stage_name] = []

            # treat ASSETS_LOAD_ABORTED as ASSETS_LOADED to make other code simpler
            if event_type == omni.usd.StageEventType.ASSETS_LOAD_ABORTED: # pragma: no cover
                TestSuiteHelpers.stage_state[stage_name].append(int(omni.usd.StageEventType.ASSETS_LOADED))
            else:
                TestSuiteHelpers.stage_state[stage_name].append(int(event_type))

        if TestSuiteHelpers.stage_event_debug:
            if int(event_type) < len(TestSuiteHelpers.stage_debug):
                carb.log_warn(f"{TestSuiteHelpers.stage_debug[int(event_type)]} for {stage_name}")
            else:  # pragma: no cover
                carb.log_warn(f"stage_event {event_type} {stage_name} for {stage_name}")

        # stage is closing, purge stage_stage info
        if event_type == omni.usd.StageEventType.CLOSING:
            del TestSuiteHelpers.stage_state[stage_name]
        # its possible to get ASSETS_LOADED without ASSETS_LOADING
        if event_type == omni.usd.StageEventType.ASSETS_LOADED and stage_name:
            stage_info = TestSuiteHelpers.stage_state[stage_name]
            if stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADING)) < stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADED)):
                TestSuiteHelpers.stage_state[stage_name].append(int(omni.usd.StageEventType.ASSETS_LOADING))
                if TestSuiteHelpers.stage_event_debug:
                    carb.log_warn(f"ASSETS_LOADED without ASSETS_LOADING {stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADING))} vs {stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADED))} for {stage_name}")

@lru_cache()
def get_test_data_path(module: str, subpath: str = "") -> str:
    if not subpath:
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(module)
        return str(Path(ext_path) / "data" / "tests")
    return str(Path(get_test_data_path(module)) / subpath)


async def wait():
    await omni.kit.app.get_app().next_update_async()
    await omni.kit.app.get_app().next_update_async()


async def wait_stage_loading(wait_frames: int = 2, usd_context=None, timeout=1000, timeout_error=True):
    """
    Waits for the USD stage to complete loading.

    Args:
        wait_frames (int): How many frames to wait after loading the stage if given (2 by default)
        usd_context (UsdContext): UsdContext to use (omni.usd.get_context() by default)
        timeout (int): How many frames to wait before reporting error & abort.
        timeout_error (bool): Report timeout as error (True by default)
    """
    if not usd_context:
        usd_context = omni.usd.get_context()
    stage_name = usd_context.get_stage_url()

    # wait for get_stage_loading_status() files to be loaded.
    maxloops = timeout
    while True:
        _, files_loaded, total_files = usd_context.get_stage_loading_status()
        if files_loaded or total_files:  # pragma: no cover
            await omni.kit.app.get_app().next_update_async()
            maxloops -= 1
            if maxloops == 0:
                if timeout_error:
                    carb.log_warn(f"wait_stage_loading waiting for {files_loaded} vs {total_files} for {stage_name}")
                break
            continue
        break

    # wait for number of ASSETS_LOADING be equal to ASSETS_LOADED
    if stage_name:
        stage_info = TestSuiteHelpers.stage_state[stage_name]
        if stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADING)) != stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADED)):
            if TestSuiteHelpers.stage_loading_debug:
                carb.log_warn(f"wait_stage_loading waiting for ASSETS_LOADED... {stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADING))} vs {stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADED))} for {stage_name}")

            maxloops = timeout
            while stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADING)) != stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADED)):
                await omni.kit.app.get_app().next_update_async()
                maxloops -= 1
                if maxloops == 0:
                    if timeout_error:  # pragma: no cover
                        carb.log_error(f"wait_stage_loading waiting timeout for {stage_name} .. {stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADING))} vs {stage_info.count(int(omni.usd.StageEventType.ASSETS_LOADED))}")
                    break  # pragma: no cover

            if TestSuiteHelpers.stage_loading_debug:
                carb.log_warn(f"wait_stage_loading completed")

    usd_context.reset_renderer_accumulation()

    frame_count = 0
    while frame_count < wait_frames:
        await omni.kit.app.get_app().next_update_async()
        frame_count += 1
        continue


async def open_stage(path: str, usd_context=omni.usd.get_context()):
    await usd_context.open_stage_async(path)
    await wait_stage_loading()


async def select_prims(paths, usd_context=omni.usd.get_context()):
    usd_context.get_selection().set_selected_prim_paths(paths, True)
    await wait()
    # wait for any materials to load
    await wait_stage_loading()


def get_prims(stage, exclude_list=[]):
    prims = []
    for p in stage.Traverse(Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded)):
        if p not in exclude_list:
            prims.append(p)
    return prims


async def wait_for_window(window_name: str):
    MAX_WAIT = 100

    # Find active window
    for _ in range(MAX_WAIT):
        window_root = ui_test.find(f"{window_name}")
        if window_root and window_root.widget.visible:
            await ui_test.human_delay()
            break
        await ui_test.human_delay(1)

    if not window_root:
        raise Exception("Can't find window {window_name}, wait time exceeded.")


async def handle_assign_material_dialog(index, strength_index=0): # pragma: no cover
    """Deprecated"""
    carb.log_warn("WARNING: 'handle_assign_material_dialog' is being DEPRECATED. Please use the function of the same name from 'omni.kit.material.library.test_helper.MaterialLibraryTestHelper'")

    from pxr import Sdf

    # handle assign dialog
    prims = omni.usd.get_context().get_selection().get_selected_prim_paths()
    if len(prims) == 1:
        shape = Sdf.Path(prims[0]).name
        window_name = f"Bind material to {shape}###context_menu_bind"
    else:
        window_name = f"Bind material to {len(prims)} selected models###context_menu_bind"

    await wait_for_window(window_name)

    # open listbox
    widget = ui_test.find(f"{window_name}//Frame/**/Button[*].identifier=='combo_open_button'")
    await ui_test.emulate_mouse_move_and_click(widget.center, human_delay_speed=4)
    # select material item on listbox
    await wait_for_window("MaterialPropertyPopupWindow")
    widget = ui_test.find(f"MaterialPropertyPopupWindow//Frame/**/TreeView[*]")
    # FIXME - can't use widget.click as open combobox has no readable size and clicks goto stage window
    item_name = widget.model.get_item_children(None)[index].name_model.as_string if index else "None"
    await ui_test.find(f"MaterialPropertyPopupWindow//Frame/**/Label[*].text=='{item_name}'").click(human_delay_speed=4)

    # select strength item on listbox
    widget = ui_test.find(f"{window_name}//Frame/**/ComboBox[*]")
    if widget:
        widget.model.set_value(strength_index)

    # click ok
    widget = ui_test.find(f"{window_name}//Frame/**/Button[*].identifier=='assign_material_ok_button'")
    await ui_test.emulate_mouse_move_and_click(widget.center, human_delay_speed=4)

    # wait for materials to load
    await ui_test.human_delay()
    await wait_stage_loading()


async def handle_create_material_dialog(mdl_path: str, mtl_name: str): # pragma: no cover
    """Deprecated"""
    carb.log_warn("WARNING: 'handle_create_material_dialog' is being DEPRECATED. Please use the function of the same name from 'omni.kit.material.library.test_helper.MaterialLibraryTestHelper'")

    subid_list = []
    def have_subids(id_list):
        nonlocal subid_list
        subid_list = id_list
    await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=mdl_path, on_complete_fn=have_subids)
    if len(subid_list)> 1:
        # material has subid and dialog is shown
        await wait_for_window("Create Material")
        create_widget = ui_test.find("Create Material//Frame/**/Button[*].identifier=='create_material_ok_button'")
        subid_widget = ui_test.find("Create Material//Frame/**/ComboBox[*].identifier=='create_material_subid_combo'")
        subid_list = subid_widget.model.get_item_list()
        subid_index = 0
        for index, subid in enumerate(subid_list):
            if subid.name == mtl_name:
                subid_index = index
        subid_widget.model.set_current_index(subid_index)
        await ui_test.human_delay()
        create_widget.widget.call_clicked_fn()
        await ui_test.human_delay(4)
        await wait_stage_loading()


async def delete_prim_path_children(prim_path: str):
    stage =  omni.usd.get_context().get_stage()
    root_prim = stage.GetPrimAtPath(prim_path)
    purge_list = []
    for prim in Usd.PrimRange(root_prim):
        if prim.GetPath().pathString != root_prim.GetPath().pathString:
            purge_list.append(prim)
    for prim in purge_list:
        stage.RemovePrim(prim.GetPath())

    # wait for refresh after deleting prims
    await ui_test.human_delay()

async def build_sdf_asset_frame_dictonary():
    widget_table = {}
    for frame in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
        if frame.widget.title != "Raw USD Properties":
            for widget in frame.find_all("Property//Frame/**/StringField[*].identifier!=''"):
                if widget.widget.identifier.startswith('sdf_asset_'):
                    if not frame.widget.title in widget_table:
                        widget_table[frame.widget.title] = {}
                    if not widget.widget.identifier in widget_table[frame.widget.title]:
                        widget_table[frame.widget.title][widget.widget.identifier] = 0
                    widget_table[frame.widget.title][widget.widget.identifier] += 1

    return widget_table


def push_window_height(cls, window_name, new_height=None):  # pragma: no cover
    """Deprecated"""
    carb.log_warn("WARNING: 'push_window_height' is being DEPRECATED.")
    window = ui_test.find(window_name)
    if window:
        if not hasattr(cls, "_original_window_height"):
            cls._original_window_height = {}
        cls._original_window_height[window_name] = window.widget.height
        if new_height is not None:
            window.widget.height = new_height


def pop_window_height(cls, window_name):  # pragma: no cover
    """Deprecated"""
    carb.log_warn("WARNING: 'push_window_height' is being DEPRECATED.")
    window = ui_test.find(window_name)
    if window:
        if hasattr(cls, "_original_window_height"):
            window.widget.height = cls._original_window_height[window_name]
            del cls._original_window_height[window_name]


async def handle_multiple_descendents_dialog(stage, prim_path: str, target_prim: str):
    root_prim = stage.GetPrimAtPath(prim_path)
    if not root_prim:
        return

    descendents = omni.usd.get_prim_descendents(root_prim)

    # skip if only root_prim
    if descendents == [root_prim]:
        return

    await ui_test.human_delay(10)
    await wait_for_window("Target prim has multiple descendents")
    await ui_test.human_delay(10)

    # need to select target_prim in combo_widget
    combo_widget = ui_test.find("Target prim has multiple descendents//Frame/**/ComboBox[*].identifier=='multi_descendents_combo'")
    combo_list = combo_widget.model.get_item_children(None)
    combo_index = 0
    for index, item in enumerate(combo_list):
        if item.prim.GetPrimPath().pathString == target_prim:
            combo_index = index

    combo_widget.model.set_current_index(combo_index)
    await ui_test.human_delay()

    ok_widget = ui_test.find("Target prim has multiple descendents//Frame/**/Button[*].identifier=='multi_descendents_ok_button'")
    await ok_widget.click()

    await wait_stage_loading()


async def arrange_windows(topleft_window="Stage", topleft_height=421.0, topleft_width=436.0, hide_viewport=False, topleft_position_x=0):
    """Arrange UI windows in the Omni UI environment.

    Args:
        topleft_window (str): Name of the top left window.
        topleft_height (float): Height for the top left window.
        topleft_width (float): Width for the top left window.
        hide_viewport (bool): If true, hides the viewport window.

    Returns:
        Window: The modified viewport window.
    """
    from omni.kit.viewport.utility import get_active_viewport_window
    viewport_window = get_active_viewport_window()
    # omni.ui & legacy viewport synch
    await wait()
    if viewport_window:
        vp_width = int(1436 - topleft_width) - topleft_position_x
        viewport_window.position_x = topleft_position_x
        viewport_window.position_y = 0
        viewport_window.width = vp_width
        viewport_window.height = 425
        viewport_window.visible = (not hide_viewport)

    import omni.ui as ui
    content_window = ui.Workspace.get_window("Content")
    if content_window:
        content_window.position_x = 0.0
        content_window.position_y = 448.0
        content_window.width = 1436.0 - topleft_width
        content_window.height = 421.0
        await ui_test.human_delay()

    stage_window = ui.Workspace.get_window("Stage")
    if stage_window:
        stage_window.position_x = 1436.0 - topleft_width
        stage_window.position_y = 0.0
        stage_window.width = topleft_width
        stage_window.height = topleft_height
        await ui_test.human_delay()

    layer_window = ui.Workspace.get_window("Layer")
    if layer_window:
        layer_window.position_x = 1436.0 - topleft_width
        layer_window.position_y = 0.0
        layer_window.width = topleft_width
        layer_window.height = topleft_height
        await ui_test.human_delay()

    tl_window = ui.Workspace.get_window(topleft_window)
    if tl_window:
        tl_window.focus()

    property_window = ui.Workspace.get_window("Property")
    if property_window:
        property_window.position_x = 1436.0 - topleft_width
        property_window.position_y = topleft_height + 27.0
        property_window.width = topleft_width
        property_window.height = 846.0 - topleft_height
        await ui_test.human_delay()

    # Wait for the layout to complete
    await wait()
    return viewport_window


async def wait_for_viewport_ready(usd_context=omni.usd.get_context()):
    future_test = asyncio.Future()

    def on_new_frame_event(_):
        nonlocal future_test

        if not future_test.done():
            future_test.set_result(True)

    # Subscribe to the event to wait for frame delivery
    new_frame_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
        event_name=usd_context.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, immediate=True),
        on_event=on_new_frame_event,
        observer_name="omni.kit.test_suite.helpers"
    )

    print("Waiting for StageRenderingEventType.NEW_FRAME")
    await future_test
    print("Received StageRenderingEventType.NEW_FRAME")

    # clean up
    del new_frame_sub
    del future_test

    for i in range(0, 10):
        await omni.kit.app.get_app().next_update_async()


class StageEventHandler():
    def __init__(self, ext_name):
        self._future_test = None
        self._required_stage_event = -1
        usd = omni.usd.get_context()
        self._stage_event_sub = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=usd.stage_event_name(omni.usd.StageEventType(i)),
                on_event=lambda _, event_type=i: self._on_stage_event(event_type)
            )
            for i in range(int(omni.usd.StageEventType.COUNT))
        ]

    def _on_stage_event(self, event_type):
        if self._future_test and int(self._required_stage_event) == event_type and not self._future_test.done():
            self._future_test.set_result(event_type)

    async def reset_stage_event(self, stage_event):
        self._required_stage_event = stage_event
        self._future_test = asyncio.Future()

    async def wait_for_stage_event(self, timeout=30.0):
        async def wait_for_event():
            await self._future_test

        try:
            await asyncio.wait_for(wait_for_event(), timeout=timeout)
        except asyncio.TimeoutError:
            carb.log_error(f"wait_for_stage_event timeout waiting for {self._required_stage_event}")
        finally:
            self._future_test = None
            self._required_stage_event = -1
