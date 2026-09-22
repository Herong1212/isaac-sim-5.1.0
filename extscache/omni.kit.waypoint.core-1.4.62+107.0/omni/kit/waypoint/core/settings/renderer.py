import carb
from pxr import Usd

from .abstract_setting import AbstractWaypointSetting

WAYPOINT_ATTR_RENDERER = "render"


class RendererSetting(AbstractWaypointSetting):
    def __init__(self, edit_context: Usd.EditContext = None):
        super().__init__(edit_context)
        # Temporarily disable the properties in waypoint
        """
        self._render_param_paths = [
            "/rtx/pathtracing/maxBounces",  # 0
            "/rtx/pathtracing/maxSpecularAndTransmissionBounces",  # 1
            "/rtx/pathtracing/totalSpp",  # 2
            "/rtx/rendermode",  # 3
            "/app/renderer/resolution/multiplier",  # 4
            "/app/renderer/resolution/width",  # 5
            "/app/renderer/resolution/height",  # 6
            "/app/renderer/gpuSynchronization",  # 7
            "/rtx/shadows/denoiser/quarterRes",  # 8
            "/rtx/sceneDb/ambientLightColor",  # 9
            "/rtx/sceneDb/ambientLightIntensity",  # 10
            "/rtx/ambientOcclusion/rayLength",  # 11
            "/rtx/reflections/halfRes",  # 12
            "/rtx/reflections/maxReflectionBounces",  # 13
            "/rtx/translucency/reflectionCutoff",  # 14
            "/rtx/pathtracing/mgpu/enabled",  # 15
            "/renderer/eco_mode_enable",  # 16
            "/rtx/post/tonemap/op",  # 17
            "/rtx/post/colorcorr/enabled",  # 18
            "/rtx/post/colorcorr/outputMode",  # 19
            "/rtx/post/colorgrad/enabled",  # 20
            "/rtx/post/colorgrad/outputMode",  # 21
            "/rtx/reflections/enabled",  # 22
            "/rtx/shadows/enabled",  # 23
            "/rtx/translucency/enabled",  # 24
            "/rtx/ambientOcclusion/enabled",  # 25
            "/rtx/ambientOcclusion/temporalSqrtLength",  # 26
            "/rtx/indirectDiffuse/enabled",  # 27
            "/rtx/post/lensFlares/enabled",  # 28
            "/rtx/post/lensFlares/flareScale",  # 29
            "/rtx/post/chromaticAberration/enabled",  # 30
            "/rtx/post/chromaticAberration/strengthR",  # 31
            "/rtx/post/chromaticAberration/strengthG",  # 32
            "/rtx/post/chromaticAberration/strengthB",  # 33
            "/rtx/post/histogram/enabled",  # 34
            "/rtx/domeLight/baking/resolution",  # 35
            "/rtx/post/dof/enabled",  # 36
            "/rtx/post/dof/overrideEnabled",  # 37
            "/rtx/post/dof/viewUIEnabled",  # 38
            "/rtx/post/aa/op",  # 39
            "/rtx/directLighting/sampledLighting/enabled",  # 40
            "/rtx/directLighting/sampledLighting/samplesPerPixel",  # 41
            "/rtx/reflections/sampledLighting/enabled",  # 42
            "/rtx/indirectDiffuse/enabled",  # 43
            "/rtx/raytracing/cached/enabled",  # 44
            "/rtx/reflections/halfRes",  # 45
            "/rtx/renderpreset"  # Additional 1
        ]
        # """
        self._render_param_paths = ["/rtx/renderpreset"]
        self._settings = carb.settings.get_settings()

    def get_name(self):
        return "Render Settings"

    def is_dirty(self):
        if not self.valid:
            return False

        for param in self._render_param_paths:
            value = self._settings.get(param)
            if param in self._data:
                if not self.equal_data(value, self._data[param]):
                    return True
            elif value is not None:
                return True
        return False

    def create(self, valid: bool = True):
        super().create(valid)
        if not valid:
            return

        # Collect data from render settings
        self._data.clear()
        for param in self._render_param_paths:
            value = self._settings.get(param)
            if value is not None:
                self._data[param] = value

    def recall(self, prim: Usd.Prim):
        if not self.valid:
            return
        # Pull/apply current data to renderer/settingsd
        """
        # Temporarily disable renderer properties recall
        rtx_render_mode = self._settings.get("/rtx/rendermode")
        if rtx_render_mode != self._data["/rtx/rendermode"]:
            if self._data["/rtx/rendermode"] == "iray":
                # Entering iray renderer
                iv = omni.kit.viewport.acquire_viewport_interface()
                if iv:
                    viewport_window = iv.get_viewport_window(None)
                    viewport_window.set_active_hydra_engine("iray")
            elif rtx_render_mode == "iray":
                # Leaving iray renderer
                iv = omni.kit.viewport.acquire_viewport_interface()
                if iv:
                    viewport_window = iv.get_viewport_window(None)
                    # viewport_window.set_active_hydra_engine("rtx")
                    viewport_window.set_active_hydra_engine("rtx")
        """

        for param in self._render_param_paths:
            value = self._data.get(param)
            if value:
                self._settings.set(param, value)

    def save_to_usd(self, prim: Usd.Prim) -> None:
        self._save_data_to_usd(prim, WAYPOINT_ATTR_RENDERER)

    def load_from_usd(self, prim: Usd.Prim) -> bool:
        return self._load_data_from_usd(prim, WAYPOINT_ATTR_RENDERER)
