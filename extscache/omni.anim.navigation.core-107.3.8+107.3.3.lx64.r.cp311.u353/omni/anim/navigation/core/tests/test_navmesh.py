# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .base_unit_test import BaseUnitTest

import os
import math
import tempfile
import carb.events
import carb.settings
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.undo
from omni.kit.test_suite.helpers import wait_stage_loading
import omni.usd
import NavSchema

from omni.anim.navigation.core import NavMeshSettings

import omni.anim.navigation.core as nav


TEST_STAGE = "TestNavMesh.usda"


class TestNavMesh(BaseUnitTest):

    async def test_navmesh(self):
        start_point = (450, 450, 0)
        end_point = (-255, 255, 50)

        # settings
        self.settings.set(NavMeshSettings.AUTO_REBAKE_SETTING_PATH, False)
        self.settings.set(NavMeshSettings.CACHE_ENABLED_SETTING_PATH, False)
        self.settings.set(NavMeshSettings.VIEW_NAVMESH_SETTING_PATH, True)

        # load test stage
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        self.assertTrue(self._navmesh)

        print("*** test query_random_points ***")
        for x in range(10000):
            p = self._navmesh.query_random_point()
            self.assertTrue(p is not None)
            result = self._navmesh.query_closest_point(p, 0)
            p1 = result[0]
            v = carb.Float3(p1[0] - p[0], p1[1] - p[1], p1[2] - p[2])
            close_enough = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) < 0.01
            self.assertTrue(close_enough)

        print("*** test set_random_seed ***")
        points1 = []
        points2 = []
        self.inav.set_random_seed("test1", 42)
        self.inav.set_random_seed("test2", 43)
        for i in range(100):
            p1 = self._navmesh.query_random_point("test1")
            self.assertTrue(p1 is not None)
            points1.append(p1)
            p2 = self._navmesh.query_random_point("test2")
            self.assertTrue(p2 is not None)
            points2.append(p2)
        self.inav.set_random_seed("test1", 42)
        self.inav.set_random_seed("test2", 43)
        for i in range(100):
            p1 = self._navmesh.query_random_point("test1")
            self.assertTrue(p1 is not None)
            p2 = self._navmesh.query_random_point("test2")
            self.assertTrue(p2 is not None)
            self.assertEqual(points1[i].x, p1.x)
            self.assertEqual(points1[i].y, p1.y)
            self.assertEqual(points1[i].z, p1.z)
            self.assertEqual(points2[i].x, p2.x)
            self.assertEqual(points2[i].y, p2.y)
            self.assertEqual(points2[i].z, p2.z)
        # query shortest path
        path = self.inav.get_navmesh().query_shortest_path(start_pos=start_point, end_pos=end_point)
        self.assertIsNotNone(path)
        self.assertGreater(len(path.get_points()), 0)
        # test path
        await self.save_and_compare_navmesh_with_paths([path])

        # get draw triangles
        print("*** get draw triangles ***")
        vertices = self.inav.get_navmesh().get_draw_triangles(0)
        self.assertGreater(len(vertices), 0)
        # print(vertices)

        # test auto rebake
        print("*** test auto rebake ***")
        self.settings.set(NavMeshSettings.AUTO_REBAKE_SETTING_PATH, True)
        self.settings.set(NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH, 1)

        omni.kit.commands.execute("TransformPrimSRT", path="/World/Cube_03", new_translation=(155, 300, 64))
        self._navmesh = await self.bake_navmesh_and_wait()
        self.assertTrue(self._navmesh)
        #await self.save_and_compare_navmesh("auto_rebake_translate")
