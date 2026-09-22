import carb
from carb.eventdispatcher import get_eventdispatcher
import omni.usd
import omni.ui as ui
import omni.kit.usd.layers as layers
import omni.kit.widget.live_session_management as lsm

from functools import partial
from omni.kit.menu.utils import MenuItemDescription, MenuAlignment
from omni.ui import color as cl
from typing import Union
from .style import Styles


class LiveStateDelegate(ui.MenuDelegate):
    def __init__(self, layers_interface, **kwargs):
        super().__init__(**kwargs)

        self._layers = layers_interface
        self._live_syncing = layers_interface.get_live_syncing()
        self._usd_context = self._live_syncing.usd_context

        self._live_background = None
        self._drop_down_background = None
        self._live_button = None
        self._drop_down_button = None
        self._live_session_user_list_widget = None

        self._layers_event_subs = []
        for event in [
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            layers.LayerEventType.LIVE_SESSION_USER_JOINED,
            layers.LayerEventType.LIVE_SESSION_USER_LEFT,
        ]:
            layers_event_sub = self._layers.get_event_stream().create_subscription_to_pop_by_type(
                event, self._on_layer_event, name=f"omni.kit.widget.live {str(event)}"
            )
            self._layers_event_subs.append(layers_event_sub)

        self._stage_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.widget.live:live_state_menu",
            event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.OPENED),
            on_event=self._on_stage_opened
        )

    def destroy(self):
        if self._live_button:
            self._live_button.set_clicked_fn(None)
            self._live_button = None

        if self._drop_down_button:
            self._drop_down_button.set_clicked_fn(None)
            self._drop_down_button = None

        if self._live_session_user_list_widget:
            self._live_session_user_list_widget.destroy()
            self._live_session_user_list_widget = None

        self._live_syncing = None
        self._layers_event_subs = []
        self._stage_event_sub = None

    def _on_layer_event(self, event: carb.events.IEvent):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if not payload.is_layer_influenced(self._usd_context.get_stage_url()):
                return

            self.__update_live_state()
        elif (
            payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_JOINED or
            payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT
        ):
            if not payload.is_layer_influenced(self._usd_context.get_stage_url()):
                return

            self.__update_live_tooltip()

    def _on_stage_opened(self, _):
        if self._live_session_user_list_widget:
            self._live_session_user_list_widget.track_layer(self._usd_context.get_stage_url())

    def _on_live_widget_button_clicked(self, button, show_options):
        menu_widget = lsm.stop_or_show_live_session_widget(
            self._live_syncing.usd_context,
            not show_options,
            False,
            show_options
        )

        if not menu_widget:
            return

        # Try to align it with the button.
        drop_down_x = button.screen_position_x
        drop_down_y = button.screen_position_y
        drop_down_height = button.computed_height
        # FIXME: The width of context menu cannot be got. Using fixed width here.
        menu_widget.show_at(
            drop_down_x - 94,
            drop_down_y + drop_down_height + 2
        )

    def build_item(self, item: ui.MenuHelper):
        margin = 2
        with ui.HStack(width=0, style={"margin" : 0}):
            with ui.HStack(content_clipping=1, width=0, style=Styles.LIVE_STATE_ITEM_STYLE):
                with ui.VStack():
                    ui.Spacer(height=margin)
                    self.__build_user_list()
                    ui.Spacer(height=margin)

                ui.Spacer(width=2 * margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    with ui.ZStack(width=0):
                        self._live_background = ui.Rectangle(width=50, name="offline")
                        with ui.HStack(width=50):
                            ui.Spacer()
                            with ui.VStack(width=0):
                                ui.Spacer()
                                ui.Image(width=14, height=14, name="lightning")
                                ui.Spacer()
                            ui.Spacer(width=margin)
                            ui.Label("LIVE", width=0)
                            ui.Spacer()
                        self._live_button = ui.InvisibleButton(width=50, identifier="live_button")
                        self._live_button.set_clicked_fn(
                            partial(self._on_live_widget_button_clicked, self._live_button, False)
                        )
                    ui.Spacer(height=margin)

                ui.Spacer(width=margin)

                with ui.VStack():
                    ui.Spacer(height=margin)
                    with ui.ZStack(width=0):
                        self._drop_down_background = ui.Rectangle(width=16, name="offline")
                        with ui.HStack(width=16):
                            ui.Spacer()
                            with ui.VStack(width=0):
                                ui.Spacer()
                                ui.Image(width=14, height=14, name="arrow_down")
                                ui.Spacer()
                            ui.Spacer()
                        self._drop_down_button = ui.InvisibleButton(width=16, identifier="drop_down_button")
                        self._drop_down_button.set_clicked_fn(
                            partial(self._on_live_widget_button_clicked, self._drop_down_button, True)
                        )
                    ui.Spacer(height=margin)
            ui.Spacer(width=8)

        self.__update_live_state()

    def get_menu_alignment(self):
        return MenuAlignment.RIGHT

    def update_menu_item(self, menu_item: Union[ui.Menu, ui.MenuItem], menu_refresh: bool):
        if isinstance(menu_item, ui.MenuItem):
            menu_item.visible = False

    def __update_live_tooltip(self):
        if not self._live_background:
            return

        current_session = self._live_syncing.get_current_live_session()
        if current_session:
            peer_users_count = len(current_session.peer_users)
            if peer_users_count > 0:
                self._live_background.set_tooltip(
                    f"Leave Session {current_session.name}\n{peer_users_count + 1} Total Users in Session"
                )
            else:
                self._live_background.set_tooltip(
                    f"Leave Session {current_session.name}"
                )

    def __update_live_state(self):
        if self._live_background:
            current_session = self._live_syncing.get_current_live_session()
            if current_session:
                self._live_background.name = "live"
                self.__update_live_tooltip()
                self._drop_down_background.name = "live"
            else:
                self._live_background.name = "offline"
                self._live_background.set_tooltip("Start Session")
                self._drop_down_background.name = "offline"

    def __build_user_list(self):
        def is_follow_enabled():
            settings = carb.settings.get_settings()
            enabled = settings.get(f"/app/liveSession/enableMenuFollowUser")
            if enabled == True or enabled == False:
                return enabled
            return True
        
        stage_url = self._usd_context.get_stage_url()
        self._live_session_user_list_widget = lsm.LiveSessionUserList(
            self._usd_context, stage_url,
            follow_user_with_double_click=is_follow_enabled(),
            allow_timeline_settings=True,
            maximum_users=10
        )


class LiveStateMenu:
    def __init__(self, usd_context):
        self._live_menu_name = "Live State Widget"
        self._menu_list = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]

        self._usd_context = usd_context
        self._layers = layers.get_layers(self._usd_context)
        self._layer_state_delegate = None

    def register_menu_widgets(self):
        self._layer_state_delegate = LiveStateDelegate(self._layers)
        omni.kit.menu.utils.add_menu_items(self._menu_list, name=self._live_menu_name, delegate=self._layer_state_delegate)

    def unregister_menu_widgets(self):
        omni.kit.menu.utils.remove_menu_items(self._menu_list, self._live_menu_name)
        self._menu_list = None

        if self._layer_state_delegate:
            self._layer_state_delegate.destroy()
            self._layer_state_delegate = None
        self._layers = None
        self._usd_context = None
