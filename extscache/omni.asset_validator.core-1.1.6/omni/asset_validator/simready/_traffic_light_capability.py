# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["TrafficLightCapabilityChecker"]

from dataclasses import dataclass, field

from omni.asset_validator.core import BaseRuleChecker, is_omni_path
from pxr import Sdf, Usd, UsdGeom, UsdLux, UsdShade


@dataclass(frozen=True)
class SimPbrAttributesInfo:
    # If True, the SimPBR material/shader has emissiveness turned on
    emissive: bool = field(default=False)


class TrafficLightCapabilityChecker(BaseRuleChecker):
    """
    Validates the following traffic light rules found in the **AV Sim Specification: Creators**:

    - **4.0.C4.04**:

      Traffic signals must have a "directional box" prim identified by the ``signalType`` attribute. "Directional box" prims must have one or more "signal" prim children.

    - **4.0.C4.05**:

      Individual signal prims within a traffic signal asset must have a ``signal`` attribute and must be ``UsdLux`` or renderable ``Mesh`` prims with a computed material that has emissive properties turned on.

    - **4.0.C4.06**:

      Signal names must be one of the following: "amber", "amber_turn", "count", "green", "green_turn", "red", "red_turn".

    - **4.0.C4.07** (Optional):

      A signal intensity domain can be defined on the "directional box" through the ``intensityDomain`` optional attribute.

    - **4.0.C4.08** (Optional):

      A custom signal order can be defined on the "directional box" through the ``signalOrder`` optional attribute.
    """

    # A 'directional box' prim is one that has the following attribute
    SIGNAL_TYPE_ATTR_NAME = "omni:simready:signalType"
    # The signal type attribute must have the following value
    SIGNAL_TYPE_ATTR_VALUE = "trafficLight"

    # A light or mesh wih this attribute represent a 'signal'
    # The value of this attribute should one of the values within
    # the omni:simready:signalOptions array, if present on the 'directional box' prim.
    SIGNAL_ATTR_NAME = "omni:simready:signal"

    # A traffic signal's default prim must have the following attribute
    SIGNAL_ORDER_ATTR_NAME = "omni:simready:signalOrder"
    # The allowed values for the signal attribute
    SIGNAL_VALUES = ["amber", "amber_turn", "count", "green", "green_turn", "red", "red_turn", "walk_green", "walk_red"]

    # The domnain intensity attribute is optional
    DOMAIN_INTENSITY_ATTR_NAME = "omni:simready:signal:domainIntensity"

    # The list of supported Sim BPR shaders
    SIM_PBR_SHADERS = ["OmniGlass.mdl", "OmniPBR.mdl", "SimPBR.mdl", "SimPBR_Translucent.mdl"]

    def CheckStage(self, usdStage: Usd.Stage):
        """
        Overwrites BaseRuleChecker.CheckStage.
        """
        if default_prim := usdStage.GetDefaultPrim():
            if not self._parse_direcional_boxes(default_prim):
                # No directional boxes found, not a traffic light
                self._AddFailedCheck(
                    "Invalid traffic light: no directional boxes found.",
                    at=usdStage,
                )
        else:
            # No default prim
            self._AddFailedCheck(
                "Invalid traffic light: missing default prim.",
                at=usdStage,
            )
            return

    def _parse_direcional_boxes(self, start_prim: Usd.Prim) -> bool:
        """Finds all directional boxes in the stage and validates them.
        Returns true if there is at least one found.
        """
        # The directional boxes in the stage. The key is the prim representing the diretional box.
        # directional_boxes: List[DirectionalBox] = []
        directional_box_count = 0
        prim_range_iter = iter(Usd.PrimRange(start_prim, Usd.TraverseInstanceProxies()))
        for prim in prim_range_iter:
            # Skip Omniverse specific prims
            if is_omni_path(prim.GetPath()):
                prim_range_iter.PruneChildren()
            # Look for directional box prim
            signal_type_attr = prim.GetAttribute(self.SIGNAL_TYPE_ATTR_NAME)
            if signal_type_attr and self._check_signal_type_attr(signal_type_attr):
                # Directional box prim found
                directional_box_count += 1
                # Check the domnain intensity attribute if any
                self._check_domain_intensity_attr(prim)
                # Get the signal order list if any
                signal_order: list[str] = self._parse_signal_order_attr(prim)
                # Parse and validate the signals in the directional box
                self._parse_signals(directional_box=prim, signal_order=signal_order)
                # Children have been visited already
                prim_range_iter.PruneChildren()
        return directional_box_count > 0

    def _check_domain_intensity_attr(self, prim: Usd.Prim):
        """Validates the domain intensity attribute of the directional box prim."""
        domain_intensity_attr: Usd.Attribute = prim.GetAttribute(self.DOMAIN_INTENSITY_ATTR_NAME)
        if not domain_intensity_attr:
            return
        # Is the type valid?
        if domain_intensity_attr.GetTypeName() != Sdf.ValueTypeNames.Float2:
            self._AddFailedCheck(
                f"Attribute has invalid type {domain_intensity_attr.GetTypeName()}. "
                f"Expected: {Sdf.ValueTypeNames.Float2}",
                at=domain_intensity_attr,
            )
            return
        # Is it time varying?
        if domain_intensity_attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                "Attribute cannot be time varying.",
                at=domain_intensity_attr,
            )
            return
        # Are the values of domain intensity valid?
        domain_intensity: list[float] = domain_intensity_attr.Get()
        if domain_intensity and len(domain_intensity) != 2:
            self._AddFailedCheck(
                "Attribute has invalid number of values. Expected 2.",
                at=domain_intensity_attr,
            )
            return
        if domain_intensity[0] > domain_intensity[1]:
            self._AddFailedCheck(
                "Attribute has invalid values. Expected the first value to be less than the second value.",
                at=domain_intensity_attr,
            )

    def _parse_signal_order_attr(self, prim: Usd.Prim) -> list[str]:
        """Reads the signal order attribute from the given prim, and validates it.
        Returns the valid signal orders, an empty list otherwise.
        """
        signal_order_attr: Usd.Attribute = prim.GetAttribute(self.SIGNAL_ORDER_ATTR_NAME)
        if not signal_order_attr:
            # The signal order attribute is optional
            return []
        # Is the type valid?
        if signal_order_attr.GetTypeName() != Sdf.ValueTypeNames.TokenArray:
            self._AddFailedCheck(
                f"Attribute '{self.SIGNAL_ORDER_ATTR_NAME}' has invalid type {signal_order_attr.GetTypeName()}. "
                f"Expected: {Sdf.ValueTypeNames.TokenArray}",
                at=signal_order_attr,
            )
            return []
        # Is it time varying?
        if signal_order_attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                f"Attribute '{self.SIGNAL_ORDER_ATTR_NAME}' cannot be time varying.",
                at=signal_order_attr,
            )
            return []
        # Are the values of signal order valid?
        # Prune the invalid values
        signal_order: list[str] = signal_order_attr.Get()
        invalid_signal_order: list[str] = []
        for signal_value in signal_order:
            if signal_value not in self.SIGNAL_VALUES:
                self._AddFailedCheck(
                    f"Invalid signal order value: '{signal_value}'. Expected one of: {self.SIGNAL_VALUES}",
                    at=signal_order_attr,
                )
                invalid_signal_order.append(signal_value)
        # Remove the invalid values
        if invalid_signal_order:
            signal_order = [value for value in signal_order if value not in invalid_signal_order]
        # Check for duplicate signal order items
        # Remove the duplicates
        if len(signal_order) != len(set(signal_order)):
            self._AddFailedCheck(
                f"Attribute '{self.SIGNAL_ORDER_ATTR_NAME}' has duplicate values.",
                at=signal_order_attr,
            )
            signal_order = list(set(signal_order))
        return signal_order

    def _parse_signals(self, directional_box: Usd.Prim, signal_order: list[str]):
        """Finds all signals under the provided directional box prim and validates them."""
        # Get all signal prims under the directional box
        signals: list[Usd.Prim] = []
        signal_values: list[str] = []
        prim_range_iter = iter(Usd.PrimRange(directional_box, Usd.TraverseInstanceProxies()))
        for prim in prim_range_iter:
            signal_attr = prim.GetAttribute(self.SIGNAL_ATTR_NAME)
            if signal_attr and self._check_signal(prim, signal_attr, signal_order):
                signals.append(prim)
                signal_values.append(signal_attr.Get())
        if signals:
            # Validate that each value in the signal order list has at least one signal prim
            for signal_order_value in signal_order:
                if not any(value == signal_order_value for value in signal_values):
                    self._AddWarning(
                        f"Invalid traffic light: item '{signal_order_value}' in '{self.SIGNAL_ORDER_ATTR_NAME}' has no corresponding signal prims.",
                        at=directional_box.GetAttribute(self.SIGNAL_ORDER_ATTR_NAME),
                    )
        else:
            # No signals found
            self._AddFailedCheck(
                f"Invalid traffic light: no signals under directional box {directional_box.GetPrimPath()}.",
                at=directional_box,
            )

    def _check_signal_type_attr(self, signal_type_attr: Usd.Attribute) -> bool:
        """Validates the signalType attribute of the directional box prim.
        Returns True if the attribute is valid, False otherwise.
        """
        # Is the value valid?
        if (signal_type_value := signal_type_attr.Get()) != self.SIGNAL_TYPE_ATTR_VALUE:
            self._AddFailedCheck(
                f"Attribute '{self.SIGNAL_TYPE_ATTR_NAME}' has invalid value '{signal_type_value}'."
                f"Expected: '{self.SIGNAL_TYPE_ATTR_VALUE}'.",
                at=signal_type_attr,
            )
            return False
        # Is the type valid?
        if signal_type_attr.GetTypeName() != Sdf.ValueTypeNames.Token:
            self._AddFailedCheck(
                f"Attribute '{self.SIGNAL_TYPE_ATTR_NAME}' has invalid type {signal_type_attr.GetTypeName()}. "
                f"Expected: {Sdf.ValueTypeNames.Token}",
                at=signal_type_attr,
            )
            return False
        # Is it time varying?
        if signal_type_attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                f"Attribute '{self.SIGNAL_TYPE_ATTR_NAME}' cannot be time varying.",
                at=signal_type_attr,
            )
            return False
        return True

    def _check_signal(self, prim: Usd.Prim, signal_attr: Usd.Attribute, signal_order: list[str]) -> bool:
        """
        Checks the signal prim's type and its signal attribute.
        """
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        is_mesh_bulb: bool = self._is_render_or_default_mesh(mesh)
        is_light: bool = self._is_light(prim)
        if not is_light:
            if not mesh:
                # Prim is neither a UsdLux light nor a Mesh
                self._AddWarning(
                    f"Attribute '{self.SIGNAL_ATTR_NAME}' not expected on prim of type {prim.GetTypeName()}. "
                    "Only prims of type UsdLux or Meshes with default or render purpose are expected to have a signal attribute.",
                    at=prim,
                )
                return False
            elif not is_mesh_bulb:
                # Prim is a mesh with an invalid purpose
                self._AddFailedCheck(
                    f"Mesh with attribute '{self.SIGNAL_ATTR_NAME}' must have render purpose 'default' or 'render'. "
                    "The mesh will be ignored.",
                    at=prim,
                )
                return False
        # There's a "lighgt bulb" (either a light or a mesh prim)
        # Validate the signal attribute
        if not self._validate_signal_attr(signal_attr, signal_order if signal_order else self.SIGNAL_VALUES):
            return False
        # Validate the mesh "light bulb"
        if is_mesh_bulb and not self._validate_mesh_bulb(mesh):
            return False
        return True

    def _validate_signal_attr(self, signal_attr: Usd.Attribute, signal_order: list[str]) -> bool:
        """Validates the signal attribute of the signal prim.
        Returns True if the attribute is valid, False otherwise.
        """
        # Check the signal attribute's type
        if signal_attr.GetTypeName() != Sdf.ValueTypeNames.Token:
            self._AddFailedCheck(
                f"Attribute has invalid type {signal_attr.GetTypeName()}. Expected: {Sdf.ValueTypeNames.Token}",
                at=signal_attr,
            )
            return False
        # Check if the signal attribute is time varying
        if signal_attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                "Attribute cannot be time varying.",
                at=signal_attr,
            )
            return False
        # Check the signal attribute's value
        signal_value: str = signal_attr.Get()
        if signal_order and signal_value not in signal_order:
            self._AddFailedCheck(
                f"Invalid signal attribute value: '{signal_value}'. " f"Expected one of: {signal_order}",
                at=signal_attr,
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
                message="Invalid traffic light: no materials found on signal mesh.",
                at=mesh.GetPrim(),
            )
            return False
        # Mesh must have simpbr shader
        simpbr_attr_info: SimPbrAttributesInfo | None = self._get_sim_pbr_shader_info(material)
        if not simpbr_attr_info:
            self._AddFailedCheck(
                message=f"Invalid traffic light: material bound to a signal mesh must use one of the supported shaders {self.SIM_PBR_SHADERS}.",
                at=material.GetPrim(),
            )
            return False
        # Mesh's material must have emissive properties turned on
        if not simpbr_attr_info.emissive:
            self._AddFailedCheck(
                message="Invalid traffic light: material bound to a signal mesh does not have emissiveness turned on.",
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
        """Check the surface shader of the given material if its a sim pbr shader
        (SimPBR, SimPBR_Translucent, SimGlassPBR) has emissive enabled.
        """
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

    def _reset(self):
        self._default_prim = None
        self._signal_groups = {}
        self._signal_order = set()

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
