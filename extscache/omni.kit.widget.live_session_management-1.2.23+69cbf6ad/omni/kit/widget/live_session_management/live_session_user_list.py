# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LiveSessionUserList"]


import carb
import omni.kit.collaboration.presence_layer as pl
import omni.kit.usd.layers as layers
import omni.ui as ui
import omni.usd

from .utils import build_live_session_user_layout, is_extension_loaded


TOOLTIP_STYLE = {"color": ui.color("#979797"), "Tooltip": {"background_color": 0xEE222222}}

PRESENTER_STYLE = {"background_color": 0xFF2032DC}  # blue alternative: 0xffff851a


class LiveSessionUserList:
    """Widget to build a user list to show all live session users of the interested layer.

    Args:
        usd_context (omni.usd.UsdContext): USD Context instance.
        base_layer_identifier (str): Interested layer to listen to.

    Keyword Args:
        icon_size (int): The width and height of the user icon. 16 pixel by default.
        spacing (int): The horizontal spacing between two icons. 2 pixel by default.
        show_myself (bool): Whether to show local user or not. True by default.
        show_myself_to_leftmost (bool): Whether to show local user to the leftmost, or rightmost otherwise. True by default.
        maximum_users (int): The maximum users to show, and show others with overflow. Unlimited by default.
        prim_path (Sdf.Path): Track Live Session for this prim only.
        allow_timeline_settings (bool): Whether to allow timeline settings. False by default.
    """

    def __init__(self, usd_context: omni.usd.UsdContext, base_layer_identifier: str, **kwargs):
        """Initializes the LiveSessionUserList widget."""

        self.__icon_size = kwargs.get("icon_size", 16)
        self.__spacing = kwargs.get("spacing", 2)
        self.__show_myself = kwargs.get("show_myself", True)
        self.__show_myself_to_leftmost = kwargs.get("show_myself_to_leftmost", True)
        self.__maximum_count = kwargs.get("maximum_users", None)
        self.__follow_user_with_double_click = kwargs.get("follow_user_with_double_click", False)
        timeline_ext_loaded = is_extension_loaded("omni.timeline.live_session")
        self.__allow_timeline_settings = kwargs.get("allow_timeline_settings", False) and timeline_ext_loaded
        self.__prim_path = kwargs.get("prim_path", None)
        self.__base_layer_identifier = base_layer_identifier
        self.__usd_context = usd_context
        self.__layers = layers.get_layers(usd_context)
        self.__live_syncing = layers.get_live_syncing()
        self.__layers_event_subscriptions = []
        self.__main_layout: ui.HStack = ui.HStack(width=0, height=0)
        self.__all_user_layouts = {}
        self.__overflow = None
        self.__overflow_button = None
        self.__initialize()

    @property
    def layout(self) -> ui.HStack:
        """Gets the root widget of the list.

        Returns:
            ui.HStack: The root layout widget.
        """

        return self.__main_layout

    def track_layer(self, layer_identifier):
        """Switches the base layer to listen to.

        Args:
            layer_identifier (str): Identifier of layer to update.
        """

        if self.__base_layer_identifier != layer_identifier:
            self.__base_layer_identifier = layer_identifier
            self.__initialize()

    def empty(self):
        """Checks if any user icons have been added.

        Returns:
            bool: True if the user list is empty, False otherwise.
        """

        return len(self.__all_user_layouts) == 0

    def __initialize(self):
        if not omni.client.is_local_url(self.__base_layer_identifier):
            for event in [
                layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
                layers.LayerEventType.LIVE_SESSION_USER_JOINED,
                layers.LayerEventType.LIVE_SESSION_USER_LEFT,
            ]:
                layers_event_subscription = self.__layers.get_event_stream().create_subscription_to_pop_by_type(
                    event,
                    self.__on_layers_event,
                    name=f"omni.kit.widget.live_session_management.LiveSessionUserList {str(event)}",
                )
                self.__layers_event_subscriptions.append(layers_event_subscription)
        else:
            self.__layers_event_subscriptions = []
        self.__build_ui()

    def __is_in_session(self):
        if self.__prim_path:
            return self.__live_syncing.is_prim_in_live_session(self.__prim_path, self.__base_layer_identifier)
        else:
            return self.__live_syncing.is_layer_in_live_session(self.__base_layer_identifier)

    def __build_myself(self):
        current_live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
        if not current_live_session:
            return

        logged_user = current_live_session.logged_user
        with ui.ZStack(width=0, height=0):
            with ui.HStack():
                ui.Spacer()
                self.__build_user_layout_or_overflow(current_live_session, logged_user, True, spacing=0)
                ui.Spacer()

            if self.__is_presenting(logged_user):
                with ui.VStack():
                    ui.Spacer()
                    with ui.HStack(height=2, width=24):
                        ui.Rectangle(
                            height=2, width=12, alignment=ui.Alignment.BOTTOM, style={"background_color": 0xFF00B86B}
                        )
                        ui.Rectangle(height=2, width=12, alignment=ui.Alignment.BOTTOM, style=PRESENTER_STYLE)
            else:
                with ui.VStack():
                    ui.Spacer()
                    ui.Rectangle(
                        height=2, width=24, alignment=ui.Alignment.BOTTOM, style={"background_color": 0xFF00B86B}
                    )

    def __build_ui(self):
        # Destroyed
        if not self.__main_layout:
            return

        self.__overflow = False
        self.__main_layout.clear()
        self.__all_user_layouts.clear()
        self.__overflow_button = None

        if not self.__is_in_session():
            return

        current_live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
        with self.__main_layout:
            if self.__show_myself and self.__show_myself_to_leftmost:
                self.__build_myself()

            if current_live_session:
                for peer_user in current_live_session.peer_users:
                    self.__build_user_layout_or_overflow(current_live_session, peer_user, False, self.__spacing)
                    if self.__overflow:
                        break

            if self.__show_myself and not self.__show_myself_to_leftmost:
                ui.Spacer(self.__spacing)
                self.__build_myself()

        if self.empty():
            self.__main_layout.visible = False
        else:
            self.__main_layout.visible = True

    @carb.profiler.profile
    def __on_layers_event(self, event):
        payload = layers.get_layer_event_payload(event)
        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if not payload.is_layer_influenced(self.__base_layer_identifier):
                return

            if self.__allow_timeline_settings:
                import omni.timeline.live_session

                timeline_session = omni.timeline.live_session.get_timeline_session()
                if timeline_session is not None:
                    timeline_session.add_presenter_changed_fn(self.__on_presenter_changed)

            self.__build_ui()
        elif (
            payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_JOINED
            or payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT
        ):
            if not payload.is_layer_influenced(self.__base_layer_identifier):
                return

            if not self.__is_in_session():
                return

            current_live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
            user_id = payload.user_id

            if payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT:
                self.__all_user_layouts.pop(user_id, None)
                # FIXME: omni.ui does not support to remove single child.
                self.__build_ui()
            else:
                if user_id in self.__all_user_layouts or self.__overflow:
                    # OMFP-2909: Refresh overflow button to rebuild tooltip.
                    if self.__overflow and self.__overflow_button:
                        self.__overflow_button.set_tooltip_fn(self.__build_tooltip)
                    return

                user_info = current_live_session.get_peer_user_info(user_id)
                if not user_info:
                    return

                self.__main_layout.add_child(
                    self.__build_user_layout_or_overflow(current_live_session, user_info, False, self.__spacing)
                )

    def destroy(self):  # pragma: no cover
        """Destroys the LiveSessionUserList widget and clears all references, subscriptions, and layouts."""
        self.__overflow_button = None
        self.__main_layout = None
        self.__layers_event_subscriptions = []
        self.__layers = None
        self.__live_syncing = None
        self.__user_menu = None
        self.__all_user_layouts.clear()

    def __on_follow_user(self, x: float, y: float, button: int, modifier, user_info: layers.LiveSessionUser):
        if button != int(carb.input.MouseInput.LEFT_BUTTON):  # only left MB click
            return

        current_live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
        if not current_live_session or current_live_session.logged_user_id == user_info.user_id:
            return

        presence_layer = pl.get_presence_layer_interface(self.__usd_context)
        if presence_layer:
            presence_layer.enter_follow_mode(user_info.user_id)

    def __on_mouse_clicked(self, x: float, y: float, button: int, modifier, user_info: layers.LiveSessionUser):
        if button == int(carb.input.MouseInput.RIGHT_BUTTON):  # right click to open menu
            import omni.timeline.live_session

            timeline_session = omni.timeline.live_session.get_timeline_session()
            if timeline_session is not None and timeline_session.am_i_owner():
                self.__user_menu = ui.Menu("global_live_timeline_user")
                show = False
                with self.__user_menu:
                    if timeline_session.is_presenter(user_info) and not timeline_session.is_owner(user_info):
                        ui.MenuItem(
                            "Withdraw Timeline Presenter",
                            triggered_fn=lambda *args: self.__set_presenter(timeline_session, timeline_session.owner),
                        )
                        show = True
                    elif not timeline_session.is_presenter(user_info):
                        ui.MenuItem(
                            "Set as Timeline Presenter",
                            triggered_fn=lambda *args: self.__set_presenter(timeline_session, user_info),
                        )
                        show = True
                if show:
                    self.__user_menu.show()

    def __set_presenter(self, timeline_session, user_info: layers.LiveSessionUser):
        timeline_session.presenter = user_info

    def __is_presenting(self, user_info: layers.LiveSessionUser) -> bool:
        if not self.__allow_timeline_settings:
            return False
        timeline_session = omni.timeline.live_session.get_timeline_session()
        return timeline_session.is_presenter(user_info) if timeline_session is not None else False

    def __on_presenter_changed(self, _):
        self.__build_ui()

    def __build_user_layout(
        self, live_session: layers.LiveSession, user_info: layers.LiveSessionUser, me: bool, spacing=2
    ):
        if me:
            tooltip = f"{user_info.user_name} - Me"
            if live_session.merge_permission:
                tooltip += " (owner)"
        else:
            tooltip = f"{user_info.user_name} ({user_info.from_app})"
            if not live_session.merge_permission and live_session.owner == user_info.user_name:
                tooltip += " - owner"

        layout = ui.ZStack(width=0, height=0)
        with layout:
            with ui.HStack():
                ui.Spacer(width=spacing)
                user_layout = build_live_session_user_layout(
                    user_info,
                    self.__icon_size,
                    tooltip,
                    self.__on_follow_user if self.__follow_user_with_double_click else None,
                    self.__on_mouse_clicked if self.__allow_timeline_settings else None,
                )
            user_layout.set_style(TOOLTIP_STYLE)
            current_live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
            logged_user = current_live_session.logged_user
            if logged_user.user_id != user_info.user_id and self.__is_presenting(user_info):
                with ui.VStack():
                    ui.Spacer()
                    ui.Rectangle(height=2, width=24, alignment=ui.Alignment.BOTTOM, style=PRESENTER_STYLE)

        return layout

    def __build_tooltip(self):  # pragma: no cover
        live_session = self.__live_syncing.get_current_live_session(self.__base_layer_identifier)
        if not live_session:
            return

        total_users = len(live_session.peer_users)
        if self.__show_myself:
            total_users += 1

        with ui.VStack():
            with ui.HStack(style={"color": ui.color("#757575")}):
                ui.Spacer()
                ui.Label(f"{total_users} Users Connected", style={"font_size": 12})
                ui.Spacer()
            ui.Spacer(height=0)
            ui.Separator(style={"color": ui.color("#4f4f4f")})
            ui.Spacer(height=4)

            all_users = []
            if self.__show_myself:
                all_users = [live_session.logged_user]
            all_users.extend(live_session.peer_users)

            for user in all_users:
                item_title = f"{user.user_name} ({user.from_app})"
                if live_session.owner == user.user_name:
                    item_title += " - owner"
                with ui.HStack():
                    build_live_session_user_layout(
                        user,
                        self.__icon_size,
                        "",
                        self.__on_follow_user if self.__follow_user_with_double_click else None,
                        self.__on_mouse_clicked if self.__allow_timeline_settings else None,
                    )
                    ui.Spacer(width=4)
                    ui.Label(item_title, style={"font_size": 14})
                ui.Spacer(height=2)

    @carb.profiler.profile
    def __build_user_layout_or_overflow(
        self, live_session: layers.LiveSession, user_info: layers.LiveSessionUser, me: bool, spacing=2
    ):  # pragma: no cover
        current_count = len(self.__all_user_layouts)
        if self.__overflow:
            return None

        if self.__maximum_count is not None and current_count >= self.__maximum_count:
            layout = ui.HStack(width=0)
            with layout:
                ui.Spacer(width=4)
                with ui.ZStack():
                    ui.Label("...", style={"font_size": 16}, aligment=ui.Alignment.V_CENTER)
                    self.__overflow_button = ui.InvisibleButton(style=TOOLTIP_STYLE)

            self.__overflow_button.set_tooltip_fn(self.__build_tooltip)
            self.__overflow = True
        else:
            layout = self.__build_user_layout(live_session, user_info, me, spacing)
            self.__all_user_layouts[user_info.user_id] = layout
            self.__main_layout.visible = True
            self.__overflow_button = None

        return layout
