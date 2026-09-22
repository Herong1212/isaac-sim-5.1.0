# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['LegacyGridScene', 'LegacyLightScene', 'LegacyAudioScene']

import carb
from carb.eventdispatcher import get_eventdispatcher
import omni.usd
from pxr import UsdGeom


class LegacyGridScene:
    AUTO_TRACK_PATH = '/app/viewport/grid/trackCamera'

    def __init__(self, desc: dict, *args, **kwargs):
        self.__vc_change = None
        self.__viewport_grid_vis_sub = None
        self.__auto_track_sub = None
        self.__usd_context_name = desc['usd_context_name']
        self.__viewport_api = desc.get('viewport_api')
        self.__persp_grid = None
        self.__last_grid = None
        self.__stage_sub = None

        settings = carb.settings.get_settings()

        self.__viewport_grid_vis_sub = settings.subscribe_to_node_change_events(
            f"/persistent/app/viewport/{self.__viewport_api.id}/guide/grid/visible",
            self.__viewport_grid_display_changed
        )

        self.__auto_track_sub = settings.subscribe_to_node_change_events(
            "/app/viewport/grid/trackCamera",
            self.__auto_track_changed
        )

        self.__viewport_grid_display_changed(None, carb.settings.ChangeEventType.CHANGED)
        self.__auto_track_changed()

    def __setup_view_tracking(self):
        if self.__vc_change:
            return

        self.__persp_grid = 'XZ'
        self.__last_grid = None
        self.__on_stage_opened(self.stage)
        self.__stage_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.viewport.window:legacy",
            event_name=self.usd_context.stage_event_name(omni.usd.StageEventType.OPENED),
            on_event=lambda _: self.__on_stage_opened(self.stage)
        )
        self.__vc_change = self.__viewport_api.subscribe_to_view_change(self.__view_changed)

    def __destroy_view_tracking(self, settings):
        self.__stage_sub = None
        if self.__vc_change:
            self.__vc_change.destroy()
            self.__vc_change = None

    @property
    def usd_context(self):
        return omni.usd.get_context(self.__usd_context_name)

    @property
    def stage(self):
        return self.usd_context.get_stage()

    def __auto_track_changed(self, *args, **kwargs):
        settings = carb.settings.get_settings()
        if settings.get(self.AUTO_TRACK_PATH):
            self.__destroy_view_tracking(settings)
        else:
            self.__setup_view_tracking()

    def __set_grid(self, grid: str):
        if self.__last_grid != grid:
            self.__last_grid = grid
            carb.settings.get_settings().set('/app/viewport/grid/plane', grid)

    def __on_stage_opened(self, stage):
        up_axis = UsdGeom.GetStageUpAxis(stage).upper() if stage else None
        if up_axis == UsdGeom.Tokens.z:
            self.__persp_grid = 'XY'
        elif up_axis == UsdGeom.Tokens.x:
            self.__persp_grid = 'YZ'
        else:
            self.__persp_grid = 'XZ'

    def __view_changed(self, viewport_api):
        is_ortho = viewport_api.projection[3][3] == 1
        if is_ortho:
            ortho_dir = viewport_api.transform.TransformDir((0, 0, 1))
            ortho_dir = [abs(v) for v in ortho_dir]
            if ortho_dir[1] > ortho_dir[0] and ortho_dir[1] > ortho_dir[2]:
                self.__set_grid('XZ')
            elif ortho_dir[2] > ortho_dir[0] and ortho_dir[2] > ortho_dir[1]:
                self.__set_grid('XY')
            else:
                self.__set_grid('YZ')
        else:
            self.__on_stage_opened(viewport_api.stage)
            self.__set_grid(self.__persp_grid)

    def __viewport_grid_display_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            key = f"/persistent/app/viewport/{self.__viewport_api.id}/guide/grid/visible"
            self.visible = bool(carb.settings.get_settings().get(key))

    @property
    def name(self):
        return 'Grid (legacy)'

    @property
    def categories(self):
        return ['guide']

    @property
    def visible(self):
        return carb.settings.get_settings().get('/app/viewport/grid/enabled')

    @visible.setter
    def visible(self, value):
        carb.settings.get_settings().set('/app/viewport/grid/enabled', bool(value))
        return self.visible

    def destroy(self):
        settings = carb.settings.get_settings()
        self.__destroy_view_tracking(settings)
        if self.__viewport_grid_vis_sub is not None:
            settings.unsubscribe_to_change_events(self.__viewport_grid_vis_sub)
            self.__viewport_grid_vis_sub = None
        if self.__auto_track_sub is not None:
            settings.unsubscribe_to_change_events(self.__auto_track_sub)
            self.__auto_track_sub = None


class LegacyLightScene:
    def __init__(self, *args, **kwargs):
        carb.settings.get_settings().set_default('/app/viewport/show/lights', True)

    @property
    def name(self):
        return 'Lights (legacy)'

    @property
    def categories(self):
        return ['scene']

    @property
    def visible(self):
        return carb.settings.get_settings().get('/app/viewport/show/lights')

    @visible.setter
    def visible(self, value):
        carb.settings.get_settings().set('/app/viewport/show/lights', bool(value))
        return self.visible

    def destroy(self):
        pass


class LegacyAudioScene:
    def __init__(self, *args, **kwargs):
        carb.settings.get_settings().set_default('/app/viewport/show/audio', True)

    @property
    def name(self):
        return 'Audio (legacy)'

    @property
    def categories(self):
        return ['scene']

    @property
    def visible(self):
        return carb.settings.get_settings().get('/app/viewport/show/audio')

    @visible.setter
    def visible(self, value):
        carb.settings.get_settings().set('/app/viewport/show/audio', bool(value))
        return self.visible

    def destroy(self):
        pass
