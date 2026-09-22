from typing import Optional

import carb.events
import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.playlist.core import PlaylistModel, get_play_manager

WAYPOIONT_PLAY_NEXT_EVENT: int = carb.events.type_from_string("waypoint.playlist.NEXT")
WAYPOIONT_PLAY_PREVIOUS_EVENT: int = carb.events.type_from_string("waypoint.playlist.PREVIOUS")
WAYPOIONT_PLAY_PLAY_EVENT: int = carb.events.type_from_string("waypoint.playlist.PLAY")
WAYPOIONT_PLAY_STOP_EVENT: int = carb.events.type_from_string("waypoint.playlist.STOP")

SETTING_PLAY_NEXT_ENABLED = "/app/waypoint/playlist/next/enabled"
SETTING_PLAY_PREVIOUS_ENABLED = "/app/waypoint/playlist/previous/enabled"
SETTING_PLAY_PLAY_ENABLED = "/app/waypoint/playlist/play/enabled"
SETTING_PLAY_PLAYING = "/app/waypoint/playlist/playing"
SETTING_PLAYLIST_ACTIVE = "/exts/omni.kit.tool.camera_playlist/active"


class PlayControl:
    def __init__(self, playlist_model: PlaylistModel):
        self._playlist_model = playlist_model
        self.__play_manager = get_play_manager()

        self._settings = carb.settings.get_settings()
        self._active_playlist_sub = self.__play_manager.subscribe_playing_playlist_changed(
            self.__on_playing_status_changed
        )

        event_stream = omni.kit.app.get_app().get_message_bus_event_stream()
        self._play_next_event_sub = event_stream.create_subscription_to_pop_by_type(
            WAYPOIONT_PLAY_NEXT_EVENT, lambda e: self.__on_next()
        )
        self._play_previous_event_sub = event_stream.create_subscription_to_pop_by_type(
            WAYPOIONT_PLAY_PREVIOUS_EVENT, lambda e: self.__on_previous()
        )
        self._play_play_event_sub = event_stream.create_subscription_to_pop_by_type(
            WAYPOIONT_PLAY_PLAY_EVENT, lambda e: self.__start_play()
        )
        self._play_stop_event_sub = event_stream.create_subscription_to_pop_by_type(
            WAYPOIONT_PLAY_STOP_EVENT, lambda e: self.__stop_play()
        )

    def destroy(self):
        self._active_playlist_sub = None

        self._play_next_event_sub = None
        self._play_previous_event_sub = None
        self._play_play_event_sub = None
        self._play_stop_event_sub = None

    def __on_next(self):
        if self.__play_manager.is_playing:
            carb.log_warn(f"Alreay playing '{self.__play_manager.current_playlist.name}'")
            return
        self.__play_manager.current_playlist = self._playlist_model
        self.__play_manager.next()

    def __on_previous(self):
        if self.__play_manager.is_playing:
            carb.log_warn(f"Alreay playing '{self.__play_manager.current_playlist.name}'")
            return
        self.__play_manager.current_playlist = self._playlist_model
        self.__play_manager.previous()

    def __start_play(self):
        if self.__play_manager.is_playing:
            carb.log_warn(f"Alreay playing '{self.__play_manager.current_playlist.name}'")
            return
        self.__play_manager.current_playlist = self._playlist_model
        self.__play_manager.play()

    def __stop_play(self):
        self.__play_manager.stop()

    def __on_playing_status_changed(self, name: str):
        playing = name != ""
        self._settings.set(SETTING_PLAY_NEXT_ENABLED, not playing)
        self._settings.set(SETTING_PLAY_PREVIOUS_ENABLED, not playing)

        playing_waypoint = name == self._playlist_model.name
        self._settings.set(SETTING_PLAY_PLAY_ENABLED, not playing or playing_waypoint)
        self._settings.set(SETTING_PLAY_PLAYING, playing_waypoint)
