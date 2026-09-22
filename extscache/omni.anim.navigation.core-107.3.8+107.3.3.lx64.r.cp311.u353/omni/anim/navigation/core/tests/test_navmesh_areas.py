# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .base_unit_test import BaseUnitTest

from omni.kit.test_suite.helpers import wait_stage_loading

import omni.anim.navigation.core as nav

TEST_STAGE = "TestNavMeshAreas.usda"


class TestNavMeshAreas(BaseUnitTest):

    async def test_stage_bake(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        self.assertIsNotNone(self._navmesh)
        # test navmesh
        await self.save_and_compare_navmesh()

    async def test_stage_defaults(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        # query
        start_point = (-200.0, 0.0, -30.0)
        end_point = (250.0, 0.0, 150.0)
        path = self._navmesh.query_shortest_path(start_pos=start_point, end_pos=end_point, area_costs=[1.0, 1.0])
        self.assertIsNotNone(path)
        self.assertGreaterEqual(path.get_point_count(), 2)

        await self.save_and_compare_navmesh_with_paths([path])

    async def test_set_defaults(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # use area apis to default costs to 1.0
        area_walkable = self.inav.find_area("Walkable")
        area_not_walkable = self.inav.find_area("NotWalkable")
        area_51 = self.inav.find_area("Area51")
        # set override for bake
        self.assertGreaterEqual(area_walkable, 0)
        self.assertLess(area_walkable, self.inav.get_area_count())
        self.assertEqual(area_not_walkable, 1)
        self.assertEqual(area_51, 2)
        self.assertLess(area_51, self.inav.get_area_count())
        self.assertNotEqual(area_walkable, area_51)
        self.assertTrue(self.inav.set_area_default_cost(area_walkable, 1.0))
        self.assertTrue(self.inav.set_area_default_cost(area_51, 1.0))
        self.assertTrue(self.inav.get_area_default_cost(area_walkable) == 1.0)
        self.assertTrue(self.inav.get_area_default_cost(area_51) == 1.0)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        # query
        start_point = (-200.0, 0.0, -30.0)
        end_point = (250.0, 0.0, 150.0)
        path = self._navmesh.query_shortest_path(start_pos=start_point, end_pos=end_point)
        self.assertIsNotNone(path)
        self.assertGreaterEqual(path.get_point_count(), 2)
        # test path
        await self.save_and_compare_navmesh_with_paths([path])

    async def test_override_area51_high_costs(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()

        # override args
        area_walkable = self.inav.find_area("Walkable")
        area_not_walkable = self.inav.find_area("NotWalkable")
        area_51 = self.inav.find_area("Area51")
        area_costs = [0] * 3
        area_costs[area_walkable] = 1.0
        area_costs[area_not_walkable] = -1.0
        area_costs[area_51] = 100.0
        # query
        start_point = (-200.0, 0.0, -30.0)
        end_point = (250.0, 0.0, 150.0)
        path = self._navmesh.query_shortest_path(start_pos=start_point, end_pos=end_point, area_costs=area_costs)
        self.assertIsNotNone(path)
        self.assertGreaterEqual(path.get_point_count(), 2)
        # test path
        await self.save_and_compare_navmesh_with_paths([path])

    async def test_set_area51_high_costs(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # set travel costs
        area_walkable = self.inav.find_area("Walkable")
        area_not_walkable = self.inav.find_area("NotWalkable")
        area_51 = self.inav.find_area("Area51")
        self.inav.set_area_default_cost(area_51, 100.0)
        self.assertTrue(self.inav.get_area_default_cost(area_walkable) == 1.0)
        self.assertTrue(self.inav.get_area_default_cost(area_not_walkable) == -1.0)
        self.assertTrue(self.inav.get_area_default_cost(area_51) == 100.0)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        # query
        start_point = (-200.0, 0.0, -30.0)
        end_point = (250.0, 0.0, 150.0)
        path = self._navmesh.query_shortest_path(start_pos=start_point, end_pos=end_point)
        self.assertIsNotNone(path)
        self.assertGreater(len(path.get_points()), 0)
        # test path
        await self.save_and_compare_navmesh_with_paths([path])

    async def test_override_area_51_no_walk(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        # override args
        area_walkable = self.inav.find_area("Walkable")
        area_not_walkable = self.inav.find_area("NotWalkable")
        area_51 = self.inav.find_area("Area51")
        area_costs = [0] * 3
        area_costs[area_walkable] = 1.0
        area_costs[area_not_walkable] = -1.0
        area_costs[area_51] = -1.0
        # query
        start_point = (-200.0, 0.0, -30.0)
        end_point = (250.0, 0.0, 150.0)
        path = self._navmesh.query_shortest_path(start_pos=start_point, end_pos=end_point, area_costs=area_costs)
        self.assertIsNotNone(path)
        self.assertGreaterEqual(path.get_point_count(), 2)

        await self.save_and_compare_navmesh_with_paths([path])

    async def test_set_area_51_no_walk(self):
        await self.load_stage(self.tests_data_path, TEST_STAGE)
        # set override
        area_walkable = self.inav.find_area("Walkable")
        area_not_walkable = self.inav.find_area("NotWalkable")
        area_51 = self.inav.find_area("Area51")
        self.inav.set_area_default_cost(area_51, -1)
        self.assertTrue(self.inav.get_area_default_cost(area_walkable) == 1.0)
        self.assertTrue(self.inav.get_area_default_cost(area_not_walkable) == -1.0)
        self.assertTrue(self.inav.get_area_default_cost(area_51) == -1)
        # bake
        self._navmesh = await self.bake_navmesh_and_wait()
        # query
        start_point = (-200.0, 0.0, -30.0)
        end_point = (250.0, 0.0, 150.0)
        path = self._navmesh.query_shortest_path(start_pos=start_point, end_pos=end_point)
        self.assertIsNotNone(path)
        self.assertGreater(len(path.get_points()), 0)
        # test path
        await self.save_and_compare_navmesh_with_paths([path])
