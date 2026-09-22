import carb
import asyncio
import json
import os
import functools
import uuid
import omni.usd
import omni.client
import omni.kit.usd.layers as layers

from omni.kit.usd.layers._omni_kit_usd_layers import IWorkflowLiveSyncing
from unittest.mock import Mock, MagicMock
from omni.kit.collaboration.channel_manager import MessageType

from pxr import Sdf, Usd


_mocked_live_sessions_per_id = {}
_mocked_live_sessions_ids_per_layer = {}
_mocked_global_live_session_ids_per_prim= {}
_mocked_layer_joined_sessions = {}
_registered_mock_apis = {}
_mock_logged_user_name = "simulated_user_name__"
_mock_logged_user_id = "simulated_user_id__"


def _register(func):
    # Name without prefixed "_"
    name = func.__name__
    name = name.lstrip("_")
    _registered_mock_apis[name] = func

    return func


def _log(func, warn=False):
    message = f"Calling mock function {func.__name__}..."
    if warn:
        carb.log_warn(message)
    else:
        carb.log_info(message)

    return func


class MockedLiveSession:
    def __init__(self, layer_identifier, name) -> None:
        self.session_name = name
        url = omni.client.break_url(layer_identifier)
        file_name_with_ext = os.path.basename(url.path)
        file_name, _ = os.path.splitext(file_name_with_ext)
        self.session_repository_url = omni.client.combine_urls(
            layer_identifier, f".live/{file_name}.live"
        )
        self.url = self.session_repository_url + f"/{name}.live"
        self.channel_url = self.url + "/__session__.channel"
        self.session_config_url = self.url + "/__session__.toml"
        self.live_layer_identifier = self.url + "/root.live"
        self.base_layer_identifier = layer_identifier
        self.id = str(uuid.uuid1().hex)
        self.owner = _mock_logged_user_name
        self.merge_permission = True
        self.live_prims = {}

    def __str__(self):
        return f"{self.name}, {self.url}"


@_register
def _get_live_session_url(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.url if live_session else None


@_register
def _get_live_session_name(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.session_name if live_session else None


@_register
def _get_live_session_root_identifier(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.live_layer_identifier if live_session else None


@_register
def _get_live_session_channel_url(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.channel_url if live_session else None


@_register
def _is_valid_live_session(layers_instance, session_handle):
    return session_handle in _mocked_live_sessions_per_id


@_register
def _get_live_session_base_layer_identifier(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.base_layer_identifier if live_session else None


@_register
def _get_live_session_owner(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.owner if live_session else None


@_register
def _permission_to_merge_session_changes(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)

    return live_session.merge_permission if live_session else False


@_register
def _get_logged_in_user_name_for_layer(layers_instance, layer_identifier):
    return _mock_logged_user_name


@_register
def _get_logged_in_user_id_for_layer(layers_instance, layer_identifier):
    return _mock_logged_user_id


@_register
def _get_live_session_last_modified_time_ns(layers_instance, session_handle):
    return 0


@_register
def _get_total_live_sessions(layers_instance, layer_identifier):
    all_session_ids = _mocked_live_sessions_ids_per_layer.get(layer_identifier, [])

    return len(all_session_ids)


@_register
def _get_live_session_at_index(layers_instance, layer_identifier, index):
    all_session_ids = _mocked_live_sessions_ids_per_layer.get(layer_identifier, [])
    if index >= len(all_session_ids):
        return None

    return all_session_ids[index]


def _send_layer_event(layers_instance, event_type: layers.LayerEventType, payload={}):
    event_stream = layers_instance.get_event_stream()
    if payload:
        event_stream.push(int(event_type), 0, payload=payload)
    else:
        event_stream.push(int(event_type))


@_register
def _find_live_session_by_name(layers_instance, layer_identifier, session_name):
    all_session_ids = _mocked_live_sessions_ids_per_layer.get(layer_identifier, [])
    for session_id in all_session_ids:
        session = _mocked_live_sessions_per_id.get(session_id)
        if session.session_name == session_name:
            return session_id

    return None


@_register
@_log
def _create_live_session(layers_instance, layer_identifier, name):
    if _find_live_session_by_name(layers_instance, layer_identifier, name):
        carb.log_error(f"Cannot create session {name} for layer {layer_identifier} as it exists already.")
        return None

    live_session = MockedLiveSession(layer_identifier, name)
    _mocked_live_sessions_ids_per_layer.setdefault(layer_identifier, [])
    _mocked_live_sessions_ids_per_layer[layer_identifier].append(live_session.id)
    _mocked_live_sessions_per_id[live_session.id] = live_session

    _send_layer_event(
        layers_instance,
        layers.LayerEventType.LIVE_SESSION_LIST_CHANGED,
        {"val": layer_identifier}
    )

    return live_session.id


def _traverse_local_layers_and_find_layer(layer_handle, to_find_layer_handle):
    for index, layer_identifier in enumerate(layer_handle.subLayerPaths):
        absolute_layer_identifier = layer_handle.ComputeAbsolutePath(layer_identifier)
        sublayer_handle = Sdf.Find(absolute_layer_identifier)
        if sublayer_handle == to_find_layer_handle:
            return layer_handle, index

        sublayer_handle, index = _traverse_local_layers_and_find_layer(sublayer_handle, to_find_layer_handle)
        if sublayer_handle:
            return sublayer_handle, index

    return None, -1


def _insert_sublayer_before(stage, to_insert_layer_handle, before_layer_handle):
    if before_layer_handle == stage.GetSessionLayer():
        carb.log_error(f"Failed to insert sublayer before session layer.")
        return

    if before_layer_handle == stage.GetRootLayer():
        stage.GetSessionLayer().subLayerPaths.append(to_insert_layer_handle.identifier)
    else:
        for root_layer in [stage.GetSessionLayer(), stage.GetRootLayer()]:
            parent_layer_handle, index = _traverse_local_layers_and_find_layer(root_layer, before_layer_handle)
            if parent_layer_handle:
                index = 0 if index == 0 else index - 1
                parent_layer_handle.subLayerPaths.insert(index, to_insert_layer_handle.identifier)
                break


def _remove_sublayer(stage, sublayer_identifier):
    sublayer_handle = Sdf.Find(sublayer_identifier)
    if not stage.HasLocalLayer(sublayer_handle):
        return

    for root_layer in [stage.GetSessionLayer(), stage.GetRootLayer()]:
        parent_layer_handle, index = _traverse_local_layers_and_find_layer(root_layer, sublayer_handle)
        if parent_layer_handle:
            del parent_layer_handle.subLayerPaths[index]
            break


@_register
@_log
def _join_live_session(layers_instance, session_handle):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)
    if not live_session:
        carb.log_error("Cannot join a session that does not exist.")
        return False

    if _is_layer_in_live_session(layers_instance, live_session.base_layer_identifier):
        carb.log_error("It must stop current session before joining new session.")
        return False

    live_layer_identifier = live_session.live_layer_identifier
    base_layer_identifier = live_session.base_layer_identifier
    base_layer_handle = Sdf.Find(base_layer_identifier)
    if not base_layer_handle:
        carb.log_error(f"Cannot join live session since base layer cannot be found.")
        return False

    live_layer_handle = Sdf.Find(live_layer_identifier)
    if not live_layer_handle:
        _, ext = os.path.splitext(live_layer_identifier)
        format = Sdf.FileFormat.FindByExtension(ext)
        live_layer_handle = Sdf.Layer.New(format, live_layer_identifier)
        if not live_layer_handle:
            carb.log_error(f"Cannot join live session since mocked live layer cannot be created.")
            return False

    _send_layer_event(
        layers_instance,
        layers.LayerEventType.LIVE_SESSION_JOINING,
        {"val": [live_session.base_layer_identifier]}
    )

    stage = omni.usd.get_context().get_stage()
    _insert_sublayer_before(stage, live_layer_handle, base_layer_handle)
    _mocked_layer_joined_sessions[live_session.base_layer_identifier] = session_handle

    _send_layer_event(
        layers_instance,
        layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
        {"val": [live_session.base_layer_identifier]}
    )

    return True


def _has_ref_or_payload_layer(prim, layer_identifier, reference):
    to_find_layer = Sdf.Find(layer_identifier)
    if not to_find_layer:
        return False

    if reference:
        references_and_layers = omni.usd.get_composed_references_from_prim(prim)
    else:
        references_and_layers = omni.usd.get_composed_payloads_from_prim(prim)

    for ref, intro_layer in references_and_layers:
        layer = Sdf.Find(intro_layer.ComputeAbsolutePath(ref.assetPath)) if ref.assetPath else None
        if layer == to_find_layer:
            return True

    return False


@_register
def _is_prim_in_live_session(layers_instance, prim_path, layer_identifier, from_reference_or_payload_only):
    prim_path = Sdf.Path(prim_path)
    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()
    if stage:
        prim = stage.GetPrimAtPath(prim_path)
    else:
        prim = None

    if not prim:
        return False

    if layer_identifier:
        session_id = _mocked_layer_joined_sessions.get(layer_identifier, None)
        if session_id:
            session = _mocked_live_sessions_per_id.get(session_id, None)
        else:
            session = None

        if not session:
            return False

        if prim_path in session.live_prims:
            if from_reference_or_payload_only:
                return False
            else:
                return True

        in_session = _has_ref_or_payload_layer(prim, session.live_layer_identifier, True)
        if not in_session:
            in_session = _has_ref_or_payload_layer(prim, session.live_layer_identifier, False)

        return in_session
    else:
        if prim_path in _mocked_global_live_session_ids_per_prim.keys():
            if from_reference_or_payload_only:
                return False
            else:
                return True

        references_and_layers = omni.usd.get_composed_references_from_prim(prim)
        for ref, intro_layer in references_and_layers:
            if not ref.assetPath:
                continue

            layer = Sdf.Find(intro_layer.ComputeAbsolutePath(ref.assetPath))
            session_id = _mocked_layer_joined_sessions.get(layer.identifier, None)
            if not session_id:
                continue

            session = _mocked_live_sessions_per_id.get(session_id)
            if not session:
                continue

            if _has_ref_or_payload_layer(prim, session.live_layer_identifier, True):
                return True

        references_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        for ref, intro_layer in references_and_layers:
            if not ref.assetPath:
                continue

            layer = Sdf.Find(intro_layer.ComputeAbsolutePath(ref.assetPath))
            session_id = _mocked_layer_joined_sessions.get(layer.identifier, None)
            if not session_id:
                continue

            session = _mocked_live_sessions_per_id(session_id)
            if not session:
                continue


            if _has_ref_or_payload_layer(prim, session.live_layer_identifier, False):
                return True

    return False


@_register
@_log
def _join_live_session_for_prim(layers_instance, session_handle, prim_path):
    live_session = _mocked_live_sessions_per_id.get(session_handle, None)
    if not live_session:
        carb.log_error("Cannot join a session that does not exist.")
        return False

    prim_path = Sdf.Path(prim_path)
    if prim_path in live_session.live_prims:
        carb.log_error(
            f"It must stop current session for layer {live_session.base_layer_identifier} before joining new session."
        )
        return False

    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()
    if stage:
        prim = stage.GetPrimAtPath(prim_path)
    else:
        prim = None

    if not prim:
        carb.log_error(f"Failed to join the session for prim {prim_path} as prim is not found in the stage.")
        return False

    base_layer_identifier = live_session.base_layer_identifier
    if _is_prim_in_live_session(layers_instance, prim_path, base_layer_identifier, False):
        carb.log_error(f"Failed to join the session for prim {prim_path} as it is in the live session already.")
        return False

    found_reference_or_payload = _has_ref_or_payload_layer(prim, base_layer_identifier, True)
    if not found_reference_or_payload:
        found_reference_or_payload = _has_ref_or_payload_layer(prim, base_layer_identifier, False)
        is_payload = True
    else:
        is_payload = False

    if not found_reference_or_payload:
        carb.log_error(
            f"Failed to join the session for prim {prim_path} as prim does not include reference or payload."
        )

        return False

    live_layer_identifier = live_session.live_layer_identifier
    base_layer_identifier = live_session.base_layer_identifier
    live_layer_handle = Sdf.Find(live_layer_identifier)
    if not live_layer_handle:
        _, ext = os.path.splitext(live_layer_identifier)
        format = Sdf.FileFormat.FindByExtension(ext)
        live_layer_handle = Sdf.Layer.New(format, live_layer_identifier)
        if not live_layer_handle:
            carb.log_error(f"Cannot join live session since mocked live layer cannot be created.")
            return False

    _send_layer_event(
        layers_instance,
        layers.LayerEventType.LIVE_SESSION_JOINING,
        {"val": [base_layer_identifier]}
    )

    live_session.live_prims[prim_path] = is_payload
    _mocked_global_live_session_ids_per_prim.setdefault(prim_path, set())
    _mocked_global_live_session_ids_per_prim[prim_path].add(session_handle)
    prim_spec = Sdf.CreatePrimInLayer(stage.GetSessionLayer(), prim_path)
    if is_payload:
        prim_spec.payloadList.Prepend(Sdf.Payload(live_layer_identifier))
    else:
        prim_spec.referenceList.Prepend(Sdf.Reference(live_layer_identifier))

    _mocked_layer_joined_sessions[live_session.base_layer_identifier] = session_handle

    _send_layer_event(
        layers_instance,
        layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
        {"val": [live_session.base_layer_identifier]}
    )

    return True


@_register
@_log
def _join_live_session_by_url(layers_instance, layer_identifier, live_session_url, create_if_not_existed):
    all_session_ids = _mocked_live_sessions_ids_per_layer.get(layer_identifier, [])
    live_session = None
    for session_id in all_session_ids:
        live_session = _mocked_live_sessions_per_id.get(session_id)
        if live_session.url == live_session_url:
            break

    if not live_session and not create_if_not_existed:
        carb.log_error(f"Cannot join session {live_session_url} since it does not exist.")
        return False
    elif not live_session:
        session_name = os.path.basename(live_session_url)
        session_name, _ = os.path.splitext(session_name)
        session_id = _create_live_session(layers_instance, layer_identifier, session_name)
    else:
        session_id = live_session.id

    return _join_live_session(layers_instance, session_id)


@_register
@_log
def _try_cancelling_live_session_join(layers_instance, layer_identifier):
    raise NotImplemented("try_cancelling_live_session_join is not implemented for mock utils.")


@_register
@_log
def _stop_live_session(layers_instance, layer_identifier, prim_path=None, notify=True):
    session_id = _mocked_layer_joined_sessions.get(layer_identifier, None)
    if not session_id:
        return

    session = _mocked_live_sessions_per_id.get(session_id, None)
    if not session:
        return

    # If prim path is provided, it means to stop live session for this prim only.
    if prim_path:
        if prim_path in session.live_prims:
            all_prim_paths = [prim_path]
            session.live_prims.pop(prim_path)
        else:
            carb.log_error(f"Failed to stop live session for prim {prim_path} as prim is not in any live session.")
            return
    else:
        # Otherwise, stops live sessions for all prims that join the same live session.
        all_prim_paths = list(session.live_prims.keys())
        session.live_prims.clear()

    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()

    if not session.live_prims:
        _mocked_layer_joined_sessions.pop(layer_identifier, None)
        _remove_sublayer(omni.usd.get_context().get_stage(), session.live_layer_identifier)
        stage.SetEditTarget(Usd.EditTarget(stage.GetRootLayer()))

    if all_prim_paths:
        for prim_path in all_prim_paths:
            # TODO: Supports multiple sessions for single prim.
            layers.LayerUtils.remove_prim_spec(stage.GetSessionLayer(), prim_path)
            live_sessions = _mocked_global_live_session_ids_per_prim.get(prim_path, None)
            if live_sessions:
                live_sessions.discard(session_id)

            if not live_sessions:
                _mocked_global_live_session_ids_per_prim.pop(prim_path, None)

    if notify:
        _send_layer_event(
            layers_instance,
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            {"val": [layer_identifier]}
        )


@_register
@_log
def _stop_live_session_for_prim(layers_instance, prim_path, layer_identifier):
    if type(prim_path) is str:
        prim_path = Sdf.Path(prim_path)
    all_base_layers = []
    if layer_identifier:
        _stop_live_session(layers_instance, layer_identifier, prim_path, False)
        all_base_layers.append(layer_identifier)
    else:
        session_ids = list(_mocked_global_live_session_ids_per_prim.get(prim_path, set()))
        for session_id in session_ids:
            session = _mocked_live_sessions_per_id.get(session_id, None)
            if not session:
                continue

            _stop_live_session(layers_instance, session.base_layer_identifier, prim_path, False)
            all_base_layers.append(session.base_layer_identifier)

    if all_base_layers:
        _send_layer_event(
            layers_instance,
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            {"val": all_base_layers}
        )


@_register
@_log
def _stop_all_live_sessions(layers_instance):
    session_ids = list(_mocked_layer_joined_sessions.values())
    all_layer_identifiers = []
    for session_id in session_ids:
        session = _mocked_live_sessions_per_id.get(session_id, None)
        if not session:
            continue

        _stop_live_session(layers_instance, session.base_layer_identifier, notify=False)
        all_layer_identifiers.append(session.base_layer_identifier)

    _mocked_layer_joined_sessions.clear()
    if all_layer_identifiers:
        _send_layer_event(
            layers_instance,
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            {"val": all_layer_identifiers}
        )


@_register
def _is_layer_in_live_session(layers_instance, layer_identifier):
    return _mocked_layer_joined_sessions.get(layer_identifier, None) != None


@_register
def is_layer_in_prim_live_session(layers_instance, layer_identifier):
    session_id = _mocked_layer_joined_sessions.get(layer_identifier, None)
    if not session_id:
        return False

    session = _mocked_live_sessions_per_id.get(session_id, None)
    if not session:
        return False

    return len(session.live_prims) != 0


@_register
def _is_stage_in_live_session(layers_instance):
    stage = omni.usd.get_context().get_stage()
    for layer in stage.GetUsedLayers():
        if _is_layer_in_live_session(layers_instance, layer.identifier):
            return True

    return False


@_register
def _is_live_session_layer(layers_instance, layer_identifier):
    for session_id in _mocked_layer_joined_sessions.values():
        session = _mocked_live_sessions_per_id.get(session_id)
        if session.live_layer_identifier == layer_identifier:
            return True

    return False


@_register
def _get_live_session_for_live_layer(layers_instance, live_layer_identifier):
    for session_id in _mocked_layer_joined_sessions.values():
        session = _mocked_live_sessions_per_id.get(session_id)
        if session.live_layer_identifier == live_layer_identifier:
            return session_id

    return None


@_register
def _get_current_live_session(layers_instance, layer_identifier):
    return _mocked_layer_joined_sessions.get(layer_identifier, None)


@_register
def _get_live_session_prim_paths(layers_instance, session_handle):
    session = _mocked_live_sessions_per_id.get(session_handle, None)

    all_prim_paths = []
    for prim_path in session.live_prims:
        all_prim_paths.append(str(prim_path))

    if all_prim_paths:
        dictionary = carb.dictionary.get_dictionary()
        item = dictionary.create_item(None, "<empty>", carb.dictionary.ItemType.DICTIONARY)
        dictionary.set_string_array(item, all_prim_paths)
    else:
        item = None

    return item


@_register
def _get_live_session_by_url(layers_instance, session_url):
    for session in _mocked_live_sessions_per_id.values():
        if session.url == session_url:
            return session.id

    return None


@_register
@_log
def _merge_live_session_changes(layers_instance, layer_identifier, stop_session):
    _send_layer_event(
        layers_instance,
        layers.LayerEventType.LIVE_SESSION_MERGE_STARTED,
        {"layer_identifier": layer_identifier}
    )

    try:
        live_session = _mocked_layer_joined_sessions.get(layer_identifier, None)
        if not live_session:
            carb.log_error(f"Cannot merge changes since no live session is on for layer {layer_identifier}.")
            return False

        if live_session.merge_permission:
            carb.log_error(f"Cannot merge changes since it has no privilages.")
            return False

    finally:
        _send_layer_event(
            layers_instance,
            layers.LayerEventType.LIVE_SESSION_MERGE_ENDED,
            {"layer_identifier": layer_identifier, "success": True}
        )

        if stop_session:
            _stop_live_session(layers_instance, layer_identifier)

    return True


@_register
@_log
def _merge_live_session_changes_to_specific_layer(layers_instance, layer_identifier,
    target_layer_identifier, stop_session, clear_target_layer
):
    return _merge_live_session_changes(layers_instance, layer_identifier, stop_session)


@_register
@_log
def _open_stage_with_live_session(layers_instance, layer_identifier, session_name, callback):
    usd_context = omni.usd.get_context()
    session_id = _find_live_session_by_name(layers_instance, layer_identifier, session_name)
    if not session_id:
        carb.log_error(f"Cannot join session for layer {layer_identifier} as it does not exist in the current stage.")
        return False

    def _callback(success, err):
        if success:
            success = _join_live_session(layers_instance, session_id)

        if not success:
            err = "ERROR: Live Session Join Failed"

        if callback:
            callback(success, err)

    usd_context.open_stage_with_callback(layer_identifier, _callback)


_native_api_handles = {}
_client_get_server_info_api = None
_client_join_channel_api = None
_client_send_message_api = None
_client_create_checkpoint_api = None
_mock_sdf_create_layer_api = None


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def _start_mock_live_syncing_api(user_name="test", user_id="test"):
    carb.log_info("Start mocking live syncing APIs...")

    global _mock_logged_user_name, _mock_logged_user_id
    _mock_logged_user_name = user_name
    _mock_logged_user_id = user_id

    global _registered_mock_apis
    global _native_api_handles
    for name, f in _registered_mock_apis.items():
        if not hasattr(IWorkflowLiveSyncing, name):
            continue

        _native_api_handle = getattr(IWorkflowLiveSyncing, name)

        # Save it for restore.
        _native_api_handles[name] = _native_api_handle

        mocked_function = _registered_mock_apis.get(name)
        mock = Mock(side_effect=mocked_function)
        setattr(IWorkflowLiveSyncing, name, mock)

    # Mock client channel API for channel manager.
    mock_server_info = Mock(username=user_name, connection_id=user_id)
    global _client_get_server_info_api
    _client_get_server_info_api = omni.client.get_server_info_async
    omni.client.get_server_info_async = AsyncMock(return_value = (omni.client.Result.OK, mock_server_info))

    def __mock_join_channel_with_callback(url, callback):
        callback(omni.client.Result.OK, omni.client.ChannelEvent.JOIN, None, None)

        return Mock(is_finished=lambda: False, id=1000)

    global _client_join_channel_api
    _client_join_channel_api = omni.client.join_channel_with_callback
    omni.client.join_channel_with_callback = Mock(
        side_effect=__mock_join_channel_with_callback
    )

    global _client_send_message_api
    _client_send_message_api = omni.client.send_message_async
    omni.client.send_message_async = AsyncMock(return_value=omni.client.Result.OK)

    global _client_create_checkpoint_api
    _client_create_checkpoint_api = omni.client.create_checkpoint_async
    omni.client.create_checkpoint_async = AsyncMock(return_value=(omni.client.Result.OK, None))

    def __create_new_mock(layer_identifier, **kwargs):
        _, ext = os.path.splitext(layer_identifier)
        format = Sdf.FileFormat.FindByExtension(ext)
        return Sdf.Layer.New(format, layer_identifier, **kwargs)

    # Mock Sdf.Layer creation to avoid creating on-disk layers
    # so it will not depend on real server access.
    # omni.kit.collaboration.presence_layer needs this for
    # stage creation.
    global _mock_sdf_create_layer_api
    _mock_sdf_create_layer_api = Sdf.Layer.CreateNew
    Sdf.Layer.CreateNew = Mock(side_effect=__create_new_mock)


def _end_mock_live_syncing_api():
    """Unmock all APIs"""

    live_syncing = layers.get_live_syncing()
    live_syncing.stop_all_live_sessions()

    global _client_get_server_info_api, _client_join_channel_api, _client_create_checkpoint_api
    global _client_send_message_api, _mock_sdf_create_layer_api
    global _mocked_live_sessions_per_id, _mocked_live_sessions_ids_per_layer
    global _mocked_layer_joined_sessions, _native_api_handles

    for name in _registered_mock_apis.keys():
        setattr(IWorkflowLiveSyncing, name, _native_api_handles.get(name))

    omni.client.get_server_info_async = _client_get_server_info_api
    omni.client.join_channel_with_callback = _client_join_channel_api
    omni.client.send_message_async = _client_send_message_api
    omni.client.create_checkpoint_async = _client_create_checkpoint_api
    Sdf.Layer.CreateNew = _mock_sdf_create_layer_api

    _mocked_live_sessions_per_id.clear()
    _mocked_live_sessions_ids_per_layer.clear()
    _mocked_global_live_session_ids_per_prim.clear()
    _mocked_layer_joined_sessions.clear()
    _native_api_handles.clear()
    _client_get_server_info_api = None
    _client_join_channel_api = None
    _client_send_message_api = None
    _mock_sdf_create_layer_api = None
    _client_create_checkpoint_api = None
    _mock_logged_user_name = "simulated_user_name__"
    _mock_logged_user_id = "simulated_user_id__"

    carb.log_info("Stop mocking live syncing APIs...")

def forbid_session_merge(session):
    live_session = _mocked_live_sessions_per_id.get(session._session_handle, None)
    live_session.merge_permission = False

# Copied from omni.kit.collaboration.channel_manager
KIT_OMNIVERSE_CHANNEL_MESSAGE_HEADER = b'__OVUM__'
KIT_CHANNEL_MESSAGE_VERSION = "3.0"
MESSAGE_VERSION_KEY = "version"
MESSAGE_FROM_USER_NAME_KEY = "from_user_name"
MESSAGE_CONTENT_KEY = "content"
MESSAGE_TYPE_KEY = "message_type"
MESSAGE_APP_KEY = "app"


def _build_message_in_bytes(from_user, app, message_type, content):
    content = {
        MESSAGE_VERSION_KEY: KIT_CHANNEL_MESSAGE_VERSION,
        MESSAGE_TYPE_KEY: message_type,
        MESSAGE_FROM_USER_NAME_KEY: from_user,
        MESSAGE_CONTENT_KEY: content,
        MESSAGE_APP_KEY: app,
    }

    content_bytes = json.dumps(content).encode()
    return KIT_OMNIVERSE_CHANNEL_MESSAGE_HEADER + content_bytes


def join_new_simulated_user(user_name, user_id, app="Kit", layer_identifier=None):
    live_syncing = layers.get_live_syncing()
    current_session = live_syncing.get_current_live_session(layer_identifier)
    if not current_session:
        return

    # Accessing private vars for user join.
    session_channel = current_session._session_channel()
    if not session_channel:
        return

    if not session_channel._channel:
        return

    native_channel = session_channel._channel._handler()
    if not native_channel:
        return

    content = _build_message_in_bytes(user_name, app, MessageType.JOIN, {})
    native_channel._handle_message(omni.client.ChannelEvent.MESSAGE, user_id, content)


def quit_simulated_user(user_id, layer_identifier=None):
    live_syncing = layers.get_live_syncing()
    current_session = live_syncing.get_current_live_session(layer_identifier)
    if not current_session:
        return

    # Accessing private vars for user join.
    session_channel = current_session._session_channel()
    user = session_channel._peer_users.get(user_id, None)
    if not user:
        return

    if not session_channel:
        return

    if not session_channel._channel:
        return

    native_channel = session_channel._channel._handler()
    if not native_channel:
        return

    content = _build_message_in_bytes(user.user_name, user.from_app, MessageType.LEFT, {})
    native_channel._handle_message(omni.client.ChannelEvent.MESSAGE, user_id, content)


def quit_all_simulated_users(layer_identifier=None):
    live_syncing = layers.get_live_syncing()
    current_session = live_syncing.get_current_live_session(layer_identifier)
    if not current_session:
        return

    # Accessing private vars for user join.
    session_channel = current_session._session_channel()
    for user_id in set(session_channel._peer_users.keys()):
        quit_simulated_user(user_id, layer_identifier=layer_identifier)


def is_in_live_session_mocking():
    global _live_session_mocking

    return _live_session_mocking

def MockLiveSyncingApi(*args, **kwargs):
    """Mock live syncing APIs so it will create in-memory live session."""
    user_name = kwargs.get("user_name", "simulated_user_name__")
    user_id = kwargs.get("user_id", "simulated_user_id__")

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        func = args[0]
        args = args[1:]
    else:
        func = None

    def wrapper(func):
        @functools.wraps(func)
        def wrapper_api(*args, **kwargs):
            global _live_session_mocking
            try:
                _live_session_mocking = True
                previous_retry_values = omni.client.set_retries(0, 0, 0)
                _start_mock_live_syncing_api(user_name, user_id)
                return func(*args, **kwargs)
            finally:
                _end_mock_live_syncing_api()
                omni.client.set_retries(*previous_retry_values)
                _live_session_mocking = False

        @functools.wraps(func)
        async def wrapper_api_async(*args, **kwargs):
            global _live_session_mocking
            try:
                _live_session_mocking = True
                previous_retry_values = omni.client.set_retries(0, 0, 0)
                _start_mock_live_syncing_api(user_name, user_id)
                return await func(*args, **kwargs)
            finally:
                _end_mock_live_syncing_api()
                omni.client.set_retries(*previous_retry_values)
                _live_session_mocking = False

        if asyncio.iscoroutinefunction(func):
            return wrapper_api_async
        else:
            return wrapper_api

    if func:
        return wrapper(func)
    else:
        return wrapper
