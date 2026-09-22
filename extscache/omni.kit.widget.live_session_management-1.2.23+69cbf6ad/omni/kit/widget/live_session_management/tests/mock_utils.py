import carb
import asyncio
import os
import functools
import uuid
import omni.usd
import omni.client
import omni.kit.usd.layers as layers
from typing import Callable, Awaitable
from omni.kit.collaboration.channel_manager.types import PeerUser
from omni.kit.usd.layers import LayersState, LiveSyncing, LiveSession
from omni.kit.widget.live_session_management_ui.file_picker import FilePicker
from ..live_session_model import LiveSessionModel

from omni.kit.usd.layers._omni_kit_usd_layers import IWorkflowLiveSyncing
from unittest.mock import Mock, MagicMock

from pxr import Sdf, Usd

_mock_sdf_save_layer_api = None
_mock_layer_states_get_all_outdated_layer_identifiers_api = None
_mock_live_session_model_all_users_api = None
_mock_live_syncing_merge_and_stop_live_session_async_api = None
_mock_filepicker_show_api = None
_mock_filepicker_set_file_selected_fn_api = None
_mock_outdated_layers = []
file_save_handler = None
merge_and_stop_live_session_async_called = False

def append_outdated_layers(layer_id):
    global _mock_outdated_layers
    _mock_outdated_layers.append(layer_id)

def clear_outdated_layers():
    global _mock_outdated_layers
    _mock_outdated_layers = []

def get_merge_and_stop_live_session_async_called():
    global merge_and_stop_live_session_async_called
    return merge_and_stop_live_session_async_called

def _start_mock_api_for_live_session_management():
    carb.log_info("Start mock api for live session management...")

    def __mock_sdf_save_layer(force):
        pass
    global _mock_sdf_save_layer_api
    _mock_sdf_save_layer_api = Sdf.Layer.Save
    Sdf.Layer.Save = Mock(side_effect=__mock_sdf_save_layer)

    def __mock_layer_states_get_all_outdated_layer_identifiers_():
        global _mock_outdated_layers
        return _mock_outdated_layers

    global _mock_layer_states_get_all_outdated_layer_identifiers_api
    _mock_layer_states_get_all_outdated_layer_identifiers_api = LayersState.get_all_outdated_layer_identifiers
    LayersState.get_all_outdated_layer_identifiers = Mock(side_effect=__mock_layer_states_get_all_outdated_layer_identifiers_)

    global _mock_live_session_model_all_users_api
    _mock_live_session_model_all_users_api = LiveSessionModel.all_users
    LiveSessionModel.all_users = {f"user_{i}": PeerUser(f"user_{i}", f"user_{i}", "Kit") for i in range(3)}

    async def __mock_live_syncing_merge_and_stop_live_session_async(
        self, target_layer: str = None, comment="",
        pre_merge: Callable[[LiveSession], Awaitable] = None,
        post_merge: Callable[[bool], Awaitable] = None,
        layer_identifier: str = None
    ) -> bool:
        global merge_and_stop_live_session_async_called
        merge_and_stop_live_session_async_called = True
        return True

    global _mock_live_syncing_merge_and_stop_live_session_async_api
    _mock_live_syncing_merge_and_stop_live_session_async_api = LiveSyncing.merge_and_stop_live_session_async
    LiveSyncing.merge_and_stop_live_session_async = Mock(side_effect=__mock_live_syncing_merge_and_stop_live_session_async)

    def __mock_filepicker_show(dummy1, dummy2):
        global file_save_handler
        if file_save_handler:
            file_save_handler(dummy1, False)

    global _mock_filepicker_show_api
    _mock_filepicker_show_api = FilePicker.show
    FilePicker.show = Mock(side_effect=__mock_filepicker_show)

    def __mock_filepicker_set_file_selected_fn(fn):
        global file_save_handler
        file_save_handler = fn

    global _mock_filepicker_set_file_selected_fn_api
    _mock_filepicker_set_file_selected_fn_api = FilePicker.set_file_selected_fn
    FilePicker.set_file_selected_fn = Mock(side_effect=__mock_filepicker_set_file_selected_fn)

def _end_mock_api_for_live_session_management():
    carb.log_info("Start mock api for live session management...")
    global _mock_sdf_save_layer_api
    Sdf.Layer.Save = _mock_sdf_save_layer_api
    _mock_sdf_save_layer_api = None

    global _mock_layer_states_get_all_outdated_layer_identifiers_api
    LayersState.get_all_outdated_layer_identifiers = _mock_layer_states_get_all_outdated_layer_identifiers_api
    _mock_layer_states_get_all_outdated_layer_identifiers_api = None

    global _mock_live_session_model_all_users_api
    LiveSessionModel.all_users = _mock_live_session_model_all_users_api
    _mock_live_session_model_all_users_api = None

    global _mock_live_syncing_merge_and_stop_live_session_async_api
    LiveSyncing.merge_and_stop_live_session_async = _mock_live_syncing_merge_and_stop_live_session_async_api
    _mock_live_syncing_merge_and_stop_live_session_async_api = None

    global _mock_filepicker_show_api
    FilePicker.show = _mock_filepicker_show_api
    _mock_filepicker_show_api = None

    global _mock_filepicker_set_file_selected_fn_api
    FilePicker.set_file_selected_fn = _mock_filepicker_set_file_selected_fn_api
    _mock_filepicker_set_file_selected_fn_api = None

    global merge_and_stop_live_session_async_called
    merge_and_stop_live_session_async_called = False

def MockApiForLiveSessionManagement(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        func = args[0]
        args = args[1:]
    else:
        func = None

    def wrapper(func):
        @functools.wraps(func)
        def wrapper_api(*args, **kwargs):
            try:
                _start_mock_api_for_live_session_management()
                return func(*args, **kwargs)
            finally:
                _end_mock_api_for_live_session_management()

        @functools.wraps(func)
        async def wrapper_api_async(*args, **kwargs):
            try:
                _start_mock_api_for_live_session_management()
                return await func(*args, **kwargs)
            finally:
                _end_mock_api_for_live_session_management()

        if asyncio.iscoroutinefunction(func):
            return wrapper_api_async
        else:
            return wrapper_api

    if func:
        return wrapper(func)
    else:
        return wrapper
