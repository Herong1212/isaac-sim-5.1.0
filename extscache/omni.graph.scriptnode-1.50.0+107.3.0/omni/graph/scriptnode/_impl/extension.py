"""Support required by the Carbonite extension loader"""

import asyncio
from contextlib import suppress
from typing import List

import carb
import carb.dictionary
import omni.ext
import omni.graph.core as og
from omni.kit.app import get_app

SCRIPTNODE_OPT_IN_SETTING = "/app/omni.graph.scriptnode/opt_in"
SCRIPTNODE_ENABLE_OPT_IN_SETTING = "/app/omni.graph.scriptnode/enable_opt_in"
OMNIGRAPH_STAGEUPDATE_ORDER = 100  # We want our attach() to run after OG so that nodes have been instantiated


# ==============================================================================================================
def set_all_graphs_enabled(enable: bool):
    """Set the enabled state of all OmniGraphs"""
    graphs = og.get_all_graphs()
    if graphs and not isinstance(graphs, list):
        graphs = [graphs]
    for graph in graphs:
        graph.set_disabled(not enable)


# ==============================================================================================================
def is_check_enabled():
    """Returns True if scriptnode opt-in is enabled"""
    settings = carb.settings.get_settings()
    if not settings.is_accessible_as(carb.dictionary.ItemType.BOOL, SCRIPTNODE_ENABLE_OPT_IN_SETTING):
        # The enable-setting is not present, we enable the check
        return True

    if not settings.get(SCRIPTNODE_ENABLE_OPT_IN_SETTING):
        # The enable-setting is present and False, disable the check
        return False
    # the enable-setting is present and True, enable the check
    return True


# ==============================================================================================================
def on_opt_in_change(item: carb.dictionary.Item, change_type: carb.settings.ChangeEventType):
    """Update the local cache of the setting value"""
    if change_type != carb.settings.ChangeEventType.CHANGED:
        return
    settings = carb.settings.get_settings()
    should_run = bool(settings.get(SCRIPTNODE_OPT_IN_SETTING))
    if should_run:
        set_all_graphs_enabled(True)


# ==============================================================================================================
def verify_scriptnode_load(script_nodes: List[og.Node]):
    """
    Get verification from the user that they want to run scriptnodes.
    This opt-in applies to the current session only.

    Args:
        script_nodes: The list of script nodes on the stage that have
                      been disabled.
    """
    from omni.kit.window.popup_dialog import MessageDialog

    def on_cancel(dialog: MessageDialog):
        settings = carb.settings.get_settings()
        settings.set(SCRIPTNODE_OPT_IN_SETTING, False)
        dialog.hide()

    def on_ok(dialog: MessageDialog):
        settings = carb.settings.get_settings()
        settings.set(SCRIPTNODE_OPT_IN_SETTING, True)
        dialog.hide()

    message = """
This stage contains scriptnodes.

There is currently no limitation on what code can be executed by this node. This means that graphs that contain these nodes should only be used when the author of the graph is trusted.

Do you want to enable the scriptnode functionality for this session?
"""

    dialog = MessageDialog(
        title="ScriptNode Warning",
        width=400,
        message=message,
        cancel_handler=on_cancel,
        ok_handler=on_ok,
        ok_label="Yes",
        cancel_label="No",
    )

    async def show_async():
        # wait a few frames to allow the app ui to finish loading
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        dialog.show()

    asyncio.ensure_future(show_async())


# ==============================================================================================================
def check_for_scriptnodes():
    """
    Check for presence of omni.graph.scriptnode instances and confirm user wants to enable them.
    """
    # If the check is not enabled then we are good
    if not is_check_enabled():
        return

    # Check is enabled - see if they already opted-in
    settings = carb.settings.get_settings()
    scriptnode_opt_in = settings.get(SCRIPTNODE_OPT_IN_SETTING)
    if scriptnode_opt_in:
        # The check is enabled, and they opted-in
        return

    # The check is enabled but they opted out, or haven't been prompted yet

    try:
        import omni.kit.window.popup_dialog  # noqa
    except ImportError:  # pragma: no cover
        # Don't prompt in headless mode
        return
    script_nodes = []
    graphs = og.get_all_graphs()
    if graphs and not isinstance(graphs, list):
        graphs = [graphs]
    for graph in graphs:
        for node in graph.get_nodes():
            node_type = node.get_node_type()
            if node_type.get_node_type() == "omni.graph.scriptnode.ScriptNode":
                # Found one
                script_nodes.append(node)
    if not script_nodes:
        # No script nodes means we can leave them enabled
        return

    # Disable them until we get the opt-in via the async dialog
    set_all_graphs_enabled(False)
    verify_scriptnode_load(script_nodes)


def on_attach(ext_id: int, _):
    """Called when USD stage is attached"""
    check_for_scriptnodes()


# ==============================================================================================================
class _PublicExtension(omni.ext.IExt):
    """Object that tracks the lifetime of the Python part of the extension loading"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stage_subscription = None
        self.__opt_in_setting_sub = None

        with suppress(ImportError):
            manager = get_app().get_extension_manager()
            # This is a bit of a hack to make the template directory visible to the OmniGraph UI extension
            # if it happens to already be enabled. The "hack" part is that this logic really should be in
            # omni.graph.ui, but it would be much more complicated there, requiring management of extensions
            # that both do and do not have dependencies on omni.graph.ui.
            if manager.is_extension_enabled("omni.graph.ui"):
                import omni.graph.ui as ogui  # noqa: PLW0621

                ogui.ComputeNodeWidget.get_instance().add_template_path(__file__)

    def on_startup(self):
        stage_update = omni.stageupdate.get_stage_update_interface()
        self.__stage_subscription = stage_update.create_stage_update_node("OmniGraphAttach", on_attach_fn=on_attach)
        assert self.__stage_subscription
        nodes = stage_update.get_stage_update_nodes()
        stage_update.set_stage_update_node_order(len(nodes) - 1, OMNIGRAPH_STAGEUPDATE_ORDER + 1)
        self.__opt_in_setting_sub = omni.kit.app.SettingChangeSubscription(SCRIPTNODE_OPT_IN_SETTING, on_opt_in_change)
        assert self.__opt_in_setting_sub

    def on_shutdown(self):
        self.__stage_subscription = None
        self.__opt_in_setting_sub = None
