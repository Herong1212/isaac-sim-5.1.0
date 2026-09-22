# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["EnvironmentCapabilityChecker"]

import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass, field

from omni.asset_validator.core import BaseRuleChecker, is_omni_path, normalize_url
from pxr import Sdf, Usd


@dataclass(frozen=True)
class XodrId:
    """Abstraction over the concept of an ID from an XODR file.
    Useful for creating Ids from strings and validating them.
    """

    value: int = field(default=-1)

    @property
    def is_valid(self) -> bool:
        """Returns True if the ID is valid."""
        return self.value >= 0

    @classmethod
    def create_xodr_id_from_string(cls, v: str):
        """Creates an XodrId from a string."""
        return cls(int(v)) if v.isdigit() else cls()


@dataclass
class XodrTrafficSignal:
    """Represents a (traffic) signal in the XODR file."""

    signal_id: XodrId = field(default_factory=XodrId)
    junction_id: XodrId = field(default_factory=XodrId)
    control_id: XodrId = field(default_factory=XodrId)


@dataclass(frozen=True)
class UsdTrafficSignal:
    """Represents a (traffic) signal in the USD file.
    The signal id is the same as the signal id in the XODR file.
    The junction and control ids found in the XODR file are not recorded
    with the traffic signal in USD Environment.
    """

    signal_id: int = field(default=-1)

    @property
    def is_valid(self) -> bool:
        """Returns True if the ID is valid."""
        return self.signal_id >= 0

    def __hash__(self):
        return hash(self.signal_id)

    def __eq__(self, other):
        if not isinstance(other, UsdTrafficSignal):
            return False
        return self.signal_id == other.signal_id


XodrSignals = dict[int, XodrTrafficSignal]
"""The signals from the XODR file. Key is the signalid, value is a XodrTrafficSignal object."""


UsdSignals = set[UsdTrafficSignal]
"""The signals from the USD stage."""


class EnvironmentCapabilityChecker(BaseRuleChecker):
    """
    Validates the following environment rules found in the **AV Sim Specification: Creators**:

    - **4.0.C4.01**:

      All environments need to have a valid OpenDRIVE file (``.XODR``) asset, matching the structure of the scene.

    - **4.0.C4.02**:

      Traffic signal (traffic light) prims in an environment must be labeled with their corresponding XODR identifier (``signalID``).
    """

    # Class constants
    OPEN_DRIVE_PROP_NAME = "omni:simready:openDrive"
    SIGNAL_ID_ATTR_NAME = "omni:simready:signalID"

    def CheckStage(self, usdStage: Usd.Stage):
        """
        Check that the default prim has an asset attribute pointing to an OpenDrive map file (.XODR)
        Extract information from the XODR file.
        Overwrites BaseRuleChecker.CheckStage.
        """
        # Is there a default prim?
        default_prim: Usd.Prim = usdStage.GetDefaultPrim()
        if not default_prim:
            self._AddFailedCheck(
                "Invalid Environment: missing default prim.",
                at=usdStage,
            )
            return
        # Is the OpenDrive map attribute present
        attr: Usd.Attribute = default_prim.GetAttribute(self.OPEN_DRIVE_PROP_NAME)
        xodr_path: str = self._validate_xodr_attribute(default_prim, attr)
        if xodr_path and self._validate_xodr(xodr_path, usdStage):
            # Extract traffic signal information from the XODR file
            xodr_signals: XodrSignals = self._extract_traffic_signals_from_xodr(xodr_path)
            # Extract traffic signals from the USD stage
            usd_signals: UsdSignals = self._extract_traffic_signals_from_usd_stage(start_prim=default_prim)
            # Validate the signals found in the USD stage against the signals found in the XODR file
            self._validate_signals(stage=usdStage, xodr_signals=xodr_signals, usd_signals=usd_signals)

    def _validate_xodr_attribute(self, prim: Usd.Prim, attr: Usd.Attribute) -> str:
        """
        Validate the OpenDrive map attribute to be a non-list, non-time-varrying, resolved asset
        Args:
            prim: The prim to check
            attr: The attribute to check
        Returns:
            The resolved path if the attribute is valid, otherwise the empty path.
        """
        if not attr:
            self._AddFailedCheck(
                f"Invalid Environment: missing attribute '{self.OPEN_DRIVE_PROP_NAME}'.",
                at=prim,
            )
            return ""
        # Is it a single asset (as opposed to a list of assets)?
        if attr.GetTypeName() != Sdf.ValueTypeNames.Asset:
            self._AddFailedCheck(
                f"Invalid Environment: incorrect attribute type '{attr.GetTypeName()}' found. Expected '{Sdf.ValueTypeNames.Asset}'.",
                at=attr,
            )
            return ""
        # Time samples should not be authored
        if attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                "Invalid Environment: attribute is time-varrying.",
                at=attr,
            )
            return ""
        # Is the OpenDrive map path valid?
        attr_value: Sdf.AssetPath = attr.Get()
        if not attr_value.resolvedPath:
            self._AddFailedCheck(
                f"Invalid Environment: OpenDrive map file '{attr_value}' not found.",
                at=attr,
            )
            return ""
        return attr_value.resolvedPath

    def _extract_traffic_signals_from_xodr(self, xodr_file_path: str) -> XodrSignals:
        """Extracts the traffic signals from the XODR file and returns them as a dictionary."""
        # The signals from the XODR file. Key is the signalid, value is a XodrTrafficSignal object
        xodr_signals: XodrSignals = {}
        if not xodr_file_path:
            return xodr_signals
        root: ElementTree = ElementTree.parse(xodr_file_path).getroot()
        junction_ids: set[str] = set()

        # 1. Extract traffic signals from all the roads
        # First we extract all signals (signal definitions) from all the roads,
        # and capture their junction id. The junction ids might be invalid (-1),
        # but we'll "patch" it when looking at signalReference elements (see loop below).
        for road in root.iter("road"):
            junction_id: XodrId = XodrId.create_xodr_id_from_string(road.attrib["junction"])
            if (signals := road.find("signals")) is not None:
                # A signal may be defined in a road, so extract its data
                self._extract_signals_from_xodr_signal_defs(
                    xodr_signals=xodr_signals, signals=signals, junction_id=junction_id, xodr_file_path=xodr_file_path
                )
                # Record valid junction ids to gather Controller info from later
                if junction_id.is_valid:
                    junction_ids.add(road.attrib["junction"])

        # 2. Extract traffic signal references from all the roads
        # Now that all signal definitions have been extracted, let's look at the signal refences (overrides).
        # We may patch the junction id of the signals that have invalid junction ids.
        for road in root.iter("road"):
            junction_id: XodrId = XodrId.create_xodr_id_from_string(road.attrib["junction"])
            signals = road.find("signals")
            if signals is not None:
                # A signal may be referenced by a road other than where it's defined, so extract any
                # overriden data that the <signalReference> element may contain. This may include the junction id.
                self._extract_signals_from_xodr_signal_refs(
                    xodr_signals=xodr_signals, signals=signals, junction_id=junction_id, xodr_file_path=xodr_file_path
                )
                # Record valid junction ids to gather Controller info from later
                if junction_id.is_valid:
                    junction_ids.add(road.attrib["junction"])

        # 3. Collect controller ids from the junctions we identified as being linked to traffic signals
        controller_ids: set[str] = set()
        for junction in root.findall("junction"):
            if junction.attrib["id"] not in junction_ids:
                continue
            for controller in junction.findall("controller"):
                controller_ids.add(controller.attrib["id"])

        # 4. Update the traffic signals with control ids
        for controller_id in controller_ids:
            # Find the controller in the XODR file
            controller: ElementTree.Element = root.find(f".//controller[@id='{controller_id}']")
            if controller is None:
                self._AddError(f"Controller {controller_id} not found in XODR file {xodr_file_path}")
                continue
            # Controllers have Control elements with signalID attributes.
            for control in controller.findall("control"):
                signal_id: XodrId = XodrId.create_xodr_id_from_string(control.attrib["signalId"])
                if signal_id.is_valid and signal_id.value in xodr_signals:
                    # Found the signal in the signals dictionary, update its control id
                    xodr_signals[signal_id.value].control_id = XodrId.create_xodr_id_from_string(controller_id)
                else:
                    self._AddError(
                        f"Signal {signal_id} in controller {controller_id} not found in XODR file {xodr_file_path}"
                    )
        # 5. Cleanup signals that don't have a junction or control id
        self._cleanup_invalid_xodr_signals(xodr_signals)
        return xodr_signals

    def _extract_signals_from_xodr_signal_defs(
        self, xodr_signals: XodrSignals, signals: ElementTree.Element, junction_id: XodrId, xodr_file_path: str
    ):
        """Extract signals from the <signal> elements of <signals>.
        A <signal> element represents a signal definition.
        """
        for signal in signals.findall("signal"):
            # Junction id may be invalid (-1), but we'll "patch" it when looking at signalReference elements
            signal_id: XodrId = XodrId.create_xodr_id_from_string(signal.attrib["id"])
            if signal_id.is_valid:
                self._update_signals(xodr_signals=xodr_signals, signal_id=signal_id, junction_id=junction_id)
            else:
                self._AddError(f"Invalid signal ID value {signal.attrib['id']} in XODR file {xodr_file_path}")

    def _extract_signals_from_xodr_signal_refs(
        self, xodr_signals: XodrSignals, signals: ElementTree.Element, junction_id: XodrId, xodr_file_path: str
    ):
        """Extract signal data from the <signalReference> elements of <signals>."""
        for signalref in signals.findall("signalReference"):
            # Junction id should not be invalid on roads that reference signals
            if junction_id.is_valid:
                self._update_signals(
                    xodr_signals=xodr_signals,
                    signal_id=XodrId.create_xodr_id_from_string(signalref.attrib["id"]),
                    junction_id=junction_id,
                )
            else:
                self._AddError(f"Invalid junction ID {junction_id} in XODR file {xodr_file_path}")

    def _update_signals(self, xodr_signals: XodrSignals, signal_id: XodrId, junction_id: XodrId):
        """Updates the dictionary of signal"""
        if signal_id.value not in xodr_signals:
            # Add new XodrTrafficSignal to dictionary
            xodr_signals[signal_id.value] = XodrTrafficSignal(
                signal_id=signal_id,
                junction_id=junction_id,
            )
        else:
            # Update existent XodrTrafficSignal.
            if junction_id.is_valid and not xodr_signals[signal_id.value].junction_id.is_valid:
                xodr_signals[signal_id.value].junction_id = junction_id

    def _cleanup_invalid_xodr_signals(self, xodr_signals: XodrSignals):
        """Removes signals that don't have a valid junction or control id."""
        signals_to_remove = [
            sid for sid, s in xodr_signals.items() if (not s.junction_id.is_valid or not s.control_id.is_valid)
        ]
        for signal_id in signals_to_remove:
            del xodr_signals[signal_id]

    def _extract_traffic_signals_from_usd_stage(self, start_prim: Usd.Prim) -> UsdSignals:
        """Extracts the traffic signals from the USD stage.
        It traverses the given stage starting with the given prim.
        """
        usd_signals: UsdSignals = UsdSignals()
        # Traverse the prims under the default prim to find all traffic signals
        traver = Usd.TraverseInstanceProxies()
        for prim in Usd.PrimRange(start_prim, traver):
            if not is_omni_path(prim.GetPath()) and (signal_attr := prim.GetAttribute(self.SIGNAL_ID_ATTR_NAME)):
                usd_signal: UsdTrafficSignal | None = self._validate_int_attribute(signal_attr)
                if usd_signal:
                    if usd_signal not in usd_signals:
                        usd_signals.add(usd_signal)
                    else:
                        self._AddFailedCheck(
                            f"Duplicate signal ID {usd_signal.signal_id} found.",
                            at=signal_attr,
                        )
        return usd_signals

    def _validate_int_attribute(self, attr: Usd.Attribute) -> UsdTrafficSignal | None:
        """Validates that the attribute is an integer and returns its value.
        Returns None if the attribute is not valid, to make it possible to distinguish
        between invalid attribute values and cases when the attribute itself is invalid.
        """
        if attr.GetTypeName() != Sdf.ValueTypeNames.Int64:
            self._AddFailedCheck(
                f"Attribute has incorrect type '{attr.GetTypeName()}'. Expected '{Sdf.ValueTypeNames.Int64}'.",
                at=attr,
            )
            return None
        if attr.GetNumTimeSamples() > 0:
            self._AddFailedCheck(
                "Attribute is time-varrying.",
                at=attr,
            )
            return None
        if attr.Get() is None:
            self._AddFailedCheck(
                "Attribute has no value.",
                at=attr,
            )
            return None
        usd_signal_id = UsdTrafficSignal(attr.Get())
        if not usd_signal_id.is_valid:
            self._AddFailedCheck(
                f"Invalid signal ID value {attr.Get()}. Signal IDs must be positive.",
                at=attr,
            )
            return None
        return usd_signal_id

    def _validate_signals(self, stage: Usd.Stage, xodr_signals: XodrSignals, usd_signals: UsdSignals):
        """Validates the signals found in the USD stage against the signals found in the XODR file."""
        # It is rare that an environment has no traffic signals, but it is possible.
        if not xodr_signals and not usd_signals:
            self._AddWarning(
                "No signals found in USD Environment and associated XODR file.",
                at=stage,
            )
            return
        # For various reasons the number of signals in the XODR file and the USD Environment may not match.
        if len(xodr_signals) != len(usd_signals):
            self._AddWarning(
                f"Number of traffic signals in the USD Environment ({len(usd_signals)}) and associated XODR file ({len(xodr_signals)}) do not match.",
                at=stage,
            )
        # The signals found in the USD Environment should have the same signal ids as the signals found in the XODR file
        for usd_signal in usd_signals:
            xodr_signal = xodr_signals.get(usd_signal.signal_id)
            if not xodr_signal:
                self._AddFailedCheck(
                    f"Signal {usd_signal.signal_id} found in USD Environment not found in XODR file.",
                    at=stage,
                )

    def _validate_xodr(self, xodr_path: str, stage: Usd.Stage) -> bool:
        """Validates the XODR file path and that it's a proper XML file.
        Note that the XODR file is not validated against a specific xml schema.
        """
        try:
            ElementTree.parse(xodr_path)
            return True
        except ElementTree.ParseError as e:
            self._AddFailedCheck(
                f"Invalid Environment: OpenDrive map file {normalize_url(xodr_path)} cannot be parsed. Error: {e}",
                at=stage,
            )
            return False
