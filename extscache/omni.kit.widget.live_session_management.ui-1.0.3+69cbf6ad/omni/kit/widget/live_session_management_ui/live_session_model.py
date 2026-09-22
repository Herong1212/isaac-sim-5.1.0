# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LiveSessionComboBoxItem", "LiveSessionComboBoxModel"]

import asyncio
from typing import Callable, List

import omni.ui as ui

from .live_session import LiveSessionInterface


class LiveSessionComboBoxItem(ui.AbstractItem):
    def __init__(self, session: LiveSessionInterface) -> None:
        super().__init__()
        self._session = session
        self.model = ui.SimpleStringModel(session.name)

    @property
    def session(self):
        return self._session

    def __str__(self) -> str:
        return self._session.name


class LiveSessionComboBoxModel(ui.AbstractItemModel):
    _last_sessions = {}

    def __init__(self, layer_identifier:str, get_current_live_session_cb: Callable[[str], LiveSessionInterface],
                 get_all_live_sessions_cb: Callable[[str], List[LiveSessionInterface]], update_users: bool=True) -> None:
        super().__init__()
        self._base_layer_identifier = layer_identifier
        self._get_current_live_session_cb = get_current_live_session_cb
        self._get_all_live_sessions_cb = get_all_live_sessions_cb
        self._current_index = ui.SimpleIntModel()
        self._current_index.set_value(-1)
        id = self._current_index.add_value_changed_fn(self._value_changed_fn)
        self._items = []
        self._current_session = None
        self._current_session_channel = None
        self._channel_subscriber = None
        self._join_channel_task = None
        self._all_users = {}
        self._user_update_callback: Callable[[], None] = None
        self._all_value_changed_fns = [id]
        self._update_users = update_users
        self._refreshing_item = False
        self._is_default_session_selected = False
        self._model_reset_callback = None

    def __del__(self):
        self.destroy()

    @property
    def base_layer_identifier(self):
        return self._base_layer_identifier

    @property
    def all_users(self):
        return self._all_users

    @property
    def is_default_session_selected(self):
        return self._is_default_session_selected

    def set_user_update_callback(self, callback: Callable[[], None]):
        self._user_update_callback = callback

    def set_model_reset_callback(self, callback: Callable[[], None]):
        self._model_reset_callback = callback

    def stop_channel(self):
        self._cancel_current_task()

    def _join_current_channel(self):
        if not self._current_session or not self._update_users:
            return

        try:
            # OM-108516: Make channel_manager optional
            import omni.kit.collaboration.channel_manager as cm
        except ImportError:
            return

        if not self._current_session_channel or self._current_session_channel.url != self._current_session.url:
            self._cancel_current_task()

            async def join_stage_async(url):
                self._current_session_channel = await cm.join_channel_async(url, True)
                if not self._current_session_channel:
                    return

                self._channel_subscriber = self._current_session_channel.add_subscriber(self._on_channel_message)
            self._join_channel_task = asyncio.ensure_future(join_stage_async(self._current_session.channel_url))

    def _on_channel_message(self, message):
        try:
            # OM-108516: Make channel_manager optional
            import omni.kit.collaboration.channel_manager as cm
        except ImportError:
            return

        user = message.from_user
        if message.message_type == cm.MessageType.LEFT and user.user_id in self._all_users:
            self._all_users.pop(user.user_id, None)
            changed = True
        elif user.user_id not in self._all_users:
            self._all_users[user.user_id] = user
            changed = True
        else:
            changed = False

        if changed and self._user_update_callback:
            self._user_update_callback()

    def _cancel_current_task(self):
        if self._join_channel_task and not self._join_channel_task.done():
            try:
                self._join_channel_task.cancel()
            except Exception:
                pass

        if self._current_session_channel:
            self._current_session_channel.stop()
        self._current_session_channel = None
        self._join_channel_task = None
        self._channel_subscriber = None

    def add_value_changed(self, fn):
        if self._current_index:
            id = self._current_index.add_value_changed_fn(fn)
            self._all_value_changed_fns.append(id)

    def _value_changed_fn(self, model):
        if self._refreshing_item:
            return

        index = self._current_index.as_int
        if index < 0 or index >= len(self._items):
            return

        self._current_session = self._items[index].session
        self._is_default_session_selected = (self._current_session and self._current_index.as_int == 0)
        self._last_sessions[self._base_layer_identifier] = self._current_session.url
        self._all_users.clear()

        if self._user_update_callback:
            self._user_update_callback()

        self._join_current_channel()

        self._refreshing_item = True
        self._item_changed(None)
        self._refreshing_item = False

    def destroy(self):
        self._user_update_callback = None
        self._cancel_current_task()
        if self._current_index:
            for fn in self._all_value_changed_fns:
                self._current_index.remove_value_changed_fn(fn)
            self._all_value_changed_fns.clear()
        self._current_index = None
        self._current_session = None
        self._items = []
        self._all_users = {}

    def clear(self):
        self._items = []
        self._current_session = None
        self._current_index.set_value(-1)
        if self._model_reset_callback:
            self._model_reset_callback()

    def empty(self):
        return len(self._items) == 0

    def get_item_children(self, item):
        return self._items

    @property
    def current_session(self):
        return self._current_session

    def refresh_sessions(self, force=False):
        current_live_session = self._get_current_live_session_cb(self._base_layer_identifier)
        live_sessions = self._get_all_live_sessions_cb(self._base_layer_identifier)
        live_sessions.sort(key=lambda s: s.get_last_modified_time(), reverse=True)
        identifier = self._base_layer_identifier
        pre_sort = []
        for session in live_sessions:
            if session.name == "Default":
                pre_sort.insert(0, session)
            else:
                pre_sort.append(session)

        self._items.clear()
        index = 0 if live_sessions else -1
        current_live_session_index = -1
        last_live_session_index = -1
        for i, session in enumerate(pre_sort):
            item = LiveSessionComboBoxItem(session)
            if current_live_session and current_live_session.url == session.url:
                current_live_session_index = i
            elif identifier in self._last_sessions and self._last_sessions[identifier] == session.url:
                last_live_session_index = i

            self._items.append(item)

        if current_live_session_index >= 0:
            index = current_live_session_index
        elif last_live_session_index >= 0:
            index = last_live_session_index

        current_index = self._current_index.as_int
        if current_index != index:
            self._current_index.set_value(index)
        elif force:
            self._item_changed(None)

        self._is_default_session_selected = (self._current_session and self._current_index.as_int == 0)
        if self._model_reset_callback:
            self._model_reset_callback()

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index

        return item.model

    def select_default_session(self):
        live_sessions = self._get_all_live_sessions_cb(self._base_layer_identifier)
        if live_sessions and self._current_index.as_int != 0:
            self._current_index.set_value(0)
            self._item_changed(None)
        return

    def create_new_session_name(self) -> str:
        """Empty by default"""

        return ""
