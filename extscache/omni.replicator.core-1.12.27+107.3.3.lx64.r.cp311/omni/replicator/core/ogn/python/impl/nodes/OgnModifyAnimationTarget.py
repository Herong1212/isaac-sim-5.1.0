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

from typing import NamedTuple, Optional, Tuple

import carb
import omni.graph.core as og
import omni.timeline
import omni.usd
from omni.replicator.core import utils
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdSkel, Vt


# From pose-tracker vid2wiv_utils.py
class SkelAnimRange(NamedTuple):
    min: float
    max: float
    has_samples: bool = False

    def __bool__(self):
        return self.has_samples


# From pose-tracker vid2wiv_utils.py
def get_skel_anim_range(skel_anim: UsdSkel.Animation):
    """Extracts time ranges from a skeleton animation.
    Args:
        skel_anim: a skeleton animation property
    Returns:
        bool: True if the animation has time samples
        float: start time in time codes
        float: end time in time codes
    """
    SKEL_ANIM_ATTR_GETTERS = (
        UsdSkel.Animation.GetTranslationsAttr,
        UsdSkel.Animation.GetRotationsAttr,
        UsdSkel.Animation.GetJointsAttr,
        UsdSkel.Animation.GetScalesAttr,
    )

    skel_anim_attrs: Tuple[Usd.Attribute] = (getter(skel_anim) for getter in SKEL_ANIM_ATTR_GETTERS)
    t_min, t_max = -float("inf"), float("inf")
    has_samples = False

    for skel_attr in skel_anim_attrs:
        if not skel_attr:
            continue

        time_samples = skel_attr.GetTimeSamples()
        if not time_samples:
            continue

        if has_samples:
            t_min = min(t_min, time_samples[0])
            t_max = max(t_max, time_samples[-1])
            continue

        t_min = time_samples[0]
        t_max = time_samples[-1]
        has_samples = True

    return SkelAnimRange(t_min, t_max, has_samples)


class OgnModifyAnimationTarget:
    @staticmethod
    def compute(db) -> bool:
        input_prims = db.inputs.prims
        skel_anim_paths = db.inputs.values
        reset_timeline = db.inputs.reset_timeline

        stage = omni.usd.get_context().get_stage()
        timeline_iface = omni.timeline.get_timeline_interface()

        # Verify prims are Skeleton prims
        skeleton_prims = []
        for prim in input_prims:
            if stage.GetPrimAtPath(str(prim)).IsA(UsdSkel.Skeleton):
                skeleton_prims.append(prim)

        # Try and get skeletons from passed in prims
        # Get all Skeleton prims in the stage then filter
        # GetAllChildren only gets all immediate children
        all_skels = [s.GetPath() for s in stage.Traverse() if s.IsA(UsdSkel.Skeleton)]

        # Filter based on the prims passed in
        valid_skels = []
        for prim in input_prims:
            for skel in all_skels:
                if Sdf.Path(str(prim)) in skel.GetPrefixes():
                    valid_skels.append(skel)
                    break

        if not valid_skels:
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        # Use only one animation
        if skel_anim_paths:
            skel_anim_path = skel_anim_paths[0]
        else:
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        # Verify anim path is valid
        anim = stage.GetPrimAtPath(str(skel_anim_path))
        if not anim.IsValid():
            carb.log_error(f"Animation {skel_anim_path} is not a valid SkelAnimation path!")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        if not anim.IsA(UsdSkel.Animation):
            carb.log_error(f"Animation {skel_anim_path} is not a valid SkelAnimation!")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        # Assign clip to target character(s)
        for skeleton_path in valid_skels:
            skeleton = stage.GetPrimAtPath(str(skeleton_path))
            anim_rel: Usd.Relationship = UsdSkel.BindingAPI(skeleton).GetAnimationSourceRel()
            if not anim_rel:
                carb.log_error(f"No animationSource relationship on {skeleton_path}")
                db.outputs.exec = og.ExecutionAttributeState.DISABLED
                return False
            anim_rel.SetTargets([str(skel_anim_path)])

        # Set stage length to anim length
        # TODO This currently doesn't work, need to investigate
        # anim_range = get_skel_anim_range(UsdSkel.Animation(anim))
        # if anim_range:
        #     stage.SetStartTimeCode(anim_range.min)
        #     stage.SetEndTimeCode(anim_range.max)
        #     fps = timeline_iface.get_time_codes_per_seconds()
        #     timeline_iface.set_start_time(anim_range.min / fps)
        #     timeline_iface.set_end_time(anim_range.max / fps)

        if reset_timeline:
            timeline_iface.set_current_time(0)

        # Play the timeline after changing animations
        timeline_iface.play()

        db.outputs.exec = og.ExecutionAttributeState.ENABLED

        return True
