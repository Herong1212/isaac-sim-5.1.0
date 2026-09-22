import math
import typing
from functools import lru_cache

import carb
import carb.dictionary
import carb.events
import carb.settings
import omni.kit.app
import omni.kit.viewport.utility as vp_util
import omni.stageupdate
import omni.timeline
import omni.usd
from omni import ui
from pxr import Sdf, Usd, UsdGeom
import SequenceSchema

from . import utils

try:
    # OMPE-20564: Since Kit 106.1 usage of pxr.OmniAudioSchema is deprecated
    import OmniAudioSchema
except ImportError:
    try:
        # pxr.OmniAudioSchema is deprecated in Kit 106.1+, but still available in Kit 106.0
        # so fallback to pxr.OmniAudioSchema if OmniAudioSchema is not available
        from pxr import OmniAudioSchema
    except ImportError:
        OmniAudioSchema = None

if utils.anim_curve is not None:
    import omni.graph.core as og

try:
    import omni.kit.viewport.menubar.camera as menubar_camera
    from omni.kit.viewport.menubar.core import SelectableMenuItem
except ImportError:
    menubar_camera = None
    SelectableMenuItem = None


@lru_cache()
def g_stage_update_interface():
    return omni.stageupdate.get_stage_update_interface()


@lru_cache()
def g_settings():
    return carb.settings.get_settings()


UPDATE_NODE_ID = "SequencePlayer"
USE_SEQUENCER_CAMERA = "/persistent/exts/omni.kit.window.sequencer/useSequencerCamera"


def _get_setting(key: str, default_value):
    value = g_settings().get(key)
    if value is None:
        return default_value
    return value


class _Player:
    def __init__(self):
        self._value_clip_baker = None
        self._camera_cache = None
        self._camera_switching_enabled = ui.SimpleBoolModel(False)
        self._sequence_camera_menu_item = None
        self._stage_update_sub: omni.stageupdate.StageUpdateNode = None
        self._camera_switch_setting_sub: carb.Subscription = None
        self._camera_switching_value_sub: carb.Subscription = None
        self._reset_stage_data()

    def _reset_stage_data(self):
        self._previous_camera_path = None
        self._last_camera_pair = None
        self._anim_datas = {}
        self._asset_datas = {}

    def on_startup(self):
        self._camera_switching_enabled.set_value(_get_setting(USE_SEQUENCER_CAMERA, False))
        SequenceSchema.ValueClipBaker.SetUpdateCallback(self._on_clip_update)
        self._stage_update_sub = g_stage_update_interface().create_stage_update_node(
            UPDATE_NODE_ID, None, None, self._on_update, None, None, None
        )
        self._camera_switch_setting_sub = omni.kit.app.SettingChangeSubscription(
            USE_SEQUENCER_CAMERA, on_change=self._on_camera_switch_setting_change
        )

        if menubar_camera:
            menubar_camera_inst: menubar_camera.ViewportCameraMenuBarExtension = menubar_camera.get_instance()
            menubar_camera_inst.register_menu_item(self._build_camera_menu_item, order=-95)
        self._camera_switching_value_sub = self._camera_switching_enabled.subscribe_value_changed_fn(
            self._on_camera_switch_value_change
        )

    def _build_camera_menu_item(self, viewport_context, cam_menu: ui.Menu):
        cam_menu.checked = False
        self._sequence_camera_menu_item = SelectableMenuItem(
            "Sequencer Camera Sync",
            model=self._camera_switching_enabled,
        )
        ui.Separator()

    def on_shutdown(self):
        # remove all subscriptions
        self._value_clip_baker = None
        SequenceSchema.ValueClipBaker.SetUpdateCallback(None)
        self._stage_update_sub = None
        self._camera_switch_setting_sub = None
        self._camera_switching_value_sub = None
        # destroy any ui elements
        self._cleanup_menus()

    def _cleanup_menus(self):
        if not menubar_camera:
            return

        menubar_camera_inst: menubar_camera.ViewportCameraMenuBarExtension = menubar_camera.get_instance()
        if not menubar_camera_inst:
            return

        menubar_camera_inst.deregister_menu_item(self._build_camera_menu_item)
        if self._sequence_camera_menu_item:
            self._sequence_camera_menu_item.destroy()
            self._sequence_camera_menu_item = None

    def _on_clip_update(
        self,
        update_type: SequenceSchema.ValueClipBaker.UpdateType,
        clip: Sdf.Path,
        clip_data: SequenceSchema.ValueClipBaker.AssetClipData,
        time: Usd.TimeCode,
        asset_prim: Sdf.Path,
        stage: Usd.Stage,
    ):
        if update_type == SequenceSchema.ValueClipBaker.UpdateType.Update and OmniAudioSchema is not None:
            sound = OmniAudioSchema.Sound.Get(stage, asset_prim)
            if sound:
                return self._on_update_sound_prim(sound, clip_data)

        anim_prim = stage.GetPrimAtPath(clip_data.animPrim)
        if (anim_prim and utils.is_curve_node(anim_prim)) or clip in self._anim_datas:
            self._on_update_anim_data(update_type, clip, clip_data, time, asset_prim, anim_prim, stage)
            return []

        return []

    def _on_update_anim_data(self, update_type, clip, clip_data, time, asset_prim, anim_prim, stage):
        if utils.anim_curve is None:
            if update_type == SequenceSchema.ValueClipBaker.UpdateType.Initialize:
                carb.log_error(
                    f"omni.anim.curve is not available. Sequencer can't handle animation {anim_prim} correctly for clip {clip}."
                )
            return

        class AnimData:
            def __init__(self):
                self.curve_node = None
                self.anim_time = None
                self.existing_curve_node = False
                self.org_node_input_time = None
                self.org_node_use_global_time = None
                self.anim_offset = None

        time_input_name = "inputs:Time"

        if update_type == SequenceSchema.ValueClipBaker.UpdateType.Initialize:
            anim_data = AnimData()
            self._anim_datas[clip] = anim_data

            anim_data.anim_time = utils.get_anim_data_range(anim_prim)
            if anim_data.anim_time is None:
                return

            anim_data.anim_time = list(anim_data.anim_time)

            def clamp(val, min, max):
                if val < min:
                    return min
                elif val > max:
                    return max
                else:
                    return val

            if not math.isnan(clip_data.animTime[0]):
                anim_data.anim_time[0] = clamp(clip_data.animTime[0], anim_data.anim_time[0], anim_data.anim_time[1])
            if not math.isnan(clip_data.animTime[1]):
                anim_data.anim_time[1] = clamp(clip_data.animTime[1], anim_data.anim_time[0], anim_data.anim_time[1])
            if not math.isnan(clip_data.animTime[2]):
                anim_data.anim_offset = clamp(clip_data.animTime[2], anim_data.anim_time[0], anim_data.anim_time[1])
            else:
                anim_data.anim_offset = anim_data.anim_time[0]

            node_path = anim_prim.GetPath().pathString

            anim_data.curve_node = og.get_node_by_path(node_path)
            if anim_data.curve_node:
                anim_data.curve_node.set_disabled(False)
                anim_data.org_node_input_time = anim_data.curve_node.get_attribute(time_input_name).get()
                use_global_time_attr = anim_data.curve_node.get_attribute("inputs:UseGlobalTime")
                anim_data.org_node_use_global_time = use_global_time_attr.get()
                use_global_time_attr.set(False)
        elif update_type == SequenceSchema.ValueClipBaker.UpdateType.Clear:
            if clip not in self._anim_datas:
                return

            anim_data = self._anim_datas.pop(clip)
            if asset_prim in self._asset_datas:
                if self._asset_datas[asset_prim] is anim_data.curve_node:
                    del self._asset_datas[asset_prim]

            if not anim_data.curve_node:
                return

            anim_data.curve_node.get_attribute("inputs:UseGlobalTime").set(anim_data.org_node_use_global_time)

            node_path = anim_data.curve_node.get_prim_path()

            if anim_data.existing_curve_node:
                time_attr = anim_data.curve_node.get_attribute(time_input_name)
                if time_attr and anim_data.org_node_input_time is not None:
                    time_attr.set(anim_data.org_node_input_time)
            else:
                stage.RemovePrim(node_path)
        elif update_type == SequenceSchema.ValueClipBaker.UpdateType.Update:
            anim_data = self._anim_datas[clip]
            if anim_data.anim_time is None or not anim_data.curve_node:
                return

            time = time.GetValue()
            if time > clip_data.endTime:
                time = clip_data.endTime
            time -= clip_data.startTime
            time = max(0, time)
            time *= clip_data.playRate
            if anim_data.anim_offset is not None:
                time += anim_data.anim_offset - anim_data.anim_time[0]

            anim_length = anim_data.anim_time[1] - anim_data.anim_time[0]
            if clip_data.loop and time > anim_length:
                time %= anim_length
            elif time > anim_length:
                time = anim_length

            time += anim_data.anim_time[0]

            last_active_curve_node = self._asset_datas.get(asset_prim, None)
            if last_active_curve_node != anim_data.curve_node:
                if last_active_curve_node is not None and last_active_curve_node:
                    last_active_curve_node.set_disabled(True)

            anim_data.curve_node.set_disabled(False)
            self._asset_datas[asset_prim] = anim_data.curve_node

            time_attr = anim_data.curve_node.get_attribute(time_input_name)
            if time_attr:
                time_attr.set(time)

    def _on_update_sound_prim(self, sound: OmniAudioSchema.Sound, clip_data) -> typing.Tuple[Sdf.Path]:
        sound.GetStartTimeAttr().Set(clip_data.startTime)
        sound.GetEndTimeAttr().Set(clip_data.endTime)
        sound.GetTimeScaleAttr().Set(clip_data.playRate)

        # TODO: mediaoffsets fixed in kit 104 (OM-49369)
        # offset_start = attrs[SequenceSchema.Tokens.playOffset]
        # if math.isnan(offset_start):
        #     offset_start = 0
        # timecodes_per_second = g_timeline_interface().get_time_codes_per_seconds()
        # media_offset_start = (start_time + offset_start) / timecodes_per_second
        # sound.GetMediaOffsetStartAttr().Set(media_offset_start)

        # # TODO: mediaoffsets fixed in kit 104 (OM-49369)
        # offset_end = attrs[SequenceSchema.Tokens.playEnd]
        # if math.isnan(offset_end):
        #     offset_end = 0
        # media_offset_end = offset_end / timecodes_per_second
        # sound.GetMediaOffsetEndAttr().Set(media_offset_end)

        sound.GetLoopCountAttr().Set(-1 if clip_data.loop else 0)

        return [
            sound.GetStartTimeAttr().GetPath(),
            sound.GetEndTimeAttr().GetPath(),
            sound.GetTimeScaleAttr().GetPath(),
            sound.GetLoopCountAttr().GetPath(),
        ]

    @staticmethod
    def _get_update_node_index(name: str) -> typing.Optional[int]:
        update_nodes = g_stage_update_interface().get_stage_update_nodes()
        for node in update_nodes:
            index = node.get("index")
            node_name = node.get("name")
            if node_name == name:
                return index
        return None

    def suspend(self):
        index = self._get_update_node_index(UPDATE_NODE_ID)
        if index is None:
            carb.log_warn(f"Could not find the stage update node index for id {UPDATE_NODE_ID}.")
            return
        g_stage_update_interface().set_stage_update_node_enabled(index, False)

    def resume(self):
        index = self._get_update_node_index(UPDATE_NODE_ID)
        if index is None:
            carb.log_warn(f"Could not find the stage update node index for id {UPDATE_NODE_ID}.")
            return
        g_stage_update_interface().set_stage_update_node_enabled(index, True)

    @staticmethod
    def _is_visible(time_code, prim):
        imageable = UsdGeom.Imageable(prim)
        if time_code is None:
            time_code = Usd.TimeCode.Default()

        visibility = imageable.ComputeVisibility(time_code)
        return visibility != UsdGeom.Tokens.invisible

    def _on_camera_switch_value_change(self, value_model: ui.SimpleBoolModel):
        g_settings().set(USE_SEQUENCER_CAMERA, value_model.as_bool)
        if not value_model.as_bool:
            self._reset_camera()

    def _on_camera_switch_setting_change(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.DESTROYED:
            self._camera_switching_enabled.set_value(False)
            self._previous_camera_path = None
            self._last_camera_pair = None
        else:
            # WTF carb dictionary item?
            self._camera_switching_enabled.set_value(item.get_dict())

    def _reset_camera(self):
        self._last_camera_pair = None
        if not self._previous_camera_path:
            return
        viewport = vp_util.get_active_viewport()
        if not viewport:
            return
        viewport.set_active_camera(self._previous_camera_path.pathString)
        self._previous_camera_path = None

    def is_camera_active(self, time_code, camera):
        return self._is_visible(time_code, camera.GetPrim())

    def cache_anim(self, prim: Usd.Prim) -> typing.Optional[Sdf.Layer]:
        stage = omni.usd.get_context().get_stage()
        if not stage:
            return None

        self._refresh_stage(stage)

        return self._value_clip_baker.CacheAnimation(prim)

    def _refresh_stage(self, stage):
        if self._value_clip_baker is None or self._value_clip_baker.GetStage() != stage:
            self._reset_stage_data()
            self._value_clip_baker = SequenceSchema.ValueClipBaker(stage)
            self._camera_cache = SequenceSchema.CameraCache(stage)

    async def async_update(self, current):
        self._on_update(current, None)

    def _on_update(self, current, elapsed):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            return

        time_code = current * stage.GetTimeCodesPerSecond()

        self._refresh_stage(stage)
        self._value_clip_baker.Update(time_code)

        # Switch camera
        if self._camera_switching_enabled.as_bool:
            # On update - we only change camera if camera cache has changed for this time_code
            camera = self._camera_cache.GetCurrentCamera(time_code)
            camera_time_pair = (camera.GetPath(), time_code)
            if camera_time_pair != self._last_camera_pair:
                if camera and self.is_camera_active(time_code, camera):
                    self._do_camera_switch(time_code, camera.GetPath())
                self._last_camera_pair = camera_time_pair

    def _do_camera_switch(self, time_code: float, camera_path: Sdf.Path):
        viewport = vp_util.get_active_viewport()
        if viewport:
            current_camera_path = viewport.get_active_camera()
            if current_camera_path == camera_path:
                return
            viewport.set_active_camera(camera_path.pathString)

            # Save off the camera so we can reset when disabling camera switching.
            if self._previous_camera_path is None:
                self._previous_camera_path = current_camera_path


g_sequence_player = _Player()
