## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestStatsBindings']


import omni.kit.test
from omni.kit.test import AsyncTestCase
import omni.hydra.engine.stats as engine_stats


class TestStatsBindings(AsyncTestCase):
    '''Simple test against the interfaces of the bindings to fail if they change'''

    def setUp(self):
        super().setUp()

    # After running each test
    def tearDown(self):
        super().tearDown()

    def assertItemIsIndexable(self, item):
        self.assertTrue(hasattr(item, '__getitem__'))

    async def test_mem_stats(self):
        mem_stats = engine_stats.get_mem_stats()
        # Item should be indexable
        self.assertItemIsIndexable(mem_stats)
        # Items should have a caetgory field
        self.assertIsNotNone(mem_stats[0].get('category'))

    async def test_mem_stats_detailed(self):
        mem_stats_detailed = engine_stats.get_mem_stats(detailed=True)
        # Item should be indexable
        self.assertItemIsIndexable(mem_stats_detailed)
        # Items should have a caetgory field
        self.assertIsNotNone(mem_stats_detailed[0].get('category'))

    async def test_device_info(self):
        all_devices = engine_stats.get_device_info()
        # Item should be indexable
        self.assertItemIsIndexable(all_devices)

        # Test getting info on individual devices
        for i in range(len(all_devices)):
            cur_device = engine_stats.get_device_info(i)
            self.assertEqual(cur_device['description'], all_devices[i]['description'])
            self.assertTrue(cur_device, all_devices[i])

    async def test_active_engine_stats(self):
        hd_stats = engine_stats.HydraEngineStats()

        a = hd_stats.get_nested_gpu_profiler_result()
        self.assertItemIsIndexable(a)

        b = hd_stats.get_gpu_profiler_result()
        self.assertItemIsIndexable(b)

        c = hd_stats.reset_gpu_profiler_containers()
        self.assertTrue(c)

        self.assertIsNotNone(hd_stats.save_gpu_profiler_result_to_json)

    async def test_specific_engine_stats(self):
        hd_stats = engine_stats.HydraEngineStats(usd_context_name='', hydra_engine_name='')

        a = hd_stats.get_nested_gpu_profiler_result()
        self.assertItemIsIndexable(a)

        b = hd_stats.get_gpu_profiler_result()
        self.assertItemIsIndexable(b)

        c = hd_stats.reset_gpu_profiler_containers()
        self.assertTrue(c)

        self.assertIsNotNone(hd_stats.save_gpu_profiler_result_to_json)
