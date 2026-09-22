# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LiveSessionCameraFollowerList"]


import carb
import omni.kit.collaboration.presence_layer as pl
import omni.kit.usd.layers as layers
import omni.ui as ui
import omni.usd
from pxr import Sdf

from .utils import build_live_session_user_layout

TOOLTIP_STYLE = {"color": ui.color("#979797"), "Tooltip": {"background_color": 0xEE222222}}


class LiveSessionCameraFollowerList:
    """Widget to build a user list to show all followers of the specific camera.

    Args:
        usd_context (omni.usd.UsdContext): USD Context instance.
        camera_path (Sdf.Path): Interested camera.

    Keyword Args:
        icon_size (int): The width and height of the user icon. 16 pixel by default.
        spacing (int): The horizontal spacing between two icons. 2 pixel by default.
        maximum_users (int): The maximum users to show, and show others with overflow.
        show_my_following_users (bool): Whether it should show the users that are following me or not.
    """

    def __init__(self, usd_context: omni.usd.UsdContext, camera_path: Sdf.Path, **kwargs):
        """Initializes the LiveSessionCameraFollowerList widget."""

        self.__icon_size = kwargs.get("icon_size", 16)
        self.__spacing = kwargs.get("spacing", 2)
        self.__maximum_count = kwargs.get("maximum_users", 3)
        self.__show_my_following_users = kwargs.get("show_my_following_users", True)
        self.__camera_path = camera_path
        self.__usd_context = usd_context
        self.__presence_layer = pl.get_presence_layer_interface(self.__usd_context)
        self.__layers = layers.get_layers(usd_context)
        self.__live_syncing = layers.get_live_syncing()
        self.__layers_event_subscriptions = []
        self.__main_layout: ui.HStack = ui.HStack(width=0, height=0)
        self.__all_user_layouts = {}
        self.__initialize()
        self.__overflow = False
        self.__overflow_button = None

    @property
    def layout(self) -> ui.HStack:
        """Gets the root widget of the list.

        Returns:
            ui.HStack: The root widget of the list.
        """

        return self.__main_layout

    def empty(self) -> bool:
        """Checks if any user icons have been added.

        Returns:
            bool: True if no user icons are added, False otherwise.
        """

        return len(self.__all_user_layouts) == 0

    def track_camera(self, camera_path: Sdf.Path):
        """Switches the camera path to listen to.

        Args:
            camera_path (Sdf.Path): New camera path to track.
        """

        if self.__camera_path != camera_path:
            self.__camera_path = camera_path
            self.__initialize()

    def __initialize(self):
        layer_identifier = self.__usd_context.get_stage_url()
        if self.__camera_path and not omni.client.is_local_url(layer_identifier):
            for event in [
                layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
                layers.LayerEventType.LIVE_SESSION_USER_JOINED,
                layers.LayerEventType.LIVE_SESSION_USER_LEFT,
                pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED,
            ]:
                layers_event_subscription = self.__layers.get_event_stream().create_subscription_to_pop_by_type(
                    event,
                    self.__on_layers_event,
                    name=f"omni.kit.widget.live_session_management.LiveSessionCameraFollowerList {str(event)}",
                )
                self.__layers_event_subscriptions.append(layers_event_subscription)
        else:
            self.__layers_event_subscriptions = []
        self.__build_ui()

    def __build_ui(self):
        # Destroyed
        if not self.__main_layout:
            return

        self.__main_layout.clear()
        self.__all_user_layouts.clear()
        self.__overflow = False
        self.__overflow_button = None

        current_live_session = self.__live_syncing.get_current_live_session()
        if not current_live_session or not self.__camera_path:
            return

        with self.__main_layout:
            for peer_user in current_live_session.peer_users:
                self.__add_user(current_live_session, peer_user.user_id, False)
                if self.__overflow:
                    break

        if self.empty():
            self.__main_layout.visible = False
        else:
            self.__main_layout.visible = True

    def __build_tooltip(self):  # pragma: no cover
        live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
        if not live_session:
            return

        with ui.VStack():
            with ui.HStack(style={"color": ui.color("#757575")}):
                ui.Spacer()
                title_label = ui.Label("Following by 0 Users", style={"font_size": 12}, width=0)
                ui.Spacer()
            ui.Spacer(height=0)
            ui.Separator(style={"color": ui.color("#4f4f4f")})
            ui.Spacer(height=4)

            valid_users = 0
            for user in live_session.peer_users:
                if not self.__show_my_following_users:
                    following_user_id = self.__presence_layer.get_following_user_id(user.user_id)
                    if following_user_id == live_session.logged_user_id:
                        continue

                bound_camera_prim = self.__presence_layer.get_bound_camera_prim(user.user_id)
                if not bound_camera_prim or bound_camera_prim.GetPath() != self.__camera_path:
                    continue

                valid_users += 1
                item_title = f"{user.user_name} ({user.from_app})"
                with ui.HStack():
                    build_live_session_user_layout(user, self.__icon_size, "")
                    ui.Spacer(width=4)
                    ui.Label(item_title, style={"font_size": 14})
                ui.Spacer(height=2)

            title_label.text = f"Following by {valid_users} Users"

    @carb.profiler.profile
    def __add_user(self, current_live_session, user_id, add_child=False):
        bound_camera_prim = self.__presence_layer.get_bound_camera_prim(user_id)
        if not bound_camera_prim:
            return False

        if bound_camera_prim.GetPath() == self.__camera_path:
            user_info = current_live_session.get_peer_user_info(user_id)
            if not user_info:
                return False

            if not self.__show_my_following_users:
                following_user_id = self.__presence_layer.get_following_user_id(user_id)
                if following_user_id == current_live_session.logged_user_id:
                    return False

            if user_id not in self.__all_user_layouts:
                current_count = len(self.__all_user_layouts)
                if current_count > self.__maximum_count or self.__overflow:
                    # OMFP-2909: Refresh overflow button to rebuild tooltip.
                    if self.__overflow and self.__overflow_button:
                        self.__overflow_button.set_tooltip_fn(self.__build_tooltip)

                    return True
                elif current_count == self.__maximum_count:
                    self.__overflow = True
                    layout = ui.HStack(width=0)
                    with layout:
                        ui.Spacer(width=4)
                        with ui.ZStack():
                            ui.Label("...", style={"font_size": 16}, aligment=ui.Alignment.V_CENTER)
                            self.__overflow_button = ui.InvisibleButton(style=TOOLTIP_STYLE)
                            self.__overflow_button.set_tooltip_fn(self.__build_tooltip)

                    if add_child:
                        self.__main_layout.add_child(layout)
                else:
                    if self.empty():
                        spacer = 0
                    else:
                        spacer = self.__spacing
                    layout = self.__build_user_layout(user_info, spacer)
                    if add_child:
                        self.__main_layout.add_child(layout)
                        self.__main_layout.visible = True
                    self.__all_user_layouts[user_id] = layout

            return True

        return False

    @carb.profiler.profile
    def __on_layers_event(self, event):
        payload = layers.get_layer_event_payload(event)
        stage_url = self.__usd_context.get_stage_url()
        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if stage_url not in payload.identifiers_or_spec_paths:
                return

            self.__build_ui()
        elif (
            payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_JOINED
            or payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT
        ):
            if stage_url != payload.layer_identifier:
                return

            current_live_session = self.__live_syncing.get_current_live_session()
            if not current_live_session:
                self.__build_ui()
                return

            user_id = payload.user_id
            if payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT:
                user = self.__all_user_layouts.pop(user_id, None)
                if user:
                    # FIXME: omni.ui does not support to remove single child.
                    self.__build_ui()
            else:
                self.__add_user(current_live_session, user_id, True)
        else:
            current_live_session = self.__live_syncing.get_current_live_session()
            if not current_live_session:
                return

            payload = pl.get_presence_layer_event_payload(event)
            if not payload or not payload.event_type:
                return

            if payload.event_type == pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED:
                changed_user_ids = payload.changed_user_ids
                needs_rebuild = False
                for user_id in changed_user_ids:
                    if not self.__add_user(current_live_session, user_id, True):
                        # It's not bound to this camera already.
                        needs_rebuild = user_id in self.__all_user_layouts
                        break

                if needs_rebuild:
                    self.__build_ui()

    def destroy(self):  # pragma: no cover
        """Destroys the widget and clears internal resources."""
        self.__main_layout = None
        self.__layers_event_subscriptions = []
        self.__layers = None
        self.__live_syncing = None
        self.__all_user_layouts.clear()
        self.__overflow_button = None

    def __build_user_layout(self, user_info: layers.LiveSessionUser, spacing=2):
        tooltip = f"{user_info.user_name} ({user_info.from_app})"
        layout = ui.HStack()
        with layout:
            ui.Spacer(width=spacing)
            build_live_session_user_layout(user_info, self.__icon_size, tooltip)

        return layout
