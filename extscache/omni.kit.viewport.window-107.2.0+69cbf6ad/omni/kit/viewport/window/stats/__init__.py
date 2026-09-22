# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportStatsLayer']

import omni.ui as ui
from omni.ui import constant as fl
from omni.gpu_foundation_factory import get_memory_info
import carb
from carb.eventdispatcher import get_eventdispatcher, Event
import traceback
import time
from typing import Callable, List, Optional, Sequence
import weakref

from ..events.delegate import _limit_camera_velocity

LOW_MEMORY_SETTING_PATH = '/persistent/app/viewport/memory/lowFraction'
MEMORY_CHECK_FREQUENCY = '/app/viewport/memory/queryFrequency'
RTX_SPP = '/rtx/pathtracing/spp'
RTX_PT_TOTAL_SPP = '/rtx/pathtracing/totalSpp'
RTX_ACCUMULATED_LIMIT = '/rtx/raytracing/accumulationLimit'
RTX_ACCUMULATION_ENABLED = '/rtx/raytracing/enableAccumulation'
IRAY_MAX_SAMPLES = '/rtx/iray/progressive_rendering_max_samples'
TOAST_MESSAGE_KEY = '/app/viewport/toastMessage'
CAM_SPEED_MESSAGE_KEY = '/exts/omni.kit.viewport.window/cameraSpeedMessage'
HUD_MEM_TYPES_KEY = "/exts/omni.kit.viewport.window/hud/memoryTypes"

import omni.kit.app
RTX_STREAMING_STATUS_GLOBAL_EVENT: str = "omni.rtx.StreamingStatus"
RTX_STREAMING_STATUS_EVENT: int = carb.events.type_from_string(RTX_STREAMING_STATUS_GLOBAL_EVENT)
omni.kit.app.register_event_alias(RTX_STREAMING_STATUS_EVENT, RTX_STREAMING_STATUS_GLOBAL_EVENT)

_get_device_info = None

def _human_readable_size(size: int, binary : bool = True, decimal_places: int = 1):
    def calc_human_readable(size, scale, *units):
        n_units = len(units)
        for i in range(n_units):
            if (size < scale) or (i == n_units):
                return f'{size:.{decimal_places}f} {units[i]}'
            size /= scale
    if binary:
        return calc_human_readable(size, 1024, 'B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB')
    return calc_human_readable(size, 1000, 'B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')

# XXX: Move to omni.kit.viewport.serialization
def _resolve_hud_visibility(viewport_api, setting_key: str, isettings: carb.settings.ISettings, dflt_value: bool = True):
    # Resolve initial visibility based on persitent settings or app defaults
    visible_key = "/app/viewport/{vp_section}" + (f"/hud/{setting_key}/visible" if setting_key else "/hud/visible")
    vp_visible = visible_key.format(vp_section=viewport_api.id)
    setting_key = "/persistent" + vp_visible
    visible = isettings.get(setting_key)
    if visible is None:
        visible = isettings.get(vp_visible)
        if visible is None:
            visible = isettings.get(visible_key.format(vp_section="defaults"))
            if visible is None:
                visible = dflt_value

        # XXX: The application defaults need to get pushed into persistent data now (for display-menu)
        isettings.set_default(setting_key, visible)

    return (setting_key, visible)


def _get_background_alpha(settings):
    bg_alpha = settings.get("/persistent/app/viewport/ui/background/opacity")
    return bg_alpha if bg_alpha is not None else 1.0


class ViewportStatistic:
    def __init__(self, stat_name: str, setting_key: str = None, parent = None,
                 alignment: ui.Alignment=ui.Alignment.RIGHT, viewport_api = None):
        self.__stat_name = stat_name
        self.__labels = []
        self.__alignment = alignment
        self.__ui_obj = self._create_ui(alignment)
        self.__subscription_id: Optional[carb.settings.SubscriptionId] = None
        self.__setting_key: Optional[str] = None

        if setting_key:
            settings = carb.settings.get_settings()
            self.__setting_key, self.visible = _resolve_hud_visibility(viewport_api, setting_key, settings)

            # Watch for per-viewport changes to persistent setting to control visibility
            self.__subscription_id = settings.subscribe_to_node_change_events(
                self.__setting_key, self._visibility_change
            )
            self._visibility_change(None, carb.settings.ChangeEventType.CHANGED)

    def __del__(self):
        self.destroy()

    def _visibility_change(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            self.visible = bool(carb.settings.get_settings().get(self.__setting_key))

    @property
    def container(self):
        return self.__ui_obj

    def _create_ui(self, alignment: ui.Alignment):
        return ui.VStack(name='Stack', height=0, style_type_name_override='ViewportStats', alignment=alignment)

    def _create_label(self, text: str = '', alignment: Optional[ui.Alignment] = None):
        if alignment is None:
            alignment = self.alignment
        return ui.Label(text, name='Label', style_type_name_override='ViewportStats', alignment=alignment)

    def _destroy_labels(self):
        for label in self.__labels:
            label.destroy()
        self.__labels = []
        self.__ui_obj.clear()
        # Workaround an issue where space is left where the stat was
        if self.__ui_obj.visible:
            self.__ui_obj.visible = False
            self.__ui_obj.visible = True

    def update(self, update_info: dict):
        if self.skip_update(update_info):
            return

        stats = self.update_stats(update_info)
        # If no stats, clear all the labels now
        if not stats:
            self._destroy_labels()
            return

        # If the number of stats has gotten less, need to rebuild it all
        index, n_stats = 0, len(stats)
        if n_stats < len(self.__labels):
            self._destroy_labels()

        for txt in stats:
            self.set_text(txt, index)
            index = index + 1

    def skip_update(self, update_info: dict):
        return False

    def update_stats(self, update_info: dict):
        return tuple()

    def set_text(self, txt: str, index: int):
        # If the number of stats has grown, add a new label
        if index >= len(self.__labels):
            with self.container:
                self.__labels.append(self._create_label())
        ui_obj = self.__labels[index]
        ui_obj.text = txt
        ui_obj.visible = txt != ''
        return ui_obj

    def destroy(self):
        if self.__labels:
            self._destroy_labels()
            self.__labels = None
        if self.__ui_obj:
            self.__ui_obj.destroy()
            self.__ui_obj = None
        if self.__subscription_id:
            carb.settings.get_settings().unsubscribe_to_change_events(self.__subscription_id)
            self.__subscription_id = None
        self.__setting_key = None

    @property
    def empty(self) -> bool:
        return not bool(self.__labels)

    @property
    def alignment(self) -> ui.Alignment:
        return self.__alignment

    @property
    def visible(self) -> bool:
        return self.__ui_obj.visible

    @visible.setter
    def visible(self, value):
        self.__ui_obj.visible = value

    @property
    def categories(self):
        return ('stats',)

    @property
    def name(self):
        return self.__stat_name


class ViewportMemoryStat(ViewportStatistic):
    def __init__(self, mem_type: str | None = None, *args, **kwargs):
        if mem_type == "process":
            self.update_stats = self.__update_process_memory
        elif mem_type == "device":
            self.update_stats = self.__update_device_memory
        elif mem_type == "host":
            self.update_stats = self.__update_host_memory
        else:
            self.update_stats = lambda *args, **kwargs: None
            carb.log_error(f"Unknown memory-type: {mem_type}")

        self.__label = mem_type.capitalize()
        self.__disabled = False
        super().__init__(f"{self.__label} Memory", setting_key=f"{mem_type}Memory", *args, **kwargs)

    def skip_update(self, update_info: dict):
        return update_info[MEMORY_CHECK_FREQUENCY]

    def __format_memory(self, update_info: dict, total: int | None = None, available: int | None = None, used: int | None = None, label: str | None = None):
        if used is None:
            used = total - available
        elif available is None:
            available = total - used
        elif total is None:
            total = available + used
        low_memory = (available / total) < update_info["low_mem_fraction"]
        label = label or f"{self.__label} Memory"
        return low_memory, f"{label}: {_human_readable_size(used)} used, {_human_readable_size(available)} available"

    def __update_device_memory(self, update_info: dict):
        stat_list = []
        global _get_device_info
        if not _get_device_info:
            return []

        dev_info = _get_device_info()
        self.__low_memory = []
        self.__disabled = []

        device_mask = update_info["viewport_api"].frame_info.get("device_mask")

        for desc_idx, dev_memory in zip(range(len(dev_info)), dev_info):
            # Check if this GPU is enabled or not
            enabled = bool(device_mask is not None and (device_mask & (1 << desc_idx)))
            self.__disabled.append(not enabled)

            available = 0
            budget, used = dev_memory["budget"], dev_memory["usage"]
            if budget > used:
                available = budget - used

            description = dev_memory['description'] or f"GPU {desc_idx}"

            low_mem, mem_txt = self.__format_memory(update_info, total=budget, available=available, used=used, label=description)
            self.__low_memory.append(low_mem)
            stat_list.append(mem_txt)

        return stat_list

    def __update_process_memory(self, update_info: dict):
        host_info = get_memory_info(rss=True)
        self.__low_memory, mem_txt = self.__format_memory(update_info, available=host_info['available_memory'], used=host_info["rss_memory"])
        return [mem_txt]

    def __update_host_memory(self, update_info: dict):
        host_info = get_memory_info()
        self.__low_memory, mem_txt = self.__format_memory(update_info, total=host_info['total_memory'], available=host_info["available_memory"])
        return [mem_txt]

    @staticmethod
    def __check_bool_or_list(obj: bool | List[bool], index: int):
        if obj is True:
            return True
        elif obj is False:
            return False
        return obj[index]

    def set_text(self, txt: str, index: int):
        ui_obj = super().set_text(txt, index)
        if not ui_obj:
            return
        elif self.__check_bool_or_list(self.__disabled, index):
            ui_obj.name = 'LabelDisabled'
        elif self.__check_bool_or_list(self.__low_memory, index):
            ui_obj.name = 'LabelError'
        else:
            ui_obj.name = 'Label'


class ViewportFPS(ViewportStatistic):
    def __init__(self, *args, **kwargs):
        super().__init__('FPS', setting_key='renderFPS', *args, **kwargs)
        self.__fps = None
        self.__multiplier = 1
        self.__precision = 2

    def skip_update(self, update_info: dict):
        # FPS update ignores freeze_frame as a signal that rendering is continuing.
        fps = round(update_info['viewport_api'].fps, self.__precision)
        multiplier = update_info['viewport_api'].frame_info.get('subframe_count', 1)
        should_skip_update = True
        if fps != self.__fps:
            self.__fps = fps
            should_skip_update = False
        if multiplier != self.__multiplier:
            self.__multiplier = multiplier
            should_skip_update = False
        return should_skip_update

    def update_stats(self, update_info: dict):
        effective_fps = self.__fps * self.__multiplier
        multiplier = max(self.__multiplier, 1)
        ms = 1000/effective_fps if effective_fps else 0
        multiplier_str = ',' if multiplier == 1 else (' ' + ('|' * (multiplier - 1)))
        return [f'FPS: {effective_fps:.{self.__precision}f}{multiplier_str} Frame time: {ms:.{self.__precision}f} ms']


class ViewportResolution(ViewportStatistic):
    def __init__(self, *args, **kwargs):
        super().__init__('Resolution', setting_key='renderResolution', *args, **kwargs)
        self.__resolution = None

    def skip_update(self, update_info: dict):
        viewport_api = update_info['viewport_api']
        # If Viewport is frozen to a frame, keep reolution displayed for that frame
        if viewport_api.freeze_frame:
            return True
        resolution = viewport_api.resolution
        if resolution == self.__resolution:
            return True
        self.__resolution = resolution
        return False

    def update_stats(self, update_info: dict):
        return [f'{self.__resolution[0]}x{self.__resolution[1]}']


class ViewportProgress(ViewportStatistic):
    def __init__(self, *args, **kwargs):
        super().__init__('Progress', setting_key='renderProgress', *args, **kwargs)
        self.__last_accumulated = 0
        self.__total_elapsed = 0

    def skip_update(self, update_info: dict):
        # If Viewport is frozen to a frame, don't update progress, what's displayed should be the last valid progress we have
        return update_info['viewport_api'].freeze_frame

    def update_stats(self, update_info: dict):
        viewport_api = update_info['viewport_api']
        total, accumulated = None, viewport_api.frame_info.get('progression', None)
        if accumulated is None:
            return

        label = 'PathTracing'
        decimal_places = 2
        no_limit = None
        renderer = viewport_api.hydra_engine
        settings = carb.settings.get_settings()
        if renderer == 'rtx':
            render_mode = settings.get('/rtx/rendermode')
            if render_mode == 'PathTracing':
                total = settings.get(RTX_PT_TOTAL_SPP)
                no_limit = 0
            elif settings.get(RTX_ACCUMULATION_ENABLED):
                label = 'Progress'
                total = settings.get(RTX_ACCUMULATED_LIMIT)
        elif renderer == 'iray':
            total = settings.get(IRAY_MAX_SAMPLES)
            no_limit = -1
        if total is None:
            return None

        rtx_spp = settings.get(RTX_SPP)
        if rtx_spp is None:
            return None

        # See RenderStatus in HydraRenderResults.h
        status = viewport_api.frame_info.get('status')

        if accumulated <= rtx_spp:
            self.__last_accumulated = 0
            self.__total_elapsed = 0
        # Update the elapsed time only if the rendering was a success, i.e. status 0.
        elif (status == 0) and ((self.__last_accumulated < total) or (no_limit is not None and total <= no_limit)):
            self.__total_elapsed = self.__total_elapsed + update_info['elapsed_time']
        self.__last_accumulated = accumulated
        return [f'{label}: {accumulated}/{total} spp : {self.__total_elapsed:.{decimal_places}f} sec']

class ViewportStreamingStatus(ViewportStatistic):
    def __init__(self, *args, **kwargs):
        super().__init__('StreamingStatus', setting_key='streamingStatus', *args, **kwargs)
        self._status = "Unknown"
        self._isDirty = False

        self._event_sub = get_eventdispatcher().observe_event(
            observer_name="streaming_status_listener",
            event_name=RTX_STREAMING_STATUS_GLOBAL_EVENT,
            on_event=self._on_msg_bus_payload)

    def getKeySafe(self, dictionary, *args):
        currentLevel = dictionary
        try:
            for key in args:
                currentLevel = currentLevel[key]
            return currentLevel
        except KeyError:
           return None

    def _on_msg_bus_payload(self, event: Event):
        self._isDirty = True
        isBusy = self.getKeySafe(event, "isBusy")
        if isBusy != None:
            self._status = ("Busy" if isBusy else "Idle")

        clients = self.getKeySafe(event, "DetailedStatus", "Clients")
        if clients != None and isinstance(clients, dict):

            # we are going to accumulate all "OutstandingItems", grouped by "GroupName" from each client
            # (note that it's not mandatory for all clients to specify a group or outstanding items, but we'll only display those that do)
            outstandingItemsForGroup = {}

            for clientName, clientState in clients.items():
                groupName = self.getKeySafe(clientState, "GroupName")
                outstandingItemsValue = self.getKeySafe(clientState, "State", "OutstandingItems")
                if groupName != None and outstandingItemsValue != None:
                    if groupName in outstandingItemsForGroup:
                        outstandingItemsForGroup[groupName] += outstandingItemsValue
                    else:
                        outstandingItemsForGroup[groupName] = outstandingItemsValue

            if len(outstandingItemsForGroup):
                self._status += " ("
                groupIndex = 0
                for name, outStandingItems in outstandingItemsForGroup.items():
                    if groupIndex > 0:
                        self._status += ", "
                    self._status += name + ":" + str(outStandingItems)
                    groupIndex+=1
                self._status += ")"


    def skip_update(self, update_info: dict):
        viewport_api = update_info['viewport_api']
        return not self._isDirty

    def update_stats(self, update_info: dict):
        return [f'Streaming: {self._status}']

class _HudMessageTime:
    def __init__(self, key: str):
        self.__message_time: float = 0
        self.__message_fade_in: float = 0
        self.__message_fade_out: float = 0
        self.__settings_subs: Sequence[carb.settings.SubscriptionId] = None
        self.__init(key)

    def __init(self, key: str):
        time_key: str = f"{key}/seconds"
        fade_in_key: str = f"{key}/fadeIn"
        fade_out_key: str = f"{key}/fadeOut"

        settings = carb.settings.get_settings()
        settings.set_default(time_key, 3)
        settings.set_default(fade_in_key, 0.5)
        settings.set_default(fade_out_key, 0.5)

        def timing_changed(*args, **kwargs):
            self.__message_time = settings.get(time_key)
            self.__message_fade_in = settings.get(fade_in_key)
            self.__message_fade_out = settings.get(fade_out_key)
        timing_changed()

        self.__settings_subs = (
            settings.subscribe_to_node_change_events(time_key, timing_changed),
            settings.subscribe_to_node_change_events(fade_in_key, timing_changed),
            settings.subscribe_to_node_change_events(fade_out_key, timing_changed),
        )

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__settings_subs:
            settings = carb.settings.get_settings()
            for sub in self.__settings_subs:
                settings.unsubscribe_to_change_events(sub)
            self.__settings_subs = None

    @property
    def message_time(self) -> float:
        return self.__message_time

    @property
    def message_fade_in(self) -> float:
        return self.__message_fade_in

    @property
    def message_fade_out(self) -> float:
        return self.__message_fade_out

    @property
    def total_up_time(self):
        return self.message_fade_in + self.message_time


class _HudMessageTracker():
    """Calculate alpha for _HudMessageTime acounting for possibility of reversing direction mid-fade"""
    def __init__(self, prev_tckr: Optional["_HudMessageTracker"] = None, message_time: Optional[_HudMessageTime] = None):
        self.__time: float = 0
        if prev_tckr and message_time:
            # If previous object was fading in, keep alpha
            if prev_tckr.__time < message_time.message_fade_in:
                self.__time = prev_tckr.__time
                return
            # If previous object was fading out, also keep alpha, but reverse direction
            total_msg_up_time = message_time.total_up_time
            if prev_tckr.__time > total_msg_up_time:
                self.__time = prev_tckr.__time - total_msg_up_time
                return
            # If previous object is already being shown at 100%, keep alpha 1
            self.__time = message_time.message_fade_in

    def update(self, message_time: _HudMessageTime, elapsed_time: float):
        self.__time += elapsed_time
        if self.__time < message_time.message_fade_in:
            if message_time.message_fade_in <= 0:
                return 1
            return min(1, self.__time / message_time.message_fade_in)
        total_msg_up_time = message_time.total_up_time
        if self.__time > total_msg_up_time:
            if message_time.message_fade_out <= 0:
                return 0
            return max(0, 1.0 - (self.__time - total_msg_up_time) / message_time.message_fade_out)
        return 1


class ViewportStatisticFading(ViewportStatistic):
    def __init__(self, anim_key: str, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__message_time = _HudMessageTime(anim_key)
        self.__update_sub = None
        self.__alpha = 0
        self.__parent = parent

    def destroy(self):
        self.__update_sub = None
        if self.__message_time:
            self.__message_time.destroy()
            self.__message_time = None
        super().destroy()

    def _skip_update(self, update_info: dict, check_empty: Optional[Callable] = None):
        # Skip updates when calld from the render-update, but return the cached alpha
        if update_info.get('external_update', None) is None:
            alpha = self.__alpha
            update_info['alpha'] = alpha
            if alpha <= 0:
                self.__update_sub = None
            return True

        # Skip any update if no message to display
        is_empty = check_empty() if check_empty else False
        if is_empty:
            update_info['alpha'] = 0
            self.__update_sub = None
        return is_empty

    def _update_alpha(self, update_info: dict, accumulate_alpha: Callable):
        alpha = 0
        elapsed_time = update_info['elapsed_time']
        if elapsed_time:
            alpha = accumulate_alpha(self.__message_time, elapsed_time, alpha)
        update_info['alpha'] = alpha
        if alpha <= 0:
            self.__update_sub = None
            self.visible = False
        else:
            self.visible = True
        return alpha

    def _begin_animation(self):
        # Add the updtae subscription so that messages / updates are received even when not rendering
        if self.__update_sub:
            return

        import carb.eventdispatcher

        bg_alpha = _get_background_alpha(carb.settings.get_settings())
        def on_update(event: carb.eventdispatcher.Event):
            # Build a dict close enough to the render-update info
            update_info = {
                'elapsed_time': event['dt'],
                'alpha': 1,
                'external_update': True, # Internally tells skip_update to not skip this update
                'background_alpha': bg_alpha
            }
            # Need to call through via parent ViewportStatsGroup to do the alpha adjustment
            self.__parent._update_stats(update_info)
            # Cache the updated alpha to be applied later, but kill the subscription if 0
            self.__alpha = update_info.get('alpha')

        # initialize alpha to 1 (what on_update would do, just in case the current app-loop-state causes
        # _skip_update to be called first
        self.__alpha = 1
        self.__update_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=on_update,
            observer_name=f"omni.kit.viewport.window.stats.ViewportStatisticFading[{self.name}]"
        )

    def _end_animation(self, alpha: float = 0):
        self.__update_sub = None
        self.__alpha = alpha

    @property
    def message_time(self) -> _HudMessageTime:
        return self.__message_time


class ViewportSpeed(ViewportStatisticFading):
    __CAM_VELOCITY = "/persistent/app/viewport/camMoveVelocity"
    __CAMERA_MANIP_MODE = "/exts/omni.kit.manipulator.camera/viewportMode"
    __COLLAPSE_CAM_SPEED = "/persistent" + f"{CAM_SPEED_MESSAGE_KEY}/collapsed"
    __FLY_VIEW_LOCK = "/persistent/exts/omni.kit.manipulator.camera/flyViewLock"
    __FLY_VIEW_LOCK_STAT = "/persistent/exts/omni.kit.viewport.window/cameraSpeedMessage/showFlyViewLock"

    def __init__(self, viewport_api, *args, **kwargs):
        self.__carb_subs: Sequence[carb.settings.SubscriptionId] = None
        self.__cam_speed_entry: Optional[ui.FloatField] = None
        self.__cam_speed_model_sub: Optional[carb.Subscription] = None
        self.__viewport_id: str = str(viewport_api.id)
        self.__root_frame: Optional[ui.Frame] = None
        self.__tracker: Optional[_HudMessageTracker] = None
        self.__style: Optional[dict] = None
        self.__focused_viewport: bool = False
        self.__fly_lock: Optional[ui.ImageWithProvider] = None

        super().__init__(anim_key=CAM_SPEED_MESSAGE_KEY, stat_name='Camera Speed', setting_key='cameraSpeed',
                         viewport_api=viewport_api, *args, **kwargs)

    def update(self, update_info: dict):
        if self._skip_update(update_info):
            return

        def accumulate_alpha(message_time: _HudMessageTime, elapsed_time: float, alpha: float):
            return self.__tracker.update(message_time, elapsed_time)

        self._update_alpha(update_info, accumulate_alpha)

    def _create_ui(self, alignment: ui.Alignment):
        ui_root = super()._create_ui(alignment=alignment)

        from pathlib import Path
        from omni.ui import color as cl, constant as fl
        extension_path = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.viewport.window}"))
        icons_path = extension_path.joinpath("data").joinpath("icons").absolute()

        self.__style = {
            "MouseImage": {
                "image_url": str(icons_path.joinpath("mouse_wheel_dark.svg")),
            },
            "ExpandCollapseButton": {
                "background_color": 0,
            },
            "ExpandCollapseButton.Image::ExpandButton": {
                "image_url": str(icons_path.joinpath("speed_expand.svg")),
            },
            "ExpandCollapseButton.Image::CollapseButton": {
                "image_url": str(icons_path.joinpath("speed_collapse.svg")),
            },
            "IconSeparator": {
                "border_width": 45,
            },
            "KeyboardKey": {
                "background_color": 0,
                "border_width": 1.5,
                "border_radius": 3
            },
            "KeyboardLabel": {
            },
            'ViewportStats::FloatField': {
                "background_color": 0,
            },
            "FlyLockButton": {
                "background_color": 0,
                'padding': 15,
            },
            "LockedImage::Locked": {
                "image_url": str(icons_path.joinpath("ignore_view_direction_on.svg")),
            },
            "LockedImage::UnLocked": {
                "image_url": str(icons_path.joinpath("ignore_view_direction_off.svg")),
            },

        }

        with ui_root:
            self.__root_frame = ui.Frame(build_fn=self.__build_root_ui, style=self.__style)
            self.__build_root_ui()
            ui_root.set_mouse_hovered_fn(self.__mouse_hovered)

        return ui_root

    def __track_time(self):
        self.__tracker = _HudMessageTracker(self.__tracker, self.message_time)
        self._begin_animation()

    def __toggle_cam_speed_info(self):
        # Reset the timer tracking on ui interaction
        self.__track_time()
        # Toggle the persistan setting
        settings = carb.settings.get_settings()
        setting_key = self.__COLLAPSE_CAM_SPEED
        collapsed = not bool(settings.get(setting_key))
        settings.set(setting_key, collapsed)

    def __add_mouse_item(self, label: str, tooltip: str, key_label: Optional[str] = None):
        ui.Spacer(width=10)
        ui.Line(width=2, alignment=ui.Alignment.V_CENTER, style_type_name_override="IconSeparator")
        ui.Spacer(width=10)

        with ui.VStack(width=50, alignment=ui.Alignment.CENTER):
            with ui.ZStack(content_clipping=True):
                if key_label:
                    ui.Rectangle(width=50, height=25, style_type_name_override="KeyboardKey", tooltip=tooltip)
                    ui.Label(key_label, alignment=ui.Alignment.CENTER, style_type_name_override="KeyboardLabel",
                             tooltip=tooltip)
                else:
                    # XXX: Odd ui-layout to have the image properly centered
                    with ui.HStack():
                        ui.Spacer(width=15)
                        self.__fly_lock = ui.ImageWithProvider(width=50, height=30, tooltip=tooltip,
                                                               name=self.__get_lock_style_name(),
                                                               style_type_name_override="LockedImage")
                        ui.Spacer()
                    ui.Button(width=50, height=25, style_type_name_override="FlyLockButton",
                              clicked_fn=self.__toggle_fly_view_lock, tooltip=tooltip)

            ui.Spacer(height=5)
            ui.Label(label, alignment=ui.Alignment.CENTER, style_type_name_override="ViewportStats", name="Label")

    def __build_cam_speed_info(self, *args, **kwargs):
        mouse_tip = "Using Mouse wheel during flight navigation will adjust how fast or slow the camera will travel"
        ctrl_tip = "Pressing and holding Ctrl button during flight navigation will decrease the speed the camera travels"
        shft_tip = "Pressing and holding Shift button during flight navigation will increase the speed the camera travels"
        settings = carb.settings.get_settings()
        with ui.VStack():
            ui.Spacer(height=10)
            with ui.HStack():
                with ui.VStack(width=50, alignment=ui.Alignment.CENTER):
                    with ui.HStack():
                        ui.Spacer(width=10)
                        ui.ImageWithProvider(width=30, height=30, style_type_name_override="MouseImage", tooltip=mouse_tip)
                    ui.Label('Speed', alignment=ui.Alignment.CENTER, style_type_name_override="ViewportStats", name="Label")

                self.__add_mouse_item("Slow", ctrl_tip, "ctrl")

                self.__add_mouse_item("Fast", shft_tip, "shift")

                if settings.get(self.__FLY_VIEW_LOCK_STAT):
                    tootip = "Whether forward/backward and up/down movements ignore camera-view direction (similar to left/right strafe)"
                    self.__add_mouse_item("Nav Height", tootip, None)

    def __build_root_ui(self, collapsed: Optional[bool] = None):
        if collapsed is None:
            collapsed = bool(carb.settings.get_settings().get(self.__COLLAPSE_CAM_SPEED))
        with self.__root_frame:
            with ui.VStack():
                with ui.HStack(alignment=ui.Alignment.LEFT, content_clipping=True):
                    ui.Button(width=20, name="ExpandButton" if collapsed else "CollapseButton",
                              style_type_name_override="ExpandCollapseButton",
                              clicked_fn=self.__toggle_cam_speed_info)
                    ui.Label("Camera Speed:", style_type_name_override="ViewportStats", name="Label")
                    # Additional HStack container to reduce float-field shifting right when expanded
                    with ui.HStack(alignment=ui.Alignment.LEFT):
                        self.__cam_speed_entry = ui.FloatField(width=55,
                                                               style_type_name_override="ViewportStats", name="FloatField")
                        ui.Spacer()
                    ui.Spacer()

                    def model_changed(model: ui.AbstractValueModel):
                        try:
                            # Compare the values with a precision to avoid possibly excessive recursion
                            settings = carb.settings.get_settings()
                            model_value, carb_value = model.as_float, settings.get(self.__CAM_VELOCITY)
                            if round(model_value, 6) == round(carb_value, 6):
                                return
                            # Short-circuit carb event handling in __cam_vel_changed
                            self.__focused_viewport = False
                            final_value = _limit_camera_velocity(model_value, settings, "text")
                            settings.set(self.__CAM_VELOCITY, final_value)
                            if model_value != final_value:
                                model.set_value(final_value)
                        finally:
                            self.__focused_viewport = True
                            # Reset the animation counter
                            self.__track_time()

                    model = self.__cam_speed_entry.model
                    self.__cam_speed_entry.precision = 3
                    model.set_value(self.__get_camera_speed_value())
                    self.__cam_speed_model_sub = model.subscribe_value_changed_fn(model_changed)

                if not collapsed:
                    self.__build_cam_speed_info()

    def __get_camera_speed_value(self):
        return carb.settings.get_settings().get(self.__CAM_VELOCITY) or 0

    def __cam_manip_mode_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            manip_mode = carb.settings.get_settings().get(self.__CAMERA_MANIP_MODE)
            if manip_mode and manip_mode[0] == self.__viewport_id:
                self.__focused_viewport = True
                if manip_mode[1] == "fly":
                    self.__track_time()
            else:
                self.__focused_viewport = False

    def __collapse_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if self.__root_frame and event_type == carb.settings.ChangeEventType.CHANGED:
            self.__root_frame.rebuild()

    def __cam_vel_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if self.__cam_speed_entry and self.__focused_viewport and event_type == carb.settings.ChangeEventType.CHANGED:
            self.__cam_speed_entry.model.set_value(self.__get_camera_speed_value())
            self.__track_time()

    def __mouse_hovered(self, hovered: bool, *args):
        if hovered:
            self._end_animation(1)
        else:
            self._begin_animation()

    def _visibility_change(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        settings = carb.settings.get_settings()
        super()._visibility_change(item, event_type)
        if self.visible:
            # Made visible, setup additional subscriptions need now
            if self.__carb_subs is None:
                self.__carb_subs = (
                    settings.subscribe_to_node_change_events(self.__CAM_VELOCITY, self.__cam_vel_changed),
                    settings.subscribe_to_node_change_events(f"{self.__CAMERA_MANIP_MODE}/1", self.__cam_manip_mode_changed),
                    settings.subscribe_to_node_change_events(self.__COLLAPSE_CAM_SPEED, self.__collapse_changed),
                    settings.subscribe_to_node_change_events(self.__FLY_VIEW_LOCK_STAT, self.__show_fly_view_lock),
                    settings.subscribe_to_node_change_events(self.__FLY_VIEW_LOCK, self.__toggled_fly_view_lock),
                )
                # Handle init case from super()__init__, only want the subscritions setup, not to show the dialog
                if item is not None:
                    self.__focused_viewport = True
                    self.__cam_vel_changed(None, carb.settings.ChangeEventType.CHANGED)
        elif self.__carb_subs:
            # Made invisible, remove uneeded subscriptions now
            self.__remove_camera_subs(settings)
            self._end_animation()

    def __remove_camera_subs(self, settings):
        carb_subs, self.__carb_subs = self.__carb_subs, None
        if carb_subs:
            for carb_sub in carb_subs:
                settings.unsubscribe_to_change_events(carb_sub)

    def __show_fly_view_lock(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return
        root_frame = self.__root_frame
        if root_frame:
            root_frame.rebuild()

    def __get_lock_style_name(self):
        enabled = carb.settings.get_settings().get(self.__FLY_VIEW_LOCK)
        return "Locked" if enabled else "UnLocked"

    def __toggled_fly_view_lock(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        lock_image = self.__fly_lock
        if lock_image:
            lock_image.name = self.__get_lock_style_name()

    def __toggle_fly_view_lock(self):
        key = self.__FLY_VIEW_LOCK
        settings = carb.settings.get_settings()
        settings.set(key, not bool(settings.get(key)))

    def destroy(self):
        self.__remove_camera_subs(carb.settings.get_settings())
        self.__tracker = None
        self.__fly_lock = None
        if self.__root_frame:
            self.__root_frame.destroy()
            self.__root_frame = None
        if self.__cam_speed_model_sub:
            self.__cam_speed_model_sub = None
        if self.__cam_speed_entry:
            self.__cam_speed_entry.destroy()
            self.__cam_speed_entry = None
        super().destroy()

    @property
    def empty(self) -> bool:
        return False


class ViewportMessage(ViewportStatisticFading):
    class _ToastMessage(_HudMessageTracker):
        """Store a message to fade with _HudMessageTracker"""
        def __init__(self, message: str, *args, **kwargs):
            self.__message = message
            super().__init__(*args, **kwargs)

        @property
        def message(self):
            return self.__message

    def __init__(self, *args, **kwargs):
        super().__init__(anim_key=TOAST_MESSAGE_KEY, stat_name='Toast Message', setting_key="toastMessage", *args, **kwargs)
        self.__messages = {}

    def skip_update(self, update_info: dict):
        return self._skip_update(update_info, lambda: not bool(self.__messages))

    def update_stats(self, update_info: dict):
        def accumulate_alpha(message_time: _HudMessageTime, elapsed_time: float, alpha: float):
            self.__messages, messages = {}, self.__messages
            for msg_id, msg in messages.items():
                cur_alpha = msg.update(message_time, elapsed_time)
                if cur_alpha:
                    alpha = max(cur_alpha, alpha)
                    self.__messages[msg_id] = msg
            return alpha

        self._update_alpha(update_info, accumulate_alpha)
        return [obj.message for obj in self.__messages.values()]

    def destroy(self):
        super().destroy()
        self.__messages = {}

    def add_message(self, message: str, message_id: str):
        self.__messages[message_id] = ViewportMessage._ToastMessage(message, self.__messages.get(message_id), self.message_time)
        # Add the update subscription so that messages / updates are received even when not rendering
        self._begin_animation()

    def remove_message(self, message: str, message_id: str):
        if message_id in self.__messages:
            del self.__messages[message_id]


class ViewportStatsGroup:
    def __init__(self, factories, name: str, alignment: ui.Alignment, viewport_api):
        self.__alpha = 0
        self.__stats = []
        self.__group_name = name
        self.__container = ui.ZStack(name='Root', width=0, height=0, style_type_name_override='ViewportStats')
        proxy_self = weakref.proxy(self)
        with self.__container:
            ui.Rectangle(name='Background', style_type_name_override='ViewportStats')
            with ui.VStack(name='Group', style_type_name_override='ViewportStats'):
                for stat_obj in factories:
                    self.__stats.append(stat_obj(parent=proxy_self, alignment=alignment, viewport_api=viewport_api))

        self.__container.visible = False

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__stats:
            for stat in self.__stats:
                stat.destroy()
            self.__stats = []
        if self.__container:
            self.__container.clear()
            self.__container.destroy()
            self.__container = None

    def __set_alpha(self, alpha: float, background_alpha: float, background_alpha_changed: bool):
        alpha = min(0.8, alpha)
        if alpha == self.__alpha and (not background_alpha_changed):
            return

        self.__alpha = alpha
        self.__container.set_style({
            'ViewportStats::Background': {
                'background_color': ui.color(0.145, 0.157, 0.165, alpha * background_alpha),
            },
            'ViewportStats::Label': {
                'color': ui.color(1.0, 1.0, 1.0, alpha)
            },
            'ViewportStats::LabelError': {
                'color': ui.color(1.0, 0.0, 0.0, alpha)
            },
            'ViewportStats::LabelWarning': {
                'color': ui.color(1.0, 1.0, 0.0, alpha)
            },
            "MouseImage": {
                "color": ui.color(1.0, 1.0, 1.0, alpha),
            },
            "IconSeparator": {
                "color": ui.color(0.431, 0.431, 0.431, alpha),
            },
            "ExpandCollapseButton.Image::ExpandButton": {
                "color": ui.color(0.102, 0.569, 0.772, alpha),
            },
            "ExpandCollapseButton.Image::CollapseButton": {
                "color": ui.color(0.102, 0.569, 0.772, alpha),
            },
            "KeyboardKey": {
                "border_color": ui.color(0.102, 0.569, 0.772, alpha),
            },
            "KeyboardLabel": {
                "color": ui.color(0.102, 0.569, 0.772, alpha),
            },
            "LockedImage": {
                "color": ui.color(1.0, 1.0, 1.0, alpha),
            },
            'ViewportStats::FloatField': {
                'color': ui.color(1.0, 1.0, 1.0, alpha),
                "background_selected_color": ui.color(0.431, 0.431, 0.431, alpha),
            },
        })
        self.__container.visible = bool(alpha > 0)

    def _update_stats(self, update_info: dict):
        alpha = 0
        any_visible = False
        for stat in self.__stats:
            try:
                update_info['alpha'] = 1
                stat.update(update_info)
                any_visible = any_visible or (stat.visible and not stat.empty)
                alpha = max(alpha, update_info['alpha'])
            except Exception:
                import traceback
                carb.log_error(f"Error updating stats {stat}. Traceback:\n{traceback.format_exc()}")

        alpha = alpha if any_visible else 0
        self.__set_alpha(alpha, update_info.get('background_alpha'), update_info.get('background_alpha_changed'))
        return alpha

    @property
    def visible(self):
        return self.__container.visible if self.__container else False

    @visible.setter
    def visible(self, value):
        if self.__container:
            self.__container.visible = value
        elif value:
            carb.log_error(f"{self.__group_name} has been destroyed, cannot set visibility to True")

    @property
    def categories(self):
        return ('stats',)

    @property
    def name(self):
        return self.__group_name

    @property
    def layers(self):
        for stats in self.__stats:
            yield stats


class ViewportStatsLayer:
    # Legacy setting that still need to be honored (transiently)
    _LEGACY_FORCE_FPS_OFF = "/app/viewport/forceHideFps"
    _LEGACY_LAYER_MENU_ON = "/app/viewport/showLayerMenu"

    def __init__(self, desc: dict):
        settings = carb.settings.get_settings()
        settings.set_default(LOW_MEMORY_SETTING_PATH, 0.2)
        settings.set_default(MEMORY_CHECK_FREQUENCY, 1.0)

        self.__viewport_api = desc.get('viewport_api')
        self.__frame_changed_sub = None
        self.__disable_ui_sub: Optional[carb.SubscriptionId] = None
        self.__setting_key, visible = _resolve_hud_visibility(self.__viewport_api, None, settings)
        self.__bg_alpha = 0

        # Check some legacy settings that control visibility and should be honored
        destroy_old_key = f"/persistent/app/viewport/{self.__viewport_api.id}/hud/forceVisible"
        force_vis_tmp = settings.get(destroy_old_key)
        if force_vis_tmp is not None:
            # Clear out this key from any further persistence
            settings.destroy_item(destroy_old_key)
            if force_vis_tmp:
                # Store it back to the persistent setting
                settings.set(self.__setting_key, True)
                visible = True

        # Check some legacy settings that control visibility and should be honored
        if visible:
            visible = self.__get_transient_visibility(settings)

        self.__last_time = time.monotonic()
        self.__frequencies = {}
        for key in [MEMORY_CHECK_FREQUENCY]:
            value = settings.get(key)
            self.__frequencies[key] = [value, value]

        self.__groups: Sequence[ViewportStatsGroup] = None
        self.__root:ui.Frame = ui.Frame(horizontal_clipping=True, content_clipping=1, opaque_for_mouse_events=True)

        self.__disable_ui_sub = (
            settings.subscribe_to_node_change_events(self.__setting_key, self.__stats_visiblity_changed),
            settings.subscribe_to_node_change_events(self._LEGACY_FORCE_FPS_OFF, self.__legacy_transient_changed),
            settings.subscribe_to_node_change_events(self._LEGACY_LAYER_MENU_ON, self.__legacy_transient_changed)
        )
        self.visible = visible

        # Workaround an issue where camera-speed HUD check should default to on
        settings.set_default(f"/persistent/app/viewport/{self.__viewport_api.id}/hud/cameraSpeed/visible", True)

    def __destroy_all_stats(self, value = None):
        if self.__groups:
            for group in self.__groups:
                group.destroy()
        self.__groups = value

    def __build_stats_hud(self, viewport_api):
        if self.__root:
            self.__root.clear()
        self.__destroy_all_stats([])

        right_stat_factories = [ViewportFPS]

        # Optional omni.hydra.engine.stats dependency
        global _get_device_info
        if not _get_device_info:
            try:
                from omni.hydra.engine.stats import get_device_info
                _get_device_info = get_device_info
            except ImportError:
                pass

        settings = carb.settings.get_settings()
        memory_types = settings.get(HUD_MEM_TYPES_KEY) or tuple()
        for mem_type in memory_types:
            if mem_type:
                right_stat_factories.append(lambda mem_type=mem_type.lower(), *args, **kwargs: ViewportMemoryStat(mem_type, *args, **kwargs))

        right_stat_factories.append(ViewportProgress)
        right_stat_factories.append(ViewportResolution)

        if settings.get("/app/viewport/enableStreamingStats"):
            right_stat_factories.append(ViewportStreamingStatus)

        # XXX: Need menu-bar height
        hud_top = 20 if hasattr(ui.constant, 'viewport_menubar_height') else 0
        with self.__root:
            with ui.VStack(height=hud_top):
                ui.Spacer(name='Spacer', style_type_name_override='ViewportStats')
                with ui.HStack():
                    with ui.VStack():
                        self.__groups.append(ViewportStatsGroup([ViewportSpeed],
                                                                "Viewport Speed",
                                                                ui.Alignment.LEFT,
                                                                self.__viewport_api))
                        self.__groups.append(ViewportStatsGroup([ViewportMessage],
                                                                "Viewport Message",
                                                                ui.Alignment.LEFT,
                                                                self.__viewport_api))

                    ui.Spacer(name='LeftRightSpacer', style_type_name_override='ViewportStats')

                    self.__groups.append(ViewportStatsGroup(right_stat_factories,
                                                            "Viewport HUD",
                                                            ui.Alignment.RIGHT,
                                                            self.__viewport_api))

    def __stats_visiblity_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            self.visible = bool(carb.settings.get_settings().get(self.__setting_key))

    @staticmethod
    def __get_transient_visibility(settings):
        # Legacy compat, this takes precedence when explicitly set to False
        ll_lm_vis = settings.get(ViewportStatsLayer._LEGACY_LAYER_MENU_ON)
        if (ll_lm_vis is not None) and (not bool(ll_lm_vis)):
            return False
        # Now check the other transient visibility
        if bool(settings.get(ViewportStatsLayer._LEGACY_FORCE_FPS_OFF)):
            return False

        return True

    def __legacy_transient_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            if self.__get_transient_visibility(carb.settings.get_settings()):
                self.__stats_visiblity_changed(None, event_type)
            else:
                self.visible = False

    def __set_stats_enabled(self, enabled: bool):
        if enabled:
            viewport_api = self.__viewport_api
            if not self.__groups:
                self.__build_stats_hud(viewport_api)
            if self.__frame_changed_sub is None:
                self.__frame_changed_sub = viewport_api.subscribe_to_frame_change(self.__update_stats)

            self.__update_stats(viewport_api)
        else:
            if self.__frame_changed_sub:
                self.__frame_changed_sub.destroy()
                self.__frame_changed_sub = None
            if self.__root:
                self.__root.clear()
            self.__destroy_all_stats([])

        self.__root.visible = enabled

    def __make_update_info(self, viewport_api):
        now = time.monotonic()
        elapsed_time, self.__last_time = now - self.__last_time, now

        settings = carb.settings.get_settings()
        bg_alpha = _get_background_alpha(settings)
        update_info = {
            'elapsed_time': elapsed_time,
            'low_mem_fraction': settings.get(LOW_MEMORY_SETTING_PATH),
            'viewport_api': viewport_api,
            'alpha': 1,
            'background_alpha': bg_alpha
        }

        # Signal background alpha changed
        if self.__bg_alpha != bg_alpha:
            self.__bg_alpha = bg_alpha
            update_info['background_alpha_changed'] = True

        for key, value in self.__frequencies.items():
            value[0] += elapsed_time
            value[1] = settings.get(key)
            if value[0] >= value[1]:
                value[0] = 0
                update_info[key] = False
            else:
                update_info[key] = True

        return update_info

    def __update_stats(self, viewport_api):
        if (not self.__root.visible) or (not self.__groups):
            return

        update_info = self.__make_update_info(viewport_api)
        for group in self.__groups:
            group._update_stats(update_info)

    def destroy(self):
        ui_subs, self.__disable_ui_sub = self.__disable_ui_sub, None
        if ui_subs:
            settings = carb.settings.get_settings()
            for ui_sub in ui_subs:
                settings.unsubscribe_to_change_events(ui_sub)

        self.__set_stats_enabled(False)
        self.__destroy_all_stats()
        if self.__root:
            self.__root.clear()
            self.__root = None
        self.__usd_context_name = None

    @property
    def layers(self):
        if self.__groups:
            for group in self.__groups:
                yield group

    @property
    def visible(self):
        return self.__root.visible

    @visible.setter
    def visible(self, value):
        value = bool(value)
        if value:
            if not self.__get_transient_visibility(carb.settings.get_settings()):
                return

        self.__set_stats_enabled(value)

    @property
    def categories(self):
        return ('stats',)

    @property
    def name(self):
        return 'All Stats'
