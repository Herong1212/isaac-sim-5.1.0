__all__ = ["StageFilterButton"]

from functools import partial
from typing import Optional
import carb.settings
from pxr import UsdGeom, UsdSkel, UsdLux, UsdShade, UsdPhysics
from omni.kit.widget.filter import FilterButton
from omni.kit.widget.options_menu import OptionItem, OptionSeparator


class StageFilterButton(FilterButton):
    """
    Filter button used in stage widget.

    Args:
        filter_provider: Provider where filter functions defined. Use stage widget.
    """
    def __init__(self, filter_provider):
        self.__filter_provider = filter_provider

        settings = carb.settings.get_settings()
        filter_flattener = settings.get("/exts/omni.kit.widget.stage/filter/flattener")
        filter_physics = settings.get("/exts/omni.kit.widget.stage/filter/physics")

        items = [
            OptionItem("Hidden", on_value_changed_fn=self._filter_by_visibility),
            OptionItem("Inactive", on_value_changed_fn=self._filter_by_active_state),
            OptionItem("Undefined", on_value_changed_fn=self._filter_by_def_state),
            OptionItem("Abstract", on_value_changed_fn=self._filter_by_abstract_state),
            OptionSeparator(),

            OptionItem("Animations", on_value_changed_fn=partial(self._filter_by_type, UsdSkel.Animation)),
            OptionItem("Audio", on_value_changed_fn=self.__filter_optional_audio),
            OptionItem("Cameras", on_value_changed_fn=partial(self._filter_by_type, UsdGeom.Camera)),
            # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
            OptionItem(
                "Lights",
                on_value_changed_fn=partial(self._filter_by_api_type, UsdLux.LightAPI) if hasattr(UsdLux, 'LightAPI') else partial(self._filter_by_type, UsdLux.Light)
            ),
            OptionItem("Materials",on_value_changed_fn=partial(self._filter_by_type, [UsdShade.Material, UsdShade.Shader])),
            OptionItem("Meshes", on_value_changed_fn=partial(self._filter_by_type, UsdGeom.Mesh)),
            OptionItem("Skeletons", on_value_changed_fn=partial(self._filter_by_type, UsdSkel.Skeleton)),
            OptionItem("Skeleton Roots", on_value_changed_fn=partial(self._filter_by_type, UsdSkel.Root)),
            OptionItem("Xforms", on_value_changed_fn=partial(self._filter_by_type, UsdGeom.Xform)),
        ]

        if filter_flattener:
            items.extend(
                [
                    OptionSeparator(),
                    OptionItem("Material Flattener Base Meshes", on_value_changed_fn=self._filter_by_flattener_basemesh),
                    OptionItem("Material Flattener Decals", on_value_changed_fn=self._filter_by_flattener_decal),
                ]
            )

        if filter_physics:
            items.extend(
                [
                    OptionSeparator(),
                    OptionItem("Physics Articulation Roots",on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.ArticulationRootAPI)),
                    OptionItem("Physics Colliders", on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.CollisionAPI)),
                    OptionItem("Physics Collision Groups", on_value_changed_fn=partial(self._filter_by_type, UsdPhysics.CollisionGroup)),
                    OptionItem("Physics Filtered Pairs", on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.FilteredPairsAPI)),
                    OptionItem("Physics Joints", on_value_changed_fn=partial(self._filter_by_type, UsdPhysics.Joint)),
                    OptionItem("Physics Drives", on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.DriveAPI)),
                    OptionItem("Physics Materials", on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.MaterialAPI)),
                    OptionItem("Physics Mass", on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.MassAPI)),
                    OptionItem("Physics Rigid Bodies", on_value_changed_fn=partial(self._filter_by_api_type, UsdPhysics.RigidBodyAPI)),
                    OptionItem("Physics Scenes", on_value_changed_fn=partial(self._filter_by_type, UsdPhysics.Scene)),
                ]
            )

        super().__init__(items, width=20, height=20)

    def enable_filters(self, usd_type_list: list) -> list:
        """
        Enable filters.

        Args:
            usd_type_list (list): List of usd types to be enabled.

        Returns:
            returns usd types not supported
        """
        self.model.reset()
        unknown_usd_types = []
        for usd_type in usd_type_list:
            name = None
            if usd_type == UsdSkel.Animation:
                name = "Animations"
            elif usd_type == UsdGeom.Camera:
                name = "Cameras"
            # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
            elif (hasattr(UsdLux, 'LightAPI') and usd_type == UsdLux.LightAPI) or (hasattr(UsdLux, 'Light') and usd_type == UsdLux.Light):
                name = "Lights"
            elif usd_type == UsdShade.Material or usd_type == UsdShade.Shader:
                name = "Materials"
            elif usd_type == UsdGeom.Mesh:
                name = "Meshes"
            elif usd_type == UsdGeom.Xform:
                name = "Xforms"
            elif usd_type == UsdSkel.Skeleton:
                name = "Skeletons"
            elif usd_type == UsdSkel.Root:
                name = "Skeleton Roots"
            elif usd_type == UsdPhysics.ArticulationRootAPI:
                name = "Physics Articulation Roots"
            elif usd_type == UsdPhysics.CollisionAPI:
                name = "Physics Colliders"
            elif usd_type == UsdPhysics.CollisionGroup:
                name = "Physics Collision Groups"
            elif usd_type == UsdPhysics.FilteredPairsAPI:
                name = "Physics Filtered Pairs"
            elif usd_type == UsdPhysics.Joint:
                name = "Physics Joints"
            elif usd_type == UsdPhysics.DriveAPI:
                name = "Physics Drives"
            elif usd_type == UsdPhysics.MaterialAPI:
                name = "Physics Materials"
            elif usd_type == UsdPhysics.MassAPI:
                name = "Physics Mass"
            elif usd_type == UsdPhysics.RigidBodyAPI:
                name = "Physics Rigid Bodies"
            elif usd_type == UsdPhysics.Scene:
                name = "Physics Scenes"

            if not name:
                try:
                    import OmniAudioSchema
                    if usd_type == OmniAudioSchema.OmniSound:
                        name = "Audio"
                except ModuleNotFoundError:
                    pass

            item = self._get_item(name) if name else None
            if item:
                item.value = True
            else:
                unknown_usd_types.append(usd_type)

        # If there is any unknow usd types, unhide filter button
        if unknown_usd_types and self.button:
            self.button.visible = False

        return unknown_usd_types

    def _filter_by_visibility(self, enabled):
        """Filter Hidden On/Off"""
        self.__filter_provider._filter_by_visibility(enabled)

    def _filter_by_active_state(self, enabled):
        """Filter Active On/Off"""

        self.__filter_provider._filter_by_active_state(enabled)

    def _filter_by_def_state(self, enabled):
        """Filter Def On/Off"""

        self.__filter_provider._filter_by_def_state(enabled)
    
    def _filter_by_abstract_state(self, enabled):
        """Filter Abstract On/Off"""

        self.__filter_provider._filter_by_abstract_state(enabled)

    def __filter_optional_audio(self, enabled):
        try:
            import OmniAudioSchema
            return self._filter_by_type(OmniAudioSchema.OmniSound, enabled)
        except ModuleNotFoundError:
            pass
        return False

    def _filter_by_type(self, usd_types, enabled):
        """
        Set filtering by USD type.

        Args:
            usd_types: The type or the list of types it's necessary to add or remove from filters.
            enabled: True to add to filters, False to remove them from the filter list.
        """
        self.__filter_provider._filter_by_type(usd_types, enabled)

    def _filter_by_api_type(self, api_types, enabled):
        """
        Set filtering by USD api type.

        Args:
            api_types: The api type or the list of types it's necessary to add or remove from filters.
            enabled: True to add to filters, False to remove them from the filter list.
        """
        self.__filter_provider._filter_by_api_type(api_types, enabled)

    def _filter_by_flattener_basemesh(self, enabled):
        self.__filter_provider._filter_by_flattener_basemesh(enabled)

    def _filter_by_flattener_decal(self, enabled):
        self.__filter_provider._filter_by_flattener_decal(enabled)

    def _get_item(self, name: str) -> Optional[OptionItem]:
        for item in self.model.get_item_children():
            if item.name == name:
                return item
        return None
