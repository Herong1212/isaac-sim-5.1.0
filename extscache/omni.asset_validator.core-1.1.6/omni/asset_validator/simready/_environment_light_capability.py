# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["EnvironmentLightCapabilityChecker"]

from dataclasses import dataclass, field

from omni.asset_validator.core import BaseRuleChecker, is_omni_path
from pxr import Sdf, Usd, UsdGeom, UsdLux, UsdShade


@dataclass(frozen=True)
class SimPbrAttributesInfo:
    # If True, the SimPBR material/shader has emissiveness turned on
    emissive: bool = field(default=False)


class EnvironmentLightCapabilityChecker(BaseRuleChecker):
    """
    Validates the following environment light rules found in the **AV Sim Specification: Creators**:

    - The asset must have at least one "light bulb" in the form of a ``UsdLux`` prim or ``Mesh`` prim with a binding to a ``SimPBR`` material that has its emissive properties turned on.

    - **4.0.C4.03** (Optional):

      To control their behavior at runtime based on the global Time of Day setting, they must have the ``TimeOfDay`` behavior attribute.
    """

    # A light or mesh wih this attribute represent a street light bulb.
    BEHAVIORS_ATTR_NAME = "omni:simready:behaviors"
    BEHAVIORS_ATTR_VALUE = ["TimeOfDay"]
    # The list of supported Sim BPR shaders
    SIM_PBR_SHADERS = ["OmniGlass.mdl", "OmniPBR.mdl", "SimPBR.mdl", "SimPBR_Translucent.mdl"]

    def CheckStage(self, usdStage: Usd.Stage):
        """
        Overwrites BaseRuleChecker.CheckStage.
        """
        if default_prim := usdStage.GetDefaultPrim():
            if not self._parse_light_bulbs(default_prim):
                self._AddFailedCheck(
                    "Invalid environment light: no light bulbs found.",
                    at=usdStage,
                )
        else:
            self._AddFailedCheck(
                "Invalid environment light: missing default prim.",
                at=usdStage,
            )

    def _parse_light_bulbs(self, start_prim: Usd.Stage) -> bool:
        """
        Parses the environment light bulbs from the stage.
        Returns True if at least one light bulb is found, false otherwise.
        """
        # Traverse the prims under the default prim to find all
        # UsdLux lights and Mesh prims with a signal attribute (signal groups)
        light_bulbs: list[Usd.Prim] = []
        prim_range_iter = iter(Usd.PrimRange(start_prim, Usd.TraverseInstanceProxies()))
        for prim in prim_range_iter:
            # Skip Omniverse specific prims
            if is_omni_path(prim.GetPath()):
                prim_range_iter.PruneChildren()
            # Get the "light builb" attribute
            attr: Usd.Attribute = prim.GetAttribute(self.BEHAVIORS_ATTR_NAME)
            if attr and self._check_light_bulb(prim, attr):
                light_bulbs.append(prim)
        return len(light_bulbs) > 0

    def _check_light_bulb(self, prim: Usd.Prim, attr: Usd.Attribute) -> bool:
        """
        Checks if the prim is a "light bulb" by looking at its attributes.
        """
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        is_mesh_bulb: bool = self._is_render_or_default_mesh(mesh)
        is_light: bool = self._is_light(prim)
        if not is_light:
            if not mesh:
                # Prim is neither a UsdLux light nor a Mesh
                self._AddWarning(
                    f"Attribute '{self.BEHAVIORS_ATTR_NAME}' not expected on prim of type {prim.GetTypeName()}. "
                    "Only prims of type UsdLux or Meshes with default or render purpose are expected to have this attribute.",
                    at=prim,
                )
                return False
            elif not is_mesh_bulb:
                # Prim is a mesh with an invalid purpose
                self._AddFailedCheck(
                    f"Mesh with attribute '{self.BEHAVIORS_ATTR_NAME}' must have render purpose 'default' or 'render'. "
                    "The mesh will be ignored.",
                    at=prim,
                )
                return False
        # There's a "lighgt bulb" (either a light or a mesh prim)
        # Validate the attribute
        if not self._validate_behavior_attr(attr):
            return False
        # Validate the mesh "light bulb"
        if is_mesh_bulb and not self._validate_mesh_bulb(mesh):
            return False
        return True

    def _validate_behavior_attr(self, attr: Usd.Attribute) -> bool:
        """Validates the {self.BEHAVIORS_ATTR_NAME} attribute.
        Returns True if the attribute is valid, False otherwise.
        """
        if attr.GetTypeName() != Sdf.ValueTypeNames.TokenArray:
            self._AddFailedCheck(
                f"Attribute has invalid type {attr.GetTypeName()}. Expected: {Sdf.ValueTypeNames.TokenArray}",
                at=attr,
            )
            return False
        if attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                "Attribute cannot be time varying.",
                at=attr,
            )
            return False
        attr_value: str = attr.Get()
        if attr_value != self.BEHAVIORS_ATTR_VALUE:
            self._AddFailedCheck(
                f"Invalid attribute value: '{attr_value}'. Expected: {self.BEHAVIORS_ATTR_VALUE}",
                at=attr,
            )
            return False
        return True

    def _validate_mesh_bulb(self, mesh: UsdGeom.Mesh) -> bool:
        """Checks that the prim is a Mesh bound to a material with emissive properties"""
        if not mesh:
            return False
        # Mesh must have a material bound to it
        material, _ = self._get_material(mesh.GetPrim())
        if not material:
            self._AddFailedCheck(
                message="Invalid environment light: no materials found on mesh used as light.",
                at=mesh.GetPrim(),
            )
            return False
        # Mesh must have simpbr shader
        simpbr_attr_info: SimPbrAttributesInfo | None = self._get_sim_pbr_shader_info(material)
        if not simpbr_attr_info:
            self._AddFailedCheck(
                message=f"Invalid environment light: material bound to mesh used as light must use one of the supported shaders {self.SIM_PBR_SHADERS}.",
                at=material.GetPrim(),
            )
            return False
        # Mesh's material must have emissive properties turned on
        if not simpbr_attr_info.emissive:
            self._AddFailedCheck(
                message="Invalid environment light: material bound to mesh mesh used as light does not have emissiveness turned on.",
                at=material.GetPrim(),
            )
            return False
        return True

    @staticmethod
    def _is_input_attr_enabled(shader: UsdShade.Shader, attr_name: str) -> bool:
        attr_shader_input = shader.GetInput(attr_name)
        if not attr_shader_input:
            return False
        attr = attr_shader_input.GetAttr()
        time_samples = attr.GetTimeSamples() or [Usd.TimeCode.EarliestTime()]
        return any(attr.Get(time) for time in time_samples)

    @staticmethod
    def _get_surface_shader(material: UsdShade.Material) -> UsdShade.Shader:
        # An MDL is authored to either the mdl render context OR if and only if the mdl render context is unauthored,
        # the universal render context
        if not material:
            return UsdShade.Shader()
        surface_output = material.GetSurfaceOutput("mdl") or material.GetSurfaceOutput()
        if not surface_output:
            return UsdShade.Shader()
        connection_source = surface_output.GetConnectedSource()
        if not connection_source:
            return UsdShade.Shader()
        return UsdShade.Shader(connection_source[0])

    def _get_sim_pbr_shader_info(self, material: UsdShade.Material) -> SimPbrAttributesInfo | None:
        """Check the surface shader of the given material if its a sim pbr shader and if it has emissive enabled."""
        shader: UsdShade.Shader = self._get_surface_shader(material)
        if not shader:
            return None
        src_asset: Sdf.AssetPath = shader.GetSourceAsset("mdl")
        if src_asset:
            for shader_name in self.SIM_PBR_SHADERS:
                if src_asset.path.endswith(shader_name):
                    return SimPbrAttributesInfo(self._is_input_attr_enabled(shader, "enable_emission"))
        return None

    @staticmethod
    def _get_material(prim: Usd.Prim) -> tuple[UsdShade.Material, Usd.Relationship]:
        """Returns the computed "full" purpose material and the relationship of the prim/geomSubset."""
        mtl_binding_api = UsdShade.MaterialBindingAPI(prim)
        return mtl_binding_api.ComputeBoundMaterial(materialPurpose=UsdShade.Tokens.full)

    @staticmethod
    def _is_light(prim: Usd.Prim) -> bool:
        """Returns True if the given prim is a UsdLux light."""
        return prim.HasAPI(UsdLux.LightAPI)

    @staticmethod
    def _is_render_or_default_mesh(mesh: UsdGeom.Mesh) -> bool:
        """Returns True if the Mesh has default or renderable purpose."""
        if not mesh:
            return False
        purpose = mesh.ComputePurpose()
        return purpose in (UsdGeom.Tokens.default_, UsdGeom.Tokens.render)
