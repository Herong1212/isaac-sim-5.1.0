# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["PreventGestureOverlap"]

from omni.ui import scene as sc


class PreventGestureOverlap(sc.GestureManager):
    """
    A gesture manager to prevent activating new gestures when an existing gesture is already active on the item
    """

    def can_be_prevented(self, arg0: sc.AbstractGesture) -> bool:
        return True

    def should_prevent(self, arg0: sc.AbstractGesture, arg1: sc.AbstractGesture) -> bool:
        gesture = arg0
        preventer = arg1

        # Determines whether 'preventer' should prevent incoming 'gesture' from being triggered
        if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
            return True

        return super().should_prevent(gesture, preventer)
