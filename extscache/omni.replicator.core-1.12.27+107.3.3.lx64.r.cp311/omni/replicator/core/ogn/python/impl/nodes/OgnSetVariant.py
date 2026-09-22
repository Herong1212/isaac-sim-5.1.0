# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the implementation of the OGN node defined in OgnOnNewFrame.ogn
"""

import carb
import omni.graph.core as og
from omni.replicator.core import utils
from pxr import Sdf, Usd, UsdGeom


@carb.profiler.profile
def set_variants(prims, variant, values):
    with Sdf.ChangeBlock():
        for prim, value in zip(prims, values):
            has_found_variant = False
            # Recurse through children to find variant set
            for prim_c in Usd.PrimRange(prim):
                if _check_for_variant(prim_c, variant, value):
                    prim_c.GetVariantSet(variant).SetVariantSelection(value)
                    has_found_variant = True
                    break  # Only one variant change per prim expected
            if not has_found_variant:
                carb.log_warn(f"{prim} has no variant {value} in the variant set {variant}. Skipping...")


@carb.profiler.profile
def _check_for_variant(prim, variant, value):
    return prim.GetVariantSets().HasVariantSet(variant) and value in prim.GetVariantSet(variant).GetVariantNames()


class OgnSetVariant:
    @staticmethod
    def compute(db) -> bool:
        targets = db.inputs.prims
        values = db.inputs.values
        variant = db.inputs.variant

        if not variant:
            # db.log_error("Variant name not specified!")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        if len(values) == 0:
            # db.log_error("No variant values provided!")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        prims = utils.find_prims(targets, "prims")

        if len(prims) != len(values):
            if len(values) == 1:
                values = values * len(prims)
            else:
                db.log_error(
                    f"Expected equal number of variant values to prims, received {len(values)} values and {len(prims)} prims."
                )

        set_variants(prims, variant, values)
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
