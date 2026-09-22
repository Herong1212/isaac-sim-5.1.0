# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import carb.eventdispatcher
import omni.kit.app
from .._usd import *
from functools import partial
from typing import Tuple, List, Dict, Any
from pxr import Usd, UsdUtils


# Save new_stage handles as it will be patched below.
__old_new_stage = UsdContext.new_stage
__old_new_stage_with_callback = UsdContext.new_stage_with_callback


def on_stage_result(result: bool, err_msg: str, future: asyncio.Future):
    """Internal callback."""
    if not future.done():
        future.set_result((result, err_msg))


def on_layers_saved_result(result: bool, err_msg: str, saved_layers: List[str], future: asyncio.Future):
    """Internal callback."""

    if not future.done():
        future.set_result((result, err_msg, saved_layers))


async def _next_stage_event_async(self) -> Tuple[StageEventType, Dict[Any, Any]]:
    """Wait for next stage event of omni.usd."""

    order = omni.kit.app.EVENT_ORDER_DEFAULT

    f = asyncio.Future()

    def on_event(e: carb.eventdispatcher.Event):
        if not f.done():
            f.set_result((int(self.stage_event_type(e.event_name)), e.payload))

    # TODO: Narrow this down to just the event(s) that we want to listen for
    subs = [
        carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="omni.usd:_next_stage_event_async",
            event_name=self.stage_event_name(StageEventType(i)),
            on_event=on_event,
            order=order
        )
        for i in range(StageEventType.COUNT)
    ]
    return await f


async def _selection_changed_async(self) -> List[str]:
    """Wait for selection to be changed. Return a list of newly selected paths."""
    f = asyncio.Future()

    def on_event(_):
        if not f.done():
            f.set_result(self.get_selection().get_selected_prim_paths())

    sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
        observer_name="omni.usd:_selection_changed_async",
        event_name=self.stage_event_name(StageEventType.SELECTION_CHANGED),
        on_event=on_event
    )
    return await f


def _new_stage_python_wrapper(self, fn=None, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL):
    """Asynchronous version of :func:`omni.usd.UsdContext.new_stage` that supports to customize load set of new stage."""

    if not fn:
        success = __old_new_stage(self, fn)
        if success and load_set == UsdContextInitialLoadSet.LOAD_NONE:
            self.get_stage().SetLoadRules(Usd.StageLoadRules.LoadNone())
    else:

        def on_new_stage_callback(success, error_message):
            if success and load_set == UsdContextInitialLoadSet.LOAD_NONE:
                self.get_stage().SetLoadRules(Usd.StageLoadRules.LoadNone())

            fn(success, error_message)

        success = __old_new_stage_with_callback(self, on_new_stage_callback)

    return success


def _new_stage_sync(self, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool:
    return _new_stage_python_wrapper(self, None, load_set)


async def _new_stage_async(
    self, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL
) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.new_stage_with_callback`. Creates a new stage with anonymous root layer.

    Args:
        load_set (omni.usd.UsdContextInitialLoadSet): Whether it should open stage with payloads loaded or not. By default, it loads all payloads.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    _new_stage_python_wrapper(self, partial(on_stage_result, future=f), load_set)
    return await f


async def _attach_stage_async(self, stage: Usd.Stage) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.attach_stage_with_callback`. Attaches an opened stage to the context.

    Args:
        stage (pxr.Usd.Stage): The instance of UsdStage.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """
    if not stage:
        return (False, "Failed to attach empty stage.")

    # Inserts stage into cache and passes it as stage id to usd context.
    cache = UsdUtils.StageCache.Get()
    stage_id = cache.Insert(stage).ToLongInt()

    f = asyncio.Future()
    self.attach_stage_with_callback(stage_id, partial(on_stage_result, future=f))
    return await f


async def _open_stage_async(
    self,
    url: str,
    load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL,
    session_layer_url: str = None,
) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.open_stage_with_callback`. Opens a new stage.

    Args:
        url (str): Stage URL to open.
        load_set (omni.usd.UsdContextInitialLoadSet): If it's to open all payloads or none.
        session_layer_url (str): Specified session layer.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    if session_layer_url:
        self.open_stage_with_session_layer(url, session_layer_url, partial(on_stage_result, future=f), load_set)
    else:
        self.open_stage_with_callback(url, partial(on_stage_result, future=f), load_set)

    return await f


async def _reopen_stage_async(
    self, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL
) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.reopen_stage_with_callback`. Re-opens the current stage.

    Args:
        load_set (omni.usd.UsdContextInitialLoadSet): If it's to open all payloads or none.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    self.reopen_stage_with_callback(partial(on_stage_result, future=f), load_set)
    return await f


async def _close_stage_async(self) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.close_stage_with_callback`. Closes the current stage.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    self.close_stage_with_callback(partial(on_stage_result, future=f))
    return await f


async def _save_stage_async(self) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.save_stage_with_callback`. Saves the current stage.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    self.save_stage_with_callback(partial(on_layers_saved_result, future=f))
    return await f


async def _save_as_stage_async(self, url: str) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.save_as_stage_with_callback`. Saves the current stage to a new location.

    Args:
        url (str): New location to save the current stage.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    self.save_as_stage_with_callback(url, partial(on_layers_saved_result, future=f))
    return await f


async def _save_layers_async(self, new_root_layer_path: str, layer_identifiers: List[str]) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.save_layers_with_callback`. Saves specified layers.

    Args:
        new_root_layer_path (str): New location for root layer if it's to save-as the current stage. If it's empty, it will save specified layers only.
        layer_identifiers (List[str]): List of layer identifiers to be saved.

    Returns:
        (bool, str, List[str]): A tuple where the first element tells whether the operation is successful or not, the second one tells the error message if it's faled and
            the third param is the list of layer identifiers that are saved successfully.
    """

    f = asyncio.Future()
    self.save_layers_with_callback(new_root_layer_path, layer_identifiers, partial(on_layers_saved_result, future=f))
    return await f


async def _export_as_stage_async(self, url: str) -> Tuple[bool, str]:
    """
    Asynchronous version of :func:`omni.usd.UsdContext.export_as_stage_with_callback`. Flattens and exports the current stage.

    Returns:
        (bool, str): A tuple where the first element tells whether the operation is successful or not, and
            the second one tells the error message if the operation is failed.
    """

    f = asyncio.Future()
    self.export_as_stage_with_callback(url, partial(on_stage_result, future=f))
    return await f


async def _load_mdl_parameters_for_prim_async(self, prim, recreate: bool = False):
    omni.kit.app.log_deprecation("load_mdl_parameters_for_prim_async: This function has been deprecated, shader parameters can be queried using a combination of the UsdShade and SDR API's.")

UsdContext.next_stage_event_async = _next_stage_event_async
UsdContext.selection_changed_async = _selection_changed_async
UsdContext.new_stage_async = _new_stage_async
UsdContext.open_stage_async = _open_stage_async
UsdContext.attach_stage_async = _attach_stage_async
UsdContext.reopen_stage_async = _reopen_stage_async
UsdContext.close_stage_async = _close_stage_async
UsdContext.save_stage_async = _save_stage_async
UsdContext.save_as_stage_async = _save_as_stage_async
UsdContext.save_layers_async = _save_layers_async
UsdContext.export_as_stage_async = _export_as_stage_async
UsdContext.load_mdl_parameters_for_prim_async = _load_mdl_parameters_for_prim_async

# Patch new_stage and new_stage_with_callback to support loadset param.
# This is only done in python currently without touching UsdContext in cpp
# for ABI safety.
UsdContext.new_stage = _new_stage_sync
UsdContext.new_stage_with_callback = _new_stage_python_wrapper
