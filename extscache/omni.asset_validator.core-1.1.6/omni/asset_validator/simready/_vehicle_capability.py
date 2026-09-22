# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["VehicleCapabilityChecker"]

import itertools
from functools import partial

from omni.asset_validator.core import BaseRuleChecker, Suggestion, is_omni_path
from pxr import Gf, Sdf, Usd, UsdGeom

from ._vehicle_utils import SIMREADY, SimReadyAttrDesc, SteerMethod, VehicleCollection

AXIS_TOKEN_TO_INDEX_MAP = {UsdGeom.Tokens.x: 0, UsdGeom.Tokens.y: 1, UsdGeom.Tokens.z: 2}

AXIS_VEC_TO_TOKEN_MAP = {
    Gf.Vec3d.XAxis(): UsdGeom.Tokens.x,
    -Gf.Vec3d.XAxis(): UsdGeom.Tokens.x,
    Gf.Vec3d.YAxis(): UsdGeom.Tokens.y,
    -Gf.Vec3d.YAxis(): UsdGeom.Tokens.y,
    Gf.Vec3d.ZAxis(): UsdGeom.Tokens.z,
    -Gf.Vec3d.ZAxis(): UsdGeom.Tokens.z,
}

IS_CLOSE_TOLERANCE = 1e-3


class VehicleCapabilityChecker(BaseRuleChecker):
    """
    Validates the following component rules in the **AV Sim Vehicle Specification**:

    - **5.0.C0.01: Vehicle Alignment Needs**

      A vehicle must be axis-aligned, centered at the origin, and its wheels must sit on the ground plane.

    - **5.0.C0.02: Vehicle Parts Annotation**

      All mesh prims must be identified as belonging to a vehicle part.

    - **5.0.C0.03**:

      The vehicle root prim cannot be transformed.
    """

    def __init__(self, verbose, consumerLevelChecks, assetLevelChecks):
        super().__init__(verbose, consumerLevelChecks, assetLevelChecks)
        self.__root_prim = None

    def CheckStage(self, usdStage: Usd.Stage):
        """
        Overwrites BaseRuleChecker.CheckStage.
        """
        self.__root_prim = None
        self._check_vehicle(usdStage)

    def CheckPrim(self, prim: Usd.Prim):
        """
        Overwrites BaseRuleChecker.CheckPrim.
        """
        if not self.__is_from_default_prim(prim):
            return
        if is_omni_path(prim.GetPath()):
            return
        # Check the type of vehile specific attributes
        for attr_desc in SIMREADY.get_vehicle_attribute_descriptions():
            self._check_attribute(prim.GetAttribute(attr_desc.name), attr_desc)
        # Some light attributes names are dependent on the values of other attributes
        # so they need some special handling
        if attr := prim.GetAttribute(SIMREADY.LIGHT_ATTR_NAME):
            light_groups = attr.Get()
            for lg in light_groups:
                for attr_desc in SIMREADY.get_vehicle_light_attribute_descriptions(lg):
                    self._check_attribute(prim.GetAttribute(attr_desc.name), attr_desc)

    def _check_vehicle(self, usdStage: Usd.Stage):
        """
        Validates the following component rules in the AV Sim vehicle Specification.
            - A vehicle must be centered at the origin.
            - wheels must sit on the ground plane.
            - Wheels must be axis-aligned.
            - The default prim the vehicle asset cannot be transformed.
        """
        # Get Asset root prim
        self.__root_prim = usdStage.GetDefaultPrim()
        if not self.__root_prim:
            self._AddFailedCheck(message=f"Input stage {usdStage} has no default prim. Unable to validate Vehicle.")
            return

        up_axis = UsdGeom.GetStageUpAxis(usdStage)
        if up_axis not in (UsdGeom.Tokens.y, UsdGeom.Tokens.z):
            raise ValueError(
                f"Invalid stage up axis - {up_axis}. Stage up axis can only be {UsdGeom.Tokens.y} or {UsdGeom.Tokens.z}"
            )

        # Check if vehicle root prim has xforms
        self._check_prim_has_non_identity_xform(self.__root_prim)

        is_close_tolerance = UsdGeom.LinearUnits.millimeters / UsdGeom.GetStageMetersPerUnit(usdStage)

        vehicle = VehicleCollection(self.__root_prim)

        # 5.0.C0.01 Vehicle Alignment Needs
        # Check if vehicle centered at the origin
        self._check_vehicle_centered(vehicle, is_close_tolerance=is_close_tolerance)

        # Check if wheels sit on the ground plane
        self._check_wheels_on_ground(vehicle, is_close_tolerance=is_close_tolerance)

        # Check if the vehicle is axis aligned.
        self._check_axis_aligned(vehicle, is_close_tolerance=is_close_tolerance)

        # 5.0.C0.02 Vehicle Definition Requirements
        # All geometry prims must be included in at least one USD Collection
        if vehicle.orphans:
            self._AddFailedCheck(
                message=(
                    f"{'Prim' if len(vehicle.orphans) == 1 else 'Prims'} - {', '.join([p.GetPath().pathString for p in vehicle.orphans])} "
                    f"{'is' if len(vehicle.orphans) == 1 else 'are'} not included in any component group."
                ),
                at=vehicle.orphans[0],
            )

        # 5.0.C1.01: Important Vehicle Geometry Semantics.
        # This condition will always pass because if GroundTruthCapabilityChecker is invoked, the condition is inherently satisfied.
        # Therefore this is removed from the Spec 0.0.5 vehicle section, but still a valid check.
        self._check_semantic_labels(vehicle)

    def _check_semantic_labels(self, vehicle: VehicleCollection):
        """Check if all components are semantic labeled"""
        for component in vehicle.components.values():
            # Skip Task markers
            if component.type == "task":
                continue

            semantic_labels = component.get_semantic_tags()
            if semantic_labels:
                continue

            # We check the purpose of the component, if the purpose is not render or default, then it is ok
            if (
                component.prim
                and (imageable := UsdGeom.Imageable(component.prim))
                and imageable.ComputePurpose() not in (UsdGeom.Tokens.default_, UsdGeom.Tokens.render)
            ):
                continue

            # We check the purpose of each prim in the component, only report failure if the purpose is render or default.
            for prim in itertools.chain.from_iterable(component.collections.values()):
                if (imageable := UsdGeom.Imageable(prim)) and imageable.ComputePurpose() in (
                    UsdGeom.Tokens.default_,
                    UsdGeom.Tokens.render,
                ):
                    self._AddFailedCheck(
                        message=f"Prim {prim.GetPath()} in component '{component.path}' of type '{component.type}' is not semantic labeled.",
                        at=prim,
                    )

    def _check_wheels_on_ground(self, vehicle: VehicleCollection, is_close_tolerance: float = IS_CLOSE_TOLERANCE):
        """Check if all wheels on the ground"""
        wheel_components = vehicle.get_components_of_type("wheel")
        if not wheel_components:
            self._AddFailedCheck(
                message=f"No wheels found under asset prim {vehicle.vehicle_root.GetPath()}.", at=vehicle.vehicle_root
            )
            return

        up_axis_idx = AXIS_TOKEN_TO_INDEX_MAP.get(AXIS_VEC_TO_TOKEN_MAP.get(vehicle.vertical_axis))
        for wheel_component in wheel_components:
            bbox_range = wheel_component.bound.ComputeAlignedBox()
            bbox_min = bbox_range.GetMin()
            is_on_ground = Gf.IsClose(bbox_min[up_axis_idx], 0, is_close_tolerance)
            if not is_on_ground:
                self._AddFailedCheck(
                    message=(
                        f"Bounding box of the wheel {wheel_component.path} does not sit on the ground. "
                        f"Bounding box bottom: {bbox_min[up_axis_idx]}"
                    ),
                    at=wheel_component.prim,
                )

    def _check_vehicle_centered(self, vehicle: VehicleCollection, is_close_tolerance: float = IS_CLOSE_TOLERANCE):
        """Validate if the bbox of the given vehicle is centered at origin."""
        center = vehicle.bound.ComputeCentroid()
        if not Gf.IsClose(
            center.GetCross(vehicle.vertical_axis),
            (0, 0, 0),
            is_close_tolerance,
        ):
            self._AddFailedCheck(
                message=(
                    f"Bounding box of the asset root prim {vehicle.vehicle_root.GetPath()} is not centered at the origin. "
                    f"Bounding box center: {center}"
                ),
                at=vehicle.vehicle_root,
            )

    def _check_prim_has_non_identity_xform(self, prim: Usd.Prim):
        """Validate if the given prim has has local transformation that is not identity matrix."""
        if (
            (xform := UsdGeom.Xform(prim))
            and xform.GetOrderedXformOps()
            and xform.GetLocalTransformation() != Gf.Matrix4d().SetIdentity()
        ):
            self._AddFailedCheck(
                message=(f"Asset root prim {prim.GetPath()} can not have non identity matrix transformation."),
                at=prim,
            )

    def _check_axis_aligned(self, vehicle: VehicleCollection, is_close_tolerance: float = IS_CLOSE_TOLERANCE):
        """Check if the given wheel bbox centers are axis aligned."""
        for wheel_group in vehicle.compute_wheel_axles():

            if len(wheel_group) == 0:
                self._AddFailedCheck(
                    message="Failed validating vehicle axis alignment. No wheel component found.",
                    at=vehicle.vehicle_root,
                )
                continue

            elif len(wheel_group) == 1:
                self._AddWarning(
                    message=(
                        f"Only one wheel component found - {wheel_group[0].path}. Skip validating vehicle axis alignment."
                    ),
                    at=wheel_group[0].prim,
                )
                continue

            # Check all wheel components in the same group are aligned
            for idx in range(len(wheel_group) - 1):
                wheel_component_1 = wheel_group[idx]
                wheel_component_2 = wheel_group[idx + 1]
                pos_1 = wheel_component_1.transform.ExtractTranslation()
                pos_2 = wheel_component_2.transform.ExtractTranslation()
                long_pos_1 = vehicle.longitudinal_axis.GetDot(pos_1)
                long_pos_2 = vehicle.longitudinal_axis.GetDot(pos_2)
                if not Gf.IsClose(long_pos_1, long_pos_2, is_close_tolerance):
                    self._AddFailedCheck(
                        message=(
                            f"Wheel {wheel_component_1.path} ({long_pos_1}) and {wheel_component_2.path} ({long_pos_2}) do not align with the longitudinal axis."
                        ),
                        at=wheel_component_1.prim,
                    )

    def _check_attribute(self, attr: Usd.Attribute, attr_desc: SimReadyAttrDesc):
        """Checks if attribute conforms to its description"""
        if not attr or not attr_desc:
            return
        # Is the attribute's type valid?
        if len(attr_desc.types) > 0 and not any(attr.GetTypeName() == t for t in attr_desc.types):
            self._AddFailedCheck(
                f"Invalid attribute type '{attr.GetTypeName()}' found. Expected "
                + (
                    f"'{attr_desc.types[0]}'."
                    if len(attr_desc.types) == 1
                    else f"one of: '{[str(t) for t in attr_desc.types]}'."
                ),
                at=attr,
            )
        # Is the attribute's value one of the allowed values?
        # Only check for string and token type attributes
        if (
            len(attr_desc.allowed_values) > 0
            and len(attr_desc.types) == 1
            and (Sdf.ValueTypeNames.Token == attr_desc.types[0] or Sdf.ValueTypeNames.String == attr_desc.types[0])
        ):
            # Make a case insensitive comparison for string and token type attributes
            attr_value = VehicleCapabilityChecker.__make_string_casefold(attr.Get())
            if not any(
                attr_value == VehicleCapabilityChecker.__make_string_casefold(v) for v in attr_desc.allowed_values
            ):
                self._AddFailedCheck(
                    f"Invalid value '{attr.Get()}' found. Expected "
                    + (
                        f"'{attr_desc.allowed_values[0]}'."
                        if len(attr_desc.allowed_values) == 1
                        else f"one of: {attr_desc.allowed_values}."
                    ),
                    at=attr,
                )
            # Is the list of allowed attributes correct?
            attr_allowed_tokens = [
                VehicleCapabilityChecker.__make_string_casefold(v) for v in (attr.GetMetadata("allowedTokens") or [])
            ]
            attr_desc_allowed_values = [
                VehicleCapabilityChecker.__make_string_casefold(v) for v in attr_desc.allowed_values
            ]

            # For steering method tokens, map string tokens to enum values to allow for synonyms in the allowed values
            if attr_allowed_tokens and attr_desc.name == SIMREADY.VEHICLE_STEER_ATTR_NAME:
                attr_allowed_tokens, attr_desc_allowed_values = self._map_steering_tokens_to_enum_values(
                    attr_allowed_tokens, attr_desc_allowed_values
                )

            if attr_allowed_tokens and set(attr_desc_allowed_values) != set(attr_allowed_tokens):
                self._AddWarning(
                    f"Incorrect allowed values found: {attr.GetMetadata('allowedTokens')}. Expected: {attr_desc.allowed_values}.",
                    at=attr,
                    suggestion=Suggestion(
                        message="Set the allowed values to the expected ones",
                        callable=partial(self._set_allowed_tokens, allowed_tokens=attr_desc.allowed_values),
                        at=[attr],
                    ),
                )
        # Is the attribute time varying?
        if not attr_desc.time_varying and (attr.GetNumTimeSamples() > 0):
            self._AddFailedCheck(
                f"Attribute '{attr}' cannot be time varying.",
                at=attr,
            )
        elif attr_desc.time_varying and (attr.GetNumTimeSamples() == 0):
            self._AddFailedCheck(
                f"Attribute '{attr}' must be time varying.",
                at=attr,
            )

    def _set_allowed_tokens(self, stage: Usd.Stage, attr: Usd.Attribute, allowed_tokens: list):
        """Set the allowed tokens of the attribute to the given list."""
        attr.SetMetadata("allowedTokens", allowed_tokens)

    def __is_from_default_prim(self, prim: Usd.Prim):
        if not self.__root_prim:
            return False
        return prim.GetPath().HasPrefix(self.__root_prim.GetPath())

    @staticmethod
    def __make_string_casefold(value):
        if isinstance(value, str):
            return value.casefold()
        return value

    def _map_steering_tokens_to_enum_values(
        self, attr_allowed_tokens: list, attr_desc_allowed_values: list
    ) -> tuple[list, list]:
        """Map steering tokens to their enum values to handle synonyms like 'tank' and 'none'."""
        if not attr_allowed_tokens or not attr_desc_allowed_values:
            return attr_allowed_tokens, attr_desc_allowed_values

        mapped_tokens = [SteerMethod.steering_map()[t] for t in attr_allowed_tokens if t in SteerMethod.steering_map()]
        mapped_values = [
            SteerMethod.steering_map()[v] for v in attr_desc_allowed_values if v in SteerMethod.steering_map()
        ]
        return mapped_tokens, mapped_values
