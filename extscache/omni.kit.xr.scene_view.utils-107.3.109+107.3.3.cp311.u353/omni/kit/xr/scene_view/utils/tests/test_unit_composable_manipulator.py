# Copyright (c) 2023-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestComposableManipulator"]

import weakref

from omni.kit.xr.scene_view.core import XRSceneView
from omni.kit.xr.scene_view.utils import SceneViewUtils
from omni.kit.xr.scene_view.utils.composable_manipulator import ComposableManipulator
from omni.ui import scene

from .base_sceneview_test import BaseSceneViewTest


class TestComposableManipulator(BaseSceneViewTest):
    async def test_unit_manipulator_lifecycle(self):  # pragma: no cover
        # SceneViewUtils needs to be retained, otherwise it will try to destroy itself and its children when it
        # goes out of scope. This is a new expectation as of January, 2025
        sv_utils = SceneViewUtils(XRSceneView)
        with sv_utils.scene_view.scene:
            root = scene.Transform()
            with root:
                manipulator = ComposableManipulator()

        weak_manipulator = weakref.ref(manipulator)

        # ComposableManipulator is actually a wrapper around scene.Manipulator to help with
        # managing the lifecycle, so we need to also check the internal member is being delete
        # as well.
        weak_internal = weakref.ref(manipulator._ComposableManipulator__internal_manipulator)

        await self.wait_post_sync_async(5)

        # This drops the wrapper object, which because it's a plain Python object, there's very
        # little reason to expect this would ever fail.
        del manipulator
        del sv_utils

        await self.wait_post_sync_async(2)

        self.assertIsNone(weak_manipulator())
        self.assertIsNone(weak_internal())

    async def test_unit_manipulator_mixed_components(self):
        """Ensure that adding mixed types of components doesn't cause problems"""
        pass
