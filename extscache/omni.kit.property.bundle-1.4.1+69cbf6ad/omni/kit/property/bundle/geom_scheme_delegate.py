"""Provides a property scheme delegate for building widget schemes based on USD geometric primitives."""

from omni.kit.window.property.property_scheme_delegate import PropertySchemeDelegate
from pxr import UsdGeom, UsdLux, UsdMedia, UsdSkel


class GeomPrimSchemeDelegate(PropertySchemeDelegate):
    """A delegate class that provides widget building schemes for geometric primitives in a property window.

    This class extends the PropertySchemeDelegate and overrides methods to determine the appropriate widgets to display or hide, based on the type of USD geometric primitives encountered. The widget construction is primarily guided by the type of the USD primitive provided in the payload, such as UsdGeom.Mesh, UsdGeom.Camera, or UsdLux.Light among others. It caters to both the inclusion of relevant widgets and the exclusion of irrelevant or unwanted widgets for a given primitive.
    """

    def get_widgets(self, payload):
        """Determines widgets to build based on the given payload.

        Args:
            payload (dict): Payload containing stage and prim paths to determine widgets.

        Returns:
            list: A list of widget names to be built."""
        widgets_to_build = []
        anchor_prim = None

        stage = payload.get_stage()
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if not prim.IsA(UsdGeom.Imageable):
                        return widgets_to_build
                    anchor_prim = prim

        if anchor_prim is None:
            return widgets_to_build

        have_audio_schema = False
        try:
            import OmniAudioSchema

            have_audio_schema = True
        except ModuleNotFoundError:
            pass

        if (
            anchor_prim
            and anchor_prim.IsA(UsdMedia.SpatialAudio)
            or anchor_prim.IsA(UsdMedia.SpatialAudio if not have_audio_schema else OmniAudioSchema.OmniSound)
            or anchor_prim.IsA(UsdMedia.SpatialAudio if not have_audio_schema else OmniAudioSchema.OmniListener)
        ):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("media")
            widgets_to_build.append("audio_sound")
            if have_audio_schema:
                widgets_to_build.append("audio_listener")
                widgets_to_build.append("audio_settings")
            widgets_to_build.append("kind")

        elif anchor_prim and anchor_prim.IsA(UsdSkel.Root):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("behavior_agent_api")
            widgets_to_build.append("anim_graph_api")
            widgets_to_build.append("omni_graph_api")
            widgets_to_build.append("omni_scripting_api")
            widgets_to_build.append("kind")

        elif anchor_prim.IsA(UsdSkel.Skeleton):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("control_rig")
            widgets_to_build.append("skel_animation")

        elif anchor_prim and anchor_prim.IsA(UsdGeom.Camera):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("camera")
            widgets_to_build.append("geometry_imageable")
            widgets_to_build.append("kind")

        # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
        elif anchor_prim and (
            (hasattr(UsdLux, "LightAPI") and anchor_prim.HasAPI(UsdLux.LightAPI))
            or ((hasattr(UsdLux, "Light") and anchor_prim.IsA(UsdLux.Light)))
        ):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("light")
            widgets_to_build.append("geometry_imageable")
            widgets_to_build.append("kind")

        elif anchor_prim and anchor_prim.IsA(UsdGeom.Scope):
            widgets_to_build.append("path")
            widgets_to_build.append("behavior_motion_library")
            widgets_to_build.append("geometry_imageable")
            widgets_to_build.append("kind")

        elif anchor_prim and anchor_prim.IsA(UsdGeom.Mesh):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("material_binding")
            widgets_to_build.append("behavior_interactive_object_api")
            widgets_to_build.append("navmesh_obstacle_api")
            widgets_to_build.append("navmesh_exclude_api")
            widgets_to_build.append("navmesh_area_api")
            widgets_to_build.append("mesh_skel_binding")
            widgets_to_build.append("geometry")
            widgets_to_build.append("geometry_imageable")
            widgets_to_build.append("kind")

        elif anchor_prim and anchor_prim.IsA(UsdGeom.Xform):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("material_binding")
            widgets_to_build.append("geometry_imageable")
            widgets_to_build.append("kind")

        elif anchor_prim and anchor_prim.IsA(UsdGeom.Xformable):
            widgets_to_build.append("path")
            widgets_to_build.append("transform")
            widgets_to_build.append("material_binding")
            widgets_to_build.append("behavior_interactive_object_api")
            widgets_to_build.append("navmesh_volume")
            widgets_to_build.append("navmesh_obstacle_api")
            widgets_to_build.append("navmesh_exclude_api")
            widgets_to_build.append("navmesh_area_api")
            widgets_to_build.append("geometry")
            widgets_to_build.append("geometry_imageable")
            widgets_to_build.append("kind")

        return widgets_to_build

    def get_unwanted_widgets(self, payload):
        """Identifies unwanted widgets for removal based on the given payload.

        Args:
            payload (dict): Payload containing stage and prim paths to identify unwanted widgets.

        Returns:
            list: A list of unwanted widget names."""
        unwanted_widgets_to_build = []
        anchor_prim = None

        stage = payload.get_stage()
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if not prim.IsA(UsdGeom.Imageable):
                        return unwanted_widgets_to_build
                    anchor_prim = prim

        if anchor_prim is None:
            return unwanted_widgets_to_build

        have_audio_schema = False
        try:
            import OmniAudioSchema

            have_audio_schema = True
        except ModuleNotFoundError:
            pass

        if anchor_prim and anchor_prim.IsA(UsdGeom.Scope):
            unwanted_widgets_to_build.append("transform")
            unwanted_widgets_to_build.append("geometry")
            unwanted_widgets_to_build.append("kind")

        # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
        elif anchor_prim and (
            (hasattr(UsdLux, "LightAPI") and anchor_prim.HasAPI(UsdLux.LightAPI))
            or ((hasattr(UsdLux, "Light") and anchor_prim.IsA(UsdLux.Light)))
        ):
            unwanted_widgets_to_build.append("geometry")

        elif (
            anchor_prim
            and anchor_prim.IsA(UsdMedia.SpatialAudio)
            or anchor_prim.IsA(UsdMedia.SpatialAudio if not have_audio_schema else OmniAudioSchema.Sound)
            or anchor_prim.IsA(UsdMedia.SpatialAudio if not have_audio_schema else OmniAudioSchema.Listener)
        ):
            unwanted_widgets_to_build.append("geometry_imageable")

        elif anchor_prim and anchor_prim.IsA(UsdSkel.Skeleton) or anchor_prim.IsA(UsdSkel.Root):
            unwanted_widgets_to_build.append("geometry")
            unwanted_widgets_to_build.append("geometry_imageable")

        return unwanted_widgets_to_build
