# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["stop_or_show_live_session_widget", "LiveSessionWidgetExtension"]

import asyncio
from enum import Enum
from functools import partial
from typing import Union

import carb
import omni.client
import omni.ext
import omni.kit.app
import omni.kit.clipboard
import omni.kit.notification_manager as nm
import omni.kit.usd.layers as layers
from omni.kit.widget.live_session_management_ui import LiveSessionEndWindow
from omni.kit.widget.live_session_management_ui import LiveSessionInterface
from omni.kit.widget.live_session_management_ui import JoinWithSessionLinkWindow
from omni.kit.widget.live_session_management_ui import LiveSessionStartWindow
from omni.kit.widget.live_session_management_ui import ShareSessionLinkWindow
from omni.kit.widget.prompt import PromptButtonInfo, PromptManager
import omni.usd
import omni.ui as ui
from pxr import Sdf

from .layer_icons import LayerIcons
from .live_session_model import LiveSessionModel
from .live_style import Styles
from .utils import (
    is_extension_loaded,
    join_live_session,
    is_viewer_only_mode,
    is_quick_join_enabled,
    get_session_list_select,
    SESSION_LIST_SELECT_DEFAULT_SESSION,
)


_extension_instance = None


class LiveSessionMenuOptions(Enum):
    QUIT_ONLY = 0
    MERGE_AND_QUIT = 1


class LiveSessionWidgetExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        global _extension_instance
        _extension_instance = self
        extension_path = omni.kit.app.get_app_interface().get_extension_manager().get_extension_path(ext_id)
        self._settings = None
        LayerIcons.on_startup(extension_path)
        self._live_session_end_window = None
        self._live_session_start_window = None
        self._join_with_session_link_window = None
        self._share_session_link_window = None
        self._live_session_menu = None
        self._app = omni.kit.app.get_app()
        try:
            from omni.kit.window.preferences import register_page
            from .live_session_preferences import LiveSessionPreferences

            self._settings = register_page(LiveSessionPreferences())
        except ImportError:  # pragma: no cover
            pass
        Styles.on_startup()

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None
        self._live_session_menu = None
        if self._live_session_end_window:
            self._live_session_end_window.destroy()
            self._live_session_end_window = None

        if self._live_session_start_window:
            self._live_session_start_window.destroy()
            self._live_session_start_window = None

        if self._join_with_session_link_window:
            self._join_with_session_link_window.destroy()
            self._join_with_session_link_window = None

        if self._share_session_link_window:
            self._share_session_link_window.destroy()
            self._share_session_link_window = None

        if self._settings:
            try:
                from omni.kit.window.preferences import unregister_page

                unregister_page(self._settings)
            except ImportError:
                pass
            self._settings = None

    @staticmethod
    def get_instance():
        global _extension_instance
        return _extension_instance

    def _on_live_session_end_cb(self, layers_interface: layers.Layers):
        live_syncing = layers_interface.get_live_syncing()
        self._live_session_end_window.visible = False
        if not live_syncing.is_layer_in_live_session(
            self._live_session_end_window.current_session.base_layer_identifier
        ):
            return

        prompt = None

        async def pre_merge(current_session):
            nonlocal prompt
            app = omni.kit.app.get_app()
            await app.next_update_async()
            await app.next_update_async()
            prompt = PromptManager.post_simple_prompt(
                "Merging", "Merging live layers into base layers...", None, shortcut_keys=False
            )

        async def post_merge(success):
            nonlocal prompt
            if prompt:
                prompt.destroy()
                prompt = None

            if success:
                await live_syncing.broadcast_merge_done_message_async(
                    layer_identifier=self._live_session_end_window.current_session.base_layer_identifier
                )

        current_session = live_syncing.get_current_live_session(
            self._live_session_end_window.current_session.base_layer_identifier
        )
        comment = self._live_session_end_window.description_field.model.get_value_as_string()
        option = self._live_session_end_window.options_combo.model.get_item_value_model().as_int
        if option == 1:

            def save_model(file_path: str, overwrite_existing: bool):
                layer = Sdf.Layer.FindOrOpen(file_path)
                if not layer:
                    layer = Sdf.Layer.CreateNew(file_path)

                if not layer:
                    error = f"Failed to save live changes to layer {file_path} as it's not writable."
                    carb.log_error(error)
                    nm.post_notification(error, status=nm.NotificationStatus.WARNING)

                    return

                asyncio.ensure_future(
                    live_syncing.merge_and_stop_live_session_async(
                        file_path,
                        comment,
                        pre_merge=pre_merge,
                        post_merge=post_merge,
                        layer_identifier=self._live_session_end_window.current_session.base_layer_identifier,
                    )
                )

            usd_context = live_syncing.usd_context
            stage = usd_context.get_stage()
            root_layer_identifier = stage.GetRootLayer().identifier
            root_layer_name = current_session.name
            self._live_session_end_window.show_file_picker(save_model, root_layer_identifier, root_layer_name)
        elif option == 0:
            asyncio.ensure_future(
                live_syncing.merge_and_stop_live_session_async(
                    comment=comment,
                    pre_merge=pre_merge,
                    post_merge=post_merge,
                    layer_identifier=self._live_session_end_window.current_session.base_layer_identifier,
                )
            )

    def _show_live_session_end_window(self, layers_interface: layers.Layers, layer_identifier):
        if self._live_session_end_window:
            self._live_session_end_window.destroy()

        async def show_dialog():
            live_syncing = layers_interface.get_live_syncing()
            current_session = live_syncing.get_current_live_session(layer_identifier)
            self._live_session_end_window = LiveSessionEndWindow(
                current_session, on_ok_button_cb=partial(self._on_live_session_end_cb, layers_interface)
            )
            await live_syncing.broadcast_merge_started_message_async(layer_identifier)
            async with self._live_session_end_window:
                pass

        asyncio.ensure_future(show_dialog())

    def _on_join_with_session_link_button_cb(self, layers_interface, session_link):
        live_syncing = layers_interface.get_live_syncing()

        async def open_stage_with_live_session(live_syncing, session_link):
            (success, error) = await live_syncing.open_stage_with_live_session_async(session_link)
            if not success:
                nm.post_notification(f"Failed to open stage {session_link} with live session: {error}.")

        asyncio.ensure_future(open_stage_with_live_session(live_syncing, session_link))

    def _show_join_with_session_link_window(self, layers_interface):
        current_session_link = None

        # Destroys it to center the window.
        if self._join_with_session_link_window:
            current_session_link = self._join_with_session_link_window.current_session_link
            self._join_with_session_link_window.destroy()

        self._join_with_session_link_window = JoinWithSessionLinkWindow(
            partial(self._on_join_with_session_link_button_cb, layers_interface)
        )
        self._join_with_session_link_window.visible = True
        if current_session_link:
            self._join_with_session_link_window.current_session_link = current_session_link

    def _show_share_session_link_window(self, layers_interface, layer_identifier):
        # Destroys it to center the window.
        if self._share_session_link_window:
            self._share_session_link_window.destroy()

        self._share_session_link_window = ShareSessionLinkWindow(
            LiveSessionModel(layers_interface, layer_identifier, False)
        )
        self._share_session_link_window.visible = True

    def _show_live_session_menu_options(
        self, layers_interface, layer_identifier, is_stage_session, prim_path: Union[str, Sdf.Path] = None
    ):
        live_syncing = layers_interface.get_live_syncing()
        current_session = live_syncing.get_current_live_session(layer_identifier)
        self._live_session_menu = ui.Menu("global_live_update")
        import omni.client
        is_omni_objects_enabled = omni.client.is_omni_objects_enabled(layer_identifier)
        is_live_prim = prim_path or live_syncing.is_layer_in_live_session(layer_identifier, live_prim_only=True)

        with self._live_session_menu:
            if is_omni_objects_enabled:
                if current_session:
                    if is_extension_loaded("omni.timeline.live_session"):
                        import omni.timeline.live_session

                        timeline_session = omni.timeline.live_session.get_timeline_session()
                        if timeline_session is not None:
                            session_window = omni.timeline.live_session.get_session_window()
                            ui.MenuItem(
                                "Open Timeline Window",
                                triggered_fn=lambda *args: self._on_open_timeline_session_window(
                                    layers_interface, layer_identifier, timeline_session, session_window
                                ),
                            )
                            ui.MenuItem(
                                "Synchronize Timeline",
                                triggered_fn=lambda *args: self._on_timeline_sync_triggered(
                                    layers_interface, layer_identifier, timeline_session
                                ),
                                checkable=True,
                                checked=timeline_session.is_sync_enabled(),
                            )
                            ui.Separator()
                    # If layer is in the live session already, showing `leave` and `end and merge`
                    ui.MenuItem(
                        "Leave Session",
                        triggered_fn=lambda *args: self._on_leave_live_session_menu_options(
                            layers_interface, LiveSessionMenuOptions.QUIT_ONLY, layer_identifier
                        ),
                    )

                    if not is_viewer_only_mode():
                        ui.MenuItem(
                            "End and Merge",
                            triggered_fn=lambda *args: self._on_leave_live_session_menu_options(
                                layers_interface, LiveSessionMenuOptions.MERGE_AND_QUIT, layer_identifier
                            ),
                        )
                    ui.Separator()
                else:
                    # If it's not in the live session, show `join` and `create`.
                    ui.MenuItem(
                        "Join Session",
                        triggered_fn=lambda *args: self._show_live_session_start_window(
                            layers_interface, layer_identifier, prim_path, True
                        ),
                    )
                    ui.MenuItem(
                        "Create Session",
                        triggered_fn=lambda *args: self._show_live_session_start_window(
                            layers_interface, layer_identifier, prim_path, False
                        ),
                    )

                # Don't show those options for live prim
                if not is_live_prim:
                    # If layer_identifier is given, it's to show menu options for sublayer.
                    # Show `copy` to copy session link. Otherwise, show share session dialog
                    # to choose session to share.
                    if is_stage_session:
                        ui.Separator()
                        ui.MenuItem(
                            "Share Session Link",
                            triggered_fn=lambda *args: self._show_share_session_link_window(
                                layers_interface, layer_identifier
                            ),
                        )
                    elif current_session:
                        ui.Separator()
                        ui.MenuItem(
                            "Copy Session Link",
                            triggered_fn=lambda *args: self._copy_session_link(layers_interface),
                        )

            # If layer identifier is gven, it will not show `join with session link` menu option.
            if is_stage_session and not is_live_prim:
                ui.MenuItem(
                    "Join With Session Link",
                    triggered_fn=lambda *args: self._show_join_with_session_link_window(layers_interface),
                )

        self._live_session_menu.show()

    def _on_join_session(
        self,
        layers_interface: layers.Layers,
        current_session: LiveSessionInterface,
        layer_identifier: str,
        prim_path: Union[str, Sdf.Path],
    ) -> bool:
        return join_live_session(layers_interface, layer_identifier, current_session, prim_path, is_viewer_only_mode())

    def _create_live_session(
        self, layers_interface: layers.Layers, layer_identifier: str, name: str
    ) -> LiveSessionInterface:
        live_syncing = layers_interface.get_live_syncing()
        return live_syncing.create_live_session(name, layer_identifier)

    def _show_live_session_start_window(
        self,
        layers_interface: layers.Layers,
        layer_identifier: str,
        prim_path: Union[str, Sdf.Path] = None,
        join_session=None,
    ):
        if self._live_session_start_window:
            self._live_session_start_window.destroy()

        session_model = LiveSessionModel(layers_interface, layer_identifier)
        self._live_session_start_window = LiveSessionStartWindow(
            session_model,
            prim_path,
            partial(self._on_join_session, layers_interface),
            partial(self._create_live_session, layers_interface),
        )

        # Select default session if it's set by default or latest accessed one.
        if get_session_list_select() == SESSION_LIST_SELECT_DEFAULT_SESSION:
            self._live_session_start_window.select_default_session()
        self._live_session_start_window.visible = True
        if join_session is not None:
            self._live_session_start_window.set_focus(join_session)

    def _show_session_start_window_or_menu(
        self,
        layers_interface: layers.Layers,
        show_join_options,
        layer_identifier,
        is_stage_session,
        join_session=None,
        prim_path=None,
    ):
        if show_join_options:
            return self._show_live_session_menu_options(layers_interface, layer_identifier, is_stage_session, prim_path)
        else:
            self._show_live_session_start_window(layers_interface, layer_identifier, prim_path, join_session)

        return None

    def _on_timeline_sync_triggered(self, layers_interface: layers.Layers, layer_identifier: str, timeline_session):
        timeline_session.enable_sync(not timeline_session.is_sync_enabled())

    def _on_open_timeline_session_window(
        self,
        layers_interface: layers.Layers,
        layer_identifier: str,
        timeline_session,
        session_window,
    ):
        session_window.show()

    def _on_leave_live_session_menu_options(
        self,
        layers_interface: layers.Layers,
        options: LiveSessionMenuOptions,
        layer_identifier: str,
    ):
        live_syncing = layers_interface.get_live_syncing()
        current_session = live_syncing.get_current_live_session(layer_identifier)
        if current_session:
            if options == LiveSessionMenuOptions.QUIT_ONLY:
                if self._can_quit_session_directly(live_syncing, layer_identifier):
                    live_syncing.stop_live_session(layer_identifier)
                else:
                    PromptManager.post_simple_prompt(
                        "Leave Session",
                        f"You are about to leave '{current_session.name}' session.",
                        PromptButtonInfo("LEAVE", lambda: live_syncing.stop_live_session(layer_identifier)),
                        PromptButtonInfo("CANCEL"),
                    )
            elif options == LiveSessionMenuOptions.MERGE_AND_QUIT:
                layers_state = layers_interface.get_layers_state()
                is_read_only_on_disk = layers_state.is_layer_readonly_on_disk(layer_identifier)
                if current_session.merge_permission and not is_read_only_on_disk:
                    self._show_live_session_end_window(layers_interface, layer_identifier)
                else:
                    if is_read_only_on_disk:
                        owner = layers_state.get_layer_owner(layer_identifier)
                    else:
                        owner = current_session.owner

                    logged_user_name = current_session.logged_user_name
                    if logged_user_name == owner and current_session.merge_permission:
                        message = (
                            f"You currently do not have merge privileges as base layer is read-only on disk."
                            " Do you want to quit this live session?"
                        )
                    else:
                        if is_read_only_on_disk:
                            message = (
                                f"You currently do not have merge privileges as base layer is read-only on disk."
                                f" Please contact '{owner}' to grant you write access. Do you want to quit this live session?"
                            )
                        else:
                            message = (
                                f"You currently do not have merge privileges, please contact '{owner}'"
                                " to merge any changes from the live session. Do you want to quit this live session?"
                            )

                    PromptManager.post_simple_prompt(
                        "Permission Denied",
                        message,
                        PromptButtonInfo("YES", lambda: live_syncing.stop_live_session(layer_identifier)),
                        PromptButtonInfo("NO"),
                    )

    def _can_quit_session_directly(self, live_syncing: layers.LiveSyncing, layer_identifier):
        current_live_session = live_syncing.get_current_live_session(layer_identifier)
        if current_live_session:
            if current_live_session.peer_users:
                return False

            layer = Sdf.Find(current_live_session.root)
            if layer and len(layer.rootPrims) > 0:
                return False

        return True

    def _copy_session_link(self, layers_interface):
        live_syncing = layers_interface.get_live_syncing()
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return

        omni.kit.clipboard.copy(current_session.shared_link)

    def _stop_or_show_live_session_widget_internal(
        self,
        layers_interface: layers.Layers,
        stop_session_only,
        stop_session_forcely,
        show_join_options,
        layer_identifier,
        quick_join="",
        prim_path: Union[str, Sdf.Path] = None,
    ):
        usd_context = layers_interface.usd_context
        stage = usd_context.get_stage()
        # Skips it if stage is not opened.
        if not stage:
            return None

        # By default, it will join live session of tht root layer.
        if not layer_identifier:
            # If layer identifier is not provided, it's to show global
            # menu that includes share sesison link and join session with link.
            # Otherwise, it will show menu for the sublayer session only.
            is_stage_session = True
            root_layer = stage.GetRootLayer()
            layer_identifier = root_layer.identifier
        else:
            is_stage_session = False

        layer_handle = Sdf.Find(layer_identifier)
        if (
            not layer_handle
            or (not prim_path and not stage.HasLocalLayer(layer_handle))
            or (prim_path and layer_handle not in stage.GetUsedLayers())
        ):
            nm.post_notification(
                "Only a layer opened in the current stage can start a live-sync session.",
                status=nm.NotificationStatus.WARNING,
            )
            return None

        if not omni.client.is_omni_objects_enabled(layer_identifier):
            if is_stage_session and not prim_path:
                return self._show_live_session_menu_options(layers_interface, layer_identifier, is_stage_session)
            else:
                nm.post_notification(
                    "Only a layer in Nucleus can start a live-sync session.", status=nm.NotificationStatus.WARNING
                )

                return None

        live_syncing = layers_interface.get_live_syncing()
        if not live_syncing.is_layer_in_live_session(layer_identifier):
            if not quick_join and not show_join_options:
                quick_join = "Default"
            elif quick_join and show_join_options:
                show_join_options = False

            if quick_join:
                # This runs when the main live button is pressed.
                live_syncing = layers_interface.get_live_syncing()
                quick_session = live_syncing.find_live_session_by_name(layer_identifier, quick_join)
                if is_quick_join_enabled():
                    if not quick_session:
                        quick_session = live_syncing.create_live_session(
                            layer_identifier=layer_identifier, name=quick_join
                        )
                        if not quick_session:
                            nm.post_notification(
                                "Cannot create a Live session on a read only location. Please\n"
                                "save root file in a writable location.",
                                status=nm.NotificationStatus.WARNING,
                            )
                            return None

                    join_live_session(
                        layers_interface, layer_identifier, quick_session, prim_path, is_viewer_only_mode()
                    )
                    return None
                else:
                    join_session = True if quick_session is not None else False
                    return self._show_session_start_window_or_menu(
                        layers_interface, False, layer_identifier, False, join_session, prim_path
                    )
            else:
                return self._show_session_start_window_or_menu(
                    layers_interface, show_join_options, layer_identifier, is_stage_session, prim_path
                )
        elif stop_session_forcely:
            live_syncing.stop_live_session(layer_identifier)
        elif stop_session_only:
            self._on_leave_live_session_menu_options(
                layers_interface, LiveSessionMenuOptions.QUIT_ONLY, layer_identifier
            )
        else:
            return self._show_live_session_menu_options(layers_interface, layer_identifier, is_stage_session, prim_path)

        return None


def stop_or_show_live_session_widget(
    usd_context: Union[str, omni.usd.UsdContext] = "",
    stop_session_only: bool = False,
    stop_session_forcely: bool = False,
    show_join_options: bool = True,
    layer_identifier: str = None,
    quick_join: str = False,
    prim_path: Union[str, Sdf.Path] = None,
):
    """Stops current live session or shows widget to join/leave session. If current session is empty, it will show the session start dialog. If current session is not empty, it will stop session directly or show stop session menu.

    Args:
        usd_context (Union[str, omni.usd.UsdContext]): The current usd context to operate on.
        stop_session_only (bool): If True, ask user to stop session without merge options.
        stop_session_forcely (bool): If True, force stop session even if current session is not empty.
        show_join_options (bool): If True, show menu options; if False, show session dialog directly.
        layer_identifier (str): By default, join/stop the root layer session; if provided, join/stop specific sublayer.
        quick_join (str): Quick join or leave session without dialog; used only when layer is not in a live session.
        prim_path (Union[str, Sdf.Path]): Join live session for the prim instead of sublayers.

    Returns:
        The menu widgets created if options menu is needed, otherwise None.
    """

    instance = LiveSessionWidgetExtension.get_instance()
    if not instance:  # pragma: no cover
        carb.log_error("omni.kit.widget.live_session_management extension must be enabled.")
        return

    layers_interface = layers.get_layers(usd_context)
    return instance._stop_or_show_live_session_widget_internal(
        layers_interface,
        stop_session_only,
        stop_session_forcely,
        show_join_options,
        layer_identifier,
        quick_join=quick_join,
        prim_path=prim_path,
    )
