# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["GroundTruthCapabilityTests"]

from omni.asset_validator.simready import GroundTruthCapabilityChecker
from pxr import Sdf

from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning, get_url


def is_usd_semantics_available() -> bool:
    """
    Returns: True if UsdSemantics is available.
    """
    try:
        import pxr

        return hasattr(pxr, "UsdSemantics")
    except:
        return False


class GroundTruthCapabilityTests(AsyncValidationRuleTestCase):
    async def test_gprim_without_qcode(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithoutQCode.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored",
                    at=Sdf.Path("/Cube"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/Cube"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/Cube/ChildCube"),
                ),
            ],
        )

    async def test_gprim_with_semantics_api_schema(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithSemanticsApiSchema.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Deprecated SemanticsAPI schema based wikidata_qcode semantics found.",
                    at=Sdf.Path("/Cube"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/Cube"),
                ),
                IsAWarning(
                    "Deprecated SemanticsAPI schema based wikidata_qcode semantics found.",
                    at=Sdf.Path("/Cube/ChildCube1"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/Cube/ChildCube2"),
                ),
            ],
        )

    async def test_gprim_without_semantics_labels_api_schema(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithoutSemanticsLabelsApiSchema.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/Cube"),
                ),
            ],
        )

    async def test_gprim_with_valid_qcode(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithValidQCode.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[],
        )

    async def test_gprim_with_qcode_timesamples(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithQCodeTimesamples.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Incorrect attribute sampling: the attribute cannot have time samples.",
                    at=Sdf.Path("/Cube.semantics:labels:wikidata_qcode"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/Cube"),
                ),
            ],
        )

    async def test_gprim_with_invalid_qcode(self):
        if is_usd_semantics_available():
            asserts = [
                IsAFailure(
                    "Incorrect semantic label format: the label must be a string starting with letter 'Q' followed by one or more numbers. Found: Q12345abc",
                    at="Attribute (semantics:labels:wikidata_qcode) Prim </World/InvalidValue>",
                ),
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored.",
                    at="Prim </World/MissingValue>",
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at="Prim </World/MissingValue>",
                ),
            ]
        else:
            asserts = [
                IsAFailure(
                    "Incorrect attribute type: actual type string[] different than expected type token[].",
                    at="Attribute (semantics:labels:wikidata_qcode) Prim </World/InvalidTypeName>",
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at="Prim </World/InvalidTypeName>",
                ),
                IsAFailure(
                    "Incorrect semantic label format: the label must be a string starting with letter 'Q' followed by one or more numbers. Found: Q12345abc",
                    at="Attribute (semantics:labels:wikidata_qcode) Prim </World/InvalidValue>",
                ),
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored.",
                    at="Prim </World/MissingValue>",
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at="Prim </World/MissingValue>",
                ),
            ]
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithInvalidQCode.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=asserts,
        )

    async def test_gprim_with_qcode_on_material(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithQCodeOnMaterial.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[],
        )

    async def test_gprim_with_qcode_on_parent(self):
        await self.assertRuleAsync(
            asset=get_url("ground_truth/gprimWithQCodeOnParent.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=[],
        )

    async def test_no_duplicated_error(self):
        if is_usd_semantics_available():
            asserts = [
                IsAFailure(
                    "Incorrect semantic label format: the label must be a string starting with letter 'Q' followed by one or more numbers. Found: Q12345abc",
                    at=Sdf.Path("/World/Error2/InvalidValue.semantics:labels:wikidata_qcode"),
                ),
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored.",
                    at=Sdf.Path("/World/Error2/MissingValue"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/World/Error2/MissingValue"),
                ),
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored.",
                    at=Sdf.Path("/World/Error7"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/World/Error7/ChildCube"),
                ),
                IsAFailure(
                    "Incorrect attribute sampling: the attribute cannot have time samples.",
                    at=Sdf.Path("/World/Error9.semantics:labels:wikidata_qcode"),
                ),
            ]
        else:
            asserts = [
                IsAFailure(
                    "Incorrect attribute type: actual type string[] different than expected type token[].",
                    at=Sdf.Path("/World/Error2/InvalidTypeName.semantics:labels:wikidata_qcode"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/World/Error2/InvalidTypeName"),
                ),
                IsAFailure(
                    "Incorrect semantic label format: the label must be a string starting with letter 'Q' followed by one or more numbers. Found: Q12345abc",
                    at=Sdf.Path("/World/Error2/InvalidValue.semantics:labels:wikidata_qcode"),
                ),
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored.",
                    at=Sdf.Path("/World/Error2/MissingValue"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/World/Error2/MissingValue"),
                ),
                IsAFailure(
                    "Missing schema attribute: 'semantics:label:wikidata_qcode' is not authored.",
                    at=Sdf.Path("/World/Error7"),
                ),
                IsAFailure(
                    "Unlabeled prim: No wikidata_qcode semantics found on prim, its ancestors or its bound materials.",
                    at=Sdf.Path("/World/Error7/ChildCube"),
                ),
                IsAFailure(
                    "Incorrect attribute sampling: the attribute cannot have time samples.",
                    at=Sdf.Path("/World/Error9.semantics:labels:wikidata_qcode"),
                ),
            ]
        await self.assertRuleAsync(
            asset=get_url("ground_truth/noDuplicateSemanticsParsingErrors.usda"),
            rule=GroundTruthCapabilityChecker,
            asserts=asserts,
        )
