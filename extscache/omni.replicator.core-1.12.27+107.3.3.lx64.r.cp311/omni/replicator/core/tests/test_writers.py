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

import asyncio
import doctest
import gc
import os
import shutil
import subprocess
import unittest

import carb
import omni.kit
import omni.replicator.core as rep
from omni.replicator.core import Writer, WriterRegistry
from omni.syntheticdata import SyntheticData
from pxr import Sdf, Usd


class CounterWriter(rep.Writer):
    def __init__(self):
        self.counter = 0
        self.annotators = ["LdrColor"]

    def write(self, data):
        self.counter += 1


def get_memory_usage(process_pid):
    """Get memory usage of a process"""
    try:
        result = subprocess.run(["pmap", "-x", str(process_pid)], capture_output=True, text=True)

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            # Last line contains totals
            total_line = lines[-1]
            parts = total_line.split()

            # pmap -x output format: total kbytes, rss, dirty
            numbers = [part for part in parts if part.isdigit()]

            if len(numbers) >= 3:
                total_kb = int(numbers[0])
            else:
                total_kb = 0

            return total_kb / 1024

        else:
            # Fallback if pmap fails
            return 0

    except Exception as e:
        return 0


class TestWriterRegistry(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        stage.DefinePrim("/World", "Xform")
        stage.DefinePrim("/World/Camera", "Camera")
        stage.DefinePrim("/World/Camera2", "Camera")

        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_writer_registry")
        self.extra_out_dirs = []

    async def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)
        for out_dir in self.extra_out_dirs:
            shutil.rmtree(out_dir, ignore_errors=True)
        await omni.usd.get_context().new_stage_async()

    async def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.writers)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")
        else:
            print(f"Passed {test_counts} docstring tests")

    async def test_attach(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]

        writer = rep.WriterRegistry.get(writer_name)
        writer.initialize(output_dir="test_out", rgb=True)
        writer.attach(render_products)

        rgb_anno = rep.annotators.get("rgb")
        rgb_anno.attach(render_products)

        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

        await rep.orchestrator.step_async()
        for rp in writer.get_data()["annotators"]["rgb"]:
            self.assertEqual(writer.get_data()["annotators"]["rgb"][rp]["data"].shape, (500, 500, 4))
        self.assertEqual(rgb_anno.get_data().shape, (500, 500, 4))

    async def test_detach(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]
        writer1 = rep.WriterRegistry.get(writer_name)
        writer2 = rep.WriterRegistry.get(writer_name)

        writer1.initialize(output_dir="test_out", rgb=True)
        writer2.initialize(output_dir="test_out", rgb=True, bounding_box_2d_tight=True)

        writer1.attach(render_products)
        writer2.attach(render_products)

        self.assertEqual(
            len(WriterRegistry._active_writers[render_products[0].path,]),
            2,
        )

        writer1.detach()
        self.assertTrue((render_products[0].path,) in WriterRegistry._active_writers)
        self.assertEqual(
            len(WriterRegistry._active_writers[render_products[0].path,]),
            1,
        )

        writer2.detach()
        self.assertTrue((render_products[0].path,) not in WriterRegistry._active_writers)
        self.assertTrue(WriterRegistry._active_writers == {})

        stage = omni.usd.get_context().get_stage()
        graph_prim = stage.GetPrimAtPath("/Render/PostProcess")

        self.assertEqual(
            len(graph_prim.GetChildren()), 0, f"Graph elements remain after writer detach: {graph_prim.GetChildren()}"
        )

        scheduler_graph_prim = stage.GetPrimAtPath("/WriterOrchestrator")
        self.assertFalse(scheduler_graph_prim.IsValid(), f"Writer scheduler graph elements remain after writer detach")

    async def test_writer_detach_reattach_repeat(self):
        rp1 = rep.create.render_product(rep.create.camera(), (512, 512))
        writer1 = rep.WriterRegistry.get("BasicWriter")
        out_dir = os.getcwd() + "/_out_test"
        writer1.initialize(output_dir=out_dir, rgb=True)
        writer1.attach([rp1])

        writer2 = rep.WriterRegistry.get("BasicWriter")
        out_dir2 = os.getcwd() + "/_out_test2"
        writer2.initialize(output_dir=out_dir2, rgb=True)

        self.extra_out_dirs.append(out_dir)
        self.extra_out_dirs.append(out_dir2)

        for num in range(10):
            rp2 = rep.create.render_product("/OmniverseKit_Persp", (256, 256))
            rp3 = rep.create.render_product("/OmniverseKit_Persp", (256, 512))

            writer2.attach([rp2, rp3])

            await rep.orchestrator.step_async(rt_subframes=2)
            await rep.orchestrator.wait_until_complete_async()

            self.assertEqual(len(os.listdir(out_dir2)), 3, f"Missing a directory. {os.listdir(out_dir2)}")
            for item in os.listdir(out_dir2):
                full_path = os.path.join(out_dir2, item)
                if os.path.isdir(full_path):
                    files = os.listdir(os.path.join(full_path, "rgb"))
                    self.assertEqual(
                        len(files),
                        num + 1,
                        f"Incorrect number of files for RP {item}, expected {num + 1} and got {len(files)}, {files}",
                    )
            writer2.detach()
            rp2.destroy()
            rp3.destroy()

            await asyncio.sleep(0.1)

        self.assertTrue(writer1.get_node())
        with self.assertRaises(rep.writers.InvalidWriterError):
            writer2.get_node()

    async def test_detach_multi_rp(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products_multi = [
            rep.create.render_product(cam_path, (600, 500)),
            rep.create.render_product(cam_path, (700, 500)),
        ]

        writer = rep.WriterRegistry.get(writer_name)
        writer.initialize(output_dir="test_out_multi", camera_params=True, pointcloud=True)
        writer.attach(render_products_multi)

        await rep.orchestrator.step_async()

        stage = omni.usd.get_context().get_stage()
        graph_prim = stage.GetPrimAtPath("/Render/PostProcess")

        self.assertTrue(graph_prim.GetChild("SDGPipeline").IsValid(), "Missing annotator node graph")

        writer.detach()

        self.assertFalse(
            graph_prim.GetChild("SDGPipeline").IsValid(), f"Writer did not detach completely {graph_prim.GetChildren()}"
        )

    async def test_detach_by_id(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]

        writer = rep.WriterRegistry.get(writer_name)
        writer.initialize(output_dir="test_out", rgb=True)
        writer.attach(render_products)

        writer2 = rep.WriterRegistry.get(writer_name)
        writer2.initialize(output_dir="test_out2", rgb=True)
        writer2.attach(render_products)

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        graph_prim = stage.GetPrimAtPath("/Render/PostProcess")

        self.assertTrue(
            graph_prim.GetChild("SDGPipeline").GetChild("Replicator_LdrColorSDhostPtr").IsValid(),
            f"Missing LdrColorSDhostPtr for writer 1 and 2, {graph_prim.GetChildren()}",
        )

        WriterRegistry._detach_by_writer_id(writer_id=writer._writer_id)

        self.assertTrue(
            graph_prim.GetChild("SDGPipeline").GetChild("Replicator_LdrColorSDhostPtr").IsValid(),
            "Missing LdrColorSDhostPtr for writer 2",
        )

        WriterRegistry._detach_by_writer_id(writer_id=writer2._writer_id)

        self.assertFalse(
            graph_prim.GetChild("SDGPipeline").IsValid(), "LdrColorSDhostPtr remaining after all writers detached"
        )

        self.assertTrue((render_products[0].path,) not in WriterRegistry._active_writers)
        self.assertTrue(WriterRegistry._active_writers == {})

        self.assertEqual(
            len(graph_prim.GetChildren()), 0, f"Graph elements remain after writer detach: {graph_prim.GetChildren()}"
        )

        scheduler_graph_prim = stage.GetPrimAtPath("/WriterOrchestrator")
        self.assertFalse(scheduler_graph_prim.IsValid(), f"Writer scheduler graph elements remain after writer detach")

    async def test_detach_by_name(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_product1 = rep.create.render_product(cam_path, (500, 500))
        render_product2 = rep.create.render_product(cam_path, (1024, 512))

        writer1 = rep.WriterRegistry.get(writer_name)
        writer1.initialize(output_dir="test_out1", rgb=True)
        writer1.attach(render_product1)

        writer2 = rep.WriterRegistry.get(writer_name)
        writer2.initialize(output_dir="test_out2", rgb=True)
        writer2.attach(render_product2)

        writer3 = rep.WriterRegistry.get(writer_name)
        writer3.initialize(output_dir="test_out3", rgb=True)
        writer3.attach(render_product2)

        writer4 = rep.WriterRegistry.get(writer_name)
        writer4.initialize(output_dir="test_out3", rgb=True)
        writer4.attach((render_product1, render_product2.path))

        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 3)

        WriterRegistry.detach(writer_name=writer_name, render_products=render_product1)
        self.assertEqual(len(WriterRegistry._active_writers), 1)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path), [])), 0)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 2)

        WriterRegistry.detach(writer_name=writer_name)
        self.assertEqual(len(WriterRegistry._active_writers), 0)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path), [])), 0)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 0)

        WriterRegistry.detach(writer_name=writer_name)

        await omni.kit.app.get_app().next_update_async()

        self.assertTrue((render_product2.path,) not in WriterRegistry._active_writers)
        self.assertTrue(WriterRegistry._active_writers == {})

        stage = omni.usd.get_context().get_stage()
        graph_prim = stage.GetPrimAtPath("/Render/PostProcess")
        self.assertEqual(
            len(graph_prim.GetChildren()), 0, f"Graph elements remain after writer detach: {graph_prim.GetChildren()}"
        )

        scheduler_graph_prim = stage.GetPrimAtPath("/WriterOrchestrator")
        self.assertFalse(scheduler_graph_prim.IsValid(), f"Writer scheduler graph elements remain after writer detach")

    async def test_detach_specific_writer_from_specific_render_product(self):
        """Remove specific writer from specific render product"""

        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_product1 = rep.create.render_product(cam_path, (500, 500))
        render_product2 = rep.create.render_product(cam_path, (1024, 512))

        writer1 = rep.WriterRegistry.get(writer_name)
        writer1.initialize(output_dir="test_out1", rgb=True)
        writer1.attach(render_product1)

        writer2 = rep.WriterRegistry.get(writer_name)
        writer2.initialize(output_dir="test_out2", rgb=True)
        writer2.attach(render_product1)

        writer3 = rep.WriterRegistry.get(writer_name)
        writer3.initialize(output_dir="test_out3", rgb=True)
        writer3.attach(render_product2)

        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 1)

        writer1.detach()
        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 1)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 1)

    async def test_detach_all_writers_of_type_from_specific_render_product(self):
        """Remove all writers of specific type from specific render product"""

        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_product1 = rep.create.render_product(cam_path, (500, 500))
        render_product2 = rep.create.render_product(cam_path, (1024, 512))

        writer1 = rep.WriterRegistry.get(writer_name)
        writer1.initialize(output_dir="test_out1", rgb=True)
        writer1.attach(render_product1)

        writer2 = rep.WriterRegistry.get(writer_name)
        writer2.initialize(output_dir="test_out2", rgb=True)
        writer2.attach(render_product1)

        writer3 = rep.WriterRegistry.get(writer_name)
        writer3.initialize(output_dir="test_out3", rgb=True)
        writer3.attach(render_product2)

        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 1)

        WriterRegistry.detach(writer_name, render_product1)
        self.assertEqual(len(WriterRegistry._active_writers), 1)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 0)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 1)

    async def test_detach_specific_writer_from_all_render_product(self):
        """Remove specific writer from all render products"""

        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_product1 = rep.create.render_product(cam_path, (500, 500))
        render_product2 = rep.create.render_product(cam_path, (1024, 512))

        writer1 = rep.WriterRegistry.get(writer_name)
        writer1.initialize(output_dir="test_out1", rgb=True)
        writer1.attach((render_product1, render_product2))

        writer2 = rep.WriterRegistry.get(writer_name)
        writer2.initialize(output_dir="test_out2", rgb=True)
        writer2.attach(render_product1)

        writer3 = rep.WriterRegistry.get(writer_name)
        writer3.initialize(output_dir="test_out3", rgb=True)
        writer3.attach(render_product2)

        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 2)

        writer1.detach()
        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 1)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 1)

    async def test_detach_all_writers_of_type_from_all_render_product(self):
        """Remove all writers of specific type from all render products"""

        cam_path = "/World/Camera"
        writer_name = "BasicWriter"
        writer_name2 = "KittiWriter"

        render_product1 = rep.create.render_product(cam_path, (500, 500))
        render_product2 = rep.create.render_product(cam_path, (1024, 512))

        writer1 = rep.WriterRegistry.get(writer_name)
        writer1.initialize(output_dir="test_out1", rgb=True)
        writer1.attach(render_product1)

        writer2 = rep.WriterRegistry.get(writer_name2)
        writer2.initialize(output_dir="test_out2")
        writer2.attach(render_product1)

        writer3 = rep.WriterRegistry.get(writer_name)
        writer3.initialize(output_dir="test_out3", rgb=True)
        writer3.attach(render_product2)

        self.assertEqual(len(WriterRegistry._active_writers), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 2)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 1)

        WriterRegistry.detach(writer_name)
        self.assertEqual(len(WriterRegistry._active_writers), 1)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product1.path,), [])), 1)
        self.assertEqual(len(WriterRegistry._active_writers.get((render_product2.path,), [])), 0)

    async def test_get_writers(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]

        writer = rep.WriterRegistry.get(writer_name)
        writer.initialize(output_dir="test_out", rgb=True)
        writer.attach(render_products)

        self.assertIsNotNone(writer._writer_id)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

        a_writers = WriterRegistry.get_attached_writers(render_products)

        self.assertTrue(len(a_writers.keys()) == 1)
        self.assertTrue(writer_name in a_writers)
        self.assertTrue(a_writers[writer_name].__class__.__name__ == writer_name)

    async def test_get_writers_init_params(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]

        writer = rep.WriterRegistry.get(writer_name, init_params={"output_dir": "test_out", "rgb": True})
        writer.attach(render_products)

        self.assertIsNotNone(writer._writer_id)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

        a_writers = WriterRegistry.get_attached_writers(render_products)

        self.assertTrue(len(a_writers.keys()) == 1)
        self.assertTrue(writer_name in a_writers)
        self.assertTrue(a_writers[writer_name].__class__.__name__ == writer_name)

    async def test_reattach(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]
        writer = rep.WriterRegistry.get(writer_name)
        writer2 = rep.WriterRegistry.get(writer_name)

        writer.initialize(output_dir="test_out", rgb=True)
        writer2.initialize(output_dir="test_out", camera_params=True)

        writer.attach(render_products)
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue((render_products[0].path,) in WriterRegistry._active_writers)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

        writer.detach()

        # This await is needed to prevent a hang on Windows with the
        # omni.usd.schema.render_settings.rtx extension enabled (107.3)
        await omni.kit.app.get_app().next_update_async()

        writer2.attach(render_products)
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue((render_products[0].path,) in WriterRegistry._active_writers)
        self.assertFalse(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])
        self.assertTrue(writer2._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

    async def test_get_writer(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]
        writer = rep.WriterRegistry.get(writer_name)

        writer.initialize(output_dir="test_out", rgb=True)

        writer.attach(render_products)

        self.assertIsNotNone(writer._writer_id)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

        a_writer = WriterRegistry.get_attached_writer(writer_name, render_products)

        self.assertTrue(a_writer.__class__.__name__ == writer_name)

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_multi_writer_attach(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        render_products = [rep.create.render_product(cam_path, (500, 500))]
        writer = rep.WriterRegistry.get(writer_name)
        writer2 = rep.WriterRegistry.get(writer_name)

        writer.initialize(output_dir="test_out", rgb=True)
        writer2.initialize(output_dir="test_out", camera_params=True)

        writer.attach(render_products)
        writer2.attach(render_products)

        self.assertIsNotNone(writer._writer_id)
        self.assertIsNotNone(writer._writer_id)
        self.assertTrue(len(WriterRegistry._active_writers.keys()) == 1)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])
        self.assertTrue(writer2._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])

    async def test_multi_rp_attach(self):
        cam_path = "/World/Camera"
        cam2_path = "/World/Camera2"
        writer_name = "BasicWriter"

        render_products = [
            rep.create.render_product(cam_path, (500, 500)),
            rep.create.render_product(cam2_path, (250, 250)),
        ]
        writer = rep.WriterRegistry.get(writer_name)

        writer.initialize(output_dir="test_out", rgb=True)

        writer.attach(render_products)

        self.assertIsNotNone(writer._writer_id)
        self.assertTrue(len(WriterRegistry._active_writers) == 2)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[1].path,)])

    async def test_multi_rp_detach(self):
        cam_path = "/World/Camera"
        cam2_path = "/World/Camera2"
        writer_name = "BasicWriter"

        render_products = [
            rep.create.render_product(cam_path, (500, 500)),
            rep.create.render_product(cam2_path, (250, 250)),
        ]
        writer = rep.WriterRegistry.get(writer_name)

        writer.initialize(output_dir="test_out", rgb=True)

        writer.attach(render_products)

        self.assertIsNotNone(writer._writer_id)
        self.assertTrue(len(WriterRegistry._active_writers) == 2)
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[0].path,)])
        self.assertTrue(writer._writer_id in WriterRegistry._active_writers[(render_products[1].path,)])

        WriterRegistry.detach_all()
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue((render_products[0].path,) not in WriterRegistry._active_writers)
        self.assertTrue((render_products[1].path,) not in WriterRegistry._active_writers)
        self.assertTrue(WriterRegistry._active_writers == {})

        stage = omni.usd.get_context().get_stage()
        graph_prim = stage.GetPrimAtPath("/Render/PostProcess")
        self.assertEqual(
            len(graph_prim.GetChildren()), 0, f"Graph elements remain after writer detach: {graph_prim.GetChildren()}"
        )

    async def test_node_writer(self):
        # Create a new stage
        await omni.usd.get_context().new_stage_async()

        camera = rep.create.camera(position=(0, 0, 1000))
        rep.settings.set_render_rtx_realtime(antialiasing="FXAA")

        self.render_product = rep.create.render_product(camera, (1024, 512))
        # Create some shapes to randomize
        stage = omni.usd.get_context().get_stage()
        parent = stage.DefinePrim("/Parent", "Xform")
        rep.functional.modify.semantics(parent, [("class", "parent_semantic"), ("alias", "box")])

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])
        sphere = rep.create.sphere(semantics=[("class", "sphere"), ("alias", "ball")])
        cube = rep.create.cube(semantics=[("class", "cube")])

        # Create hierarchical semantics
        omni.kit.commands.create(
            "MovePrim", path_from="/Replicator/Cube_Xform", path_to="/Parent/Cube"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        cube.set_input("primsIn", ["/Parent/Cube"])

        # fix seed for consistent result
        test_seed = 1234
        with rep.trigger.on_frame(max_execs=10):
            with rep.create.group([torus, sphere, cube]):
                rep.modify.pose(
                    position=rep.distribution.uniform((-100, -100, -100), (200, 200, 200), seed=test_seed),
                    scale=rep.distribution.uniform(0.1, 2, seed=test_seed),
                )
                rep.randomizer.rotation(seed=test_seed)

        self.backend = rep.BackendDispatch(output_dir=self.out_dir)

        await omni.kit.app.get_app().next_update_async()

        node_type_id = "omni.replicator.core.OgnGetPrims"
        annotators = ["rgb", "distance_to_camera"]
        # triggers = [rep.trigger.on_frame(interval=2)]

        rep.writers.register_node_writer("NodeWriterTest", node_type_id, annotators)
        writer1 = rep.writers.get("NodeWriterTest")
        writer1.attach(self.render_product)
        writer2 = rep.writers.get("NodeWriterTest")
        writer2.attach(self.render_product)

        self.assertNotEqual(writer1, writer2)
        self.assertEqual(
            len(WriterRegistry._active_writers[self.render_product.path,]),
            2,
        )

        await rep.orchestrator.step_async()

        writer_prim = stage.GetPrimAtPath("/Render/PostProcess/SDGPipeline/Replicator_NodeWriterWriter")
        self.assertTrue(bool(writer_prim), "Node writer prim missing from expected path")
        self.assertEqual(writer_prim.GetAttribute("node:type").Get(), node_type_id)

        writer_node = writer1.get_node()
        self.assertTrue(
            writer_node.get_attribute_exists("inputs:writerId"), "Node writer is missing the dynamic writerId attribute"
        )

        writer1.detach()
        self.assertTrue((self.render_product.path,) in WriterRegistry._active_writers)
        self.assertEqual(
            len(WriterRegistry._active_writers[self.render_product.path,]),
            1,
        )

        writer2.detach()
        self.assertTrue((self.render_product.path,) not in WriterRegistry._active_writers)
        self.assertTrue(WriterRegistry._active_writers == {})

        graph_prim = stage.GetPrimAtPath("/Render/PostProcess")
        self.assertEqual(
            len(graph_prim.GetChildren()), 0, f"Graph elements remain after writer detach: {graph_prim.GetChildren()}"
        )

    async def test_ids_to_labels_legacy(self):
        SyntheticData.Get().set_instance_mapping_semantic_filter("class:*; alias:*")

        class TestWriter(rep.Writer):
            _payload = None

            def __init__(self):
                self.annotators = [
                    "bounding_box_2d_tight",
                    "bounding_box_2d_loose",
                    "bounding_box_3d",
                    "instance_segmentation",
                    "instance_id_segmentation",
                ]

            def write(self, data):
                self._payload = data

        cam = "/OmniverseKit_Persp"
        rp = rep.create.render_product(cam, (1024, 512))

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])

        writer = TestWriter()
        writer.attach(rp)

        await rep.orchestrator.step_async()

        golden = {"0": {"alias": "donut", "class": "torus"}}
        self.assertEqual(
            writer._payload["bounding_box_2d_tight"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d tight.",
        )
        self.assertEqual(
            writer._payload["bounding_box_2d_loose"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d loose.",
        )
        self.assertEqual(
            writer._payload["bounding_box_3d"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 3d.",
        )

    async def test_ids_to_labels_legacy_multi_rp(self):
        SyntheticData.Get().set_instance_mapping_semantic_filter("class:*; alias:*")

        class TestWriter(rep.Writer):
            _payload = None

            def __init__(self):
                self.annotators = [
                    "bounding_box_2d_tight",
                    "bounding_box_2d_loose",
                    "bounding_box_3d",
                    "instance_segmentation",
                    "instance_id_segmentation",
                ]

            def write(self, data):
                self._payload = data

        cam = "/OmniverseKit_Persp"
        rp = rep.create.render_product(cam, (1024, 512))
        rp2 = rep.create.render_product(cam, (256, 512))

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])

        writer = TestWriter()
        writer.attach([rp, rp2])

        await rep.orchestrator.step_async()

        golden = {"0": {"alias": "donut", "class": "torus"}}
        self.assertEqual(
            writer._payload["bounding_box_2d_tight-Replicator"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d tight.",
        )
        self.assertEqual(
            writer._payload["bounding_box_2d_loose-Replicator"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d loose.",
        )
        self.assertEqual(
            writer._payload["bounding_box_3d-Replicator"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 3d.",
        )

    async def test_ids_to_labels_fast(self):
        SyntheticData.Get().set_instance_mapping_semantic_filter("class:*; alias:*")

        class TestWriter(rep.Writer):
            _payload = None

            def __init__(self):
                self.annotators = ["bounding_box_2d_tight_fast", "bounding_box_2d_loose_fast", "bounding_box_3d_fast"]

            def write(self, data):
                self._payload = data

        cam = "/OmniverseKit_Persp"
        rp = rep.create.render_product(cam, (1024, 512))

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])

        writer = TestWriter()
        writer.attach(rp)

        await rep.orchestrator.step_async()

        golden = {0: {"alias": "donut", "class": "torus"}}
        self.assertEqual(
            writer._payload["bounding_box_2d_tight_fast"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d tight.",
        )
        self.assertEqual(
            writer._payload["bounding_box_2d_loose_fast"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d loose.",
        )
        self.assertEqual(
            writer._payload["bounding_box_3d_fast"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 3d.",
        )

    async def test_ids_to_labels_fast_multi_rp(self):
        SyntheticData.Get().set_instance_mapping_semantic_filter("class:*; alias:*")

        class TestWriter(rep.Writer):
            _payload = None

            def __init__(self):
                self.annotators = ["bounding_box_2d_tight_fast", "bounding_box_2d_loose_fast", "bounding_box_3d_fast"]

            def write(self, data):
                self._payload = data

        cam = "/OmniverseKit_Persp"
        rp = rep.create.render_product(cam, (1024, 512))
        rp2 = rep.create.render_product(cam, (256, 512))

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])

        writer = TestWriter()
        writer.attach([rp, rp2])

        await rep.orchestrator.step_async()

        golden = {0: {"alias": "donut", "class": "torus"}}
        self.assertEqual(
            writer._payload["bounding_box_2d_tight_fast-Replicator"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d tight.",
        )
        self.assertEqual(
            writer._payload["bounding_box_2d_loose_fast-Replicator"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 2d loose.",
        )
        self.assertEqual(
            writer._payload["bounding_box_3d_fast-Replicator"]["info"]["idToLabels"],
            golden,
            "Mismatch in id to labels result for bounding box 3d.",
        )

    async def test_render_product_idxs(self):
        cam_path = "/World/Camera"
        writer_name = "BasicWriter"

        rp_ldr_color = rep.create.render_product(cam_path, (500, 500))
        rp_depth = rep.create.render_product(cam_path, (600, 600))

        class MultiWriter(Writer):
            _payload = None

            def __init__(self):
                self.annotators = [
                    rep.annotators.get("rgb", render_product_idxs=[0]),
                    rep.annotators.get("distance_to_camera", render_product_idxs=[1]),
                ]

            def write(self, data):
                self._payload = data

        writer = MultiWriter()
        writer.attach([rp_ldr_color, rp_depth])
        await rep.orchestrator.step_async()

        gen_keys = set(writer._payload.keys())
        golden_keys = {
            "reference_time",
            "swhFrameNumber",
            "distribution_outputs",
            "trigger_outputs",
            "named_outputs",
            "rp_Replicator",
            "rp_Replicator_01",
            "rgb-Replicator",
            "distance_to_camera-Replicator_01",
        }
        self.assertTrue(
            set(writer._payload.keys()) == golden_keys,
            f"Got incorrect payload keys {golden_keys.symmetric_difference(gen_keys)}",
        )

    async def test_attach_async(self):
        rep.create.camera()
        cam = rep.get.prims(prim_types=["Camera"])
        rp = rep.create.render_product(cam, (1024, 725))

        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir="_out", rgb=True)
        await writer.attach_async(rp)

        stage = omni.usd.get_context().get_stage()
        graph_prim = stage.GetPrimAtPath("/Render/PostProcess/SDGPipeline")
        self.assertGreater(len(graph_prim.GetChildren()), 0, "No graph elements found after writer attach")

    async def test_named_outputs(self):
        class MyWriter(rep.Writer):
            def __init__(self):
                self.payload = None
                self.annotators = ["rgb"]

            def write(self, data):
                self.payload = data

        with rep.trigger.on_frame(name="on-frame"):
            light_intensity_sampler = rep.distribution.uniform(1000, 5000, name="light_intensity", seed=1234)
            rep.create.light(light_type="sphere", intensity=light_intensity_sampler)

        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = MyWriter()
        writer.attach(rp)

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        named_outputs = writer.payload["named_outputs"]
        self.assertTrue("on-frame" in named_outputs, "Missing `on-frame` in named_outputs payload.")
        self.assertEqual(named_outputs["on-frame"].get("execCounts"), 1, f"Expected exec count of `1`.")
        self.assertTrue("light_intensity" in named_outputs, "Missing `light_intensity` in named_outputs payload.")
        self.assertAlmostEqual(
            named_outputs["light_intensity"].get("samples")[0],
            2520.78,
            2,
            msg=f"Got incorrect value of light intensity",
        )

        trigger_outputs = writer.payload["trigger_outputs"]
        self.assertTrue("on-frame" in trigger_outputs, "Missing `on-frame` in named_outputs payload.")
        self.assertEqual(trigger_outputs["on-frame"], 1, f"Expected exec count of `1`.")

        distribution_outputs = writer.payload["distribution_outputs"]
        self.assertTrue(
            "light_intensity" in distribution_outputs, "Missing `light_intensity` in named_outputs payload."
        )
        self.assertAlmostEqual(
            distribution_outputs["light_intensity"][0], 2520.78, 2, msg=f"Got incorrect value of light intensity"
        )

    # TODO Add test with MR486
    # async def test_writer_on_event(self):
    #     writer = CounterWriter()
    #     rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
    #     writer.attach(rp, trigger=rep.trigger.on_event("patate"))

    #     # Verify writer does not trigger on each frame
    #     for _ in range(3):
    #         await rep.orchestrator.step_async()
    #     self.assertEqual(writer.counter, 0, f"Writer was activated `{writer.counter}` times, expected `0`.")

    #     # Fire event
    #     rep.utils.send_og_event("patate")
    #     await rep.orchestrator.step_async()
    #     self.assertEqual(writer.counter, 1, f"Writer was activated `{writer.counter}` times, expected `1`.")

    #     # Verify writer does not trigger additional times
    #     for _ in range(3):
    #         await rep.orchestrator.step_async()
    #     self.assertEqual(writer.counter - 1, 0, f"Writer was activated `{writer.counter - 1}` additional times, expected `0`.")

    async def test_writer_on_frame_interval(self):
        writer = CounterWriter()
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer.attach(rp, trigger=rep.trigger.on_frame(interval=3))

        # Verify capture first frame
        await rep.orchestrator.step_async()
        self.assertEqual(writer.counter, 1, f"Writer was activated `{writer.counter}` times, expected `1`.")

        # Verify writer does not trigger on each frame within interval
        for _ in range(2):
            await rep.orchestrator.step_async()
        self.assertEqual(
            writer.counter - 1, 0, f"Writer was activated `{writer.counter - 1}` additional times, expected `0`."
        )

        # Capture 3rd frame
        await rep.orchestrator.step_async()
        self.assertEqual(writer.counter, 2, f"Writer was activated `{writer.counter}` times, expected `2`.")

        # Verify writer does not trigger additional times
        for _ in range(2):
            await rep.orchestrator.step_async()
        self.assertEqual(
            writer.counter - 2, 0, f"Writer was activated `{writer.counter - 2}` additional times, expected `0`."
        )

    async def test_writer_manual_trigger(self):
        writer = CounterWriter()
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer.attach(rp, trigger=None)

        # Verify writer does not trigger on frame
        for _ in range(3):
            await rep.orchestrator.step_async()
        self.assertEqual(writer.counter, 0, f"Writer was activated `{writer.counter}` times, expected `0`.")

        # Manually trigger writer
        writer.schedule_write()
        self.assertEqual(writer.counter, 0, f"Writer was activated `{writer.counter}` times, expected `0`.")
        await rep.orchestrator.step_async()
        self.assertEqual(writer.counter, 1, f"Writer was activated `{writer.counter}` times, expected `1`.")

        # Verify writer does not trigger additional times
        for _ in range(2):
            await rep.orchestrator.step_async()
        self.assertEqual(
            writer.counter - 1, 0, f"Writer was activated `{writer.counter - 1}` additional times, expected `0`."
        )
        writer.detach()
        stage = omni.usd.get_context().get_stage()
        scheduler_graph_prim = stage.GetPrimAtPath("/WriterOrchestrator")
        self.assertFalse(scheduler_graph_prim.IsValid(), f"Writer scheduler graph elements remain after writer detach")

    async def test_writer_basicwriter_manual_trigger(self):
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = rep.writers.get(
            "BasicWriter", init_params={"output_dir": self.out_dir, "rgb": True}, render_products=rp, trigger=None
        )

        async def count_files(out_dir):
            await rep.orchestrator.wait_until_complete_async()
            print(out_dir)
            print(os.listdir(out_dir))
            return max(len(os.listdir(out_dir)) - 1, 0)

        # Verify writer does not trigger on frame
        for _ in range(3):
            await rep.orchestrator.step_async()
        num_frames = await count_files(self.out_dir)
        self.assertEqual(num_frames, 0, f"Writer was activated `{num_frames}` times, expected `0`.")

        # Manually trigger writer
        num_frames = await count_files(self.out_dir)
        self.assertEqual(num_frames, 0, f"Writer was activated `{num_frames}` times, expected `0`.")
        writer.schedule_write()
        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        num_frames = await count_files(self.out_dir)
        self.assertEqual(num_frames, 1, f"Writer was activated `{num_frames}` times, expected `1`.")

        # Verify writer does not trigger additional times
        for _ in range(2):
            await rep.orchestrator.step_async()
        num_frames = await count_files(self.out_dir)
        self.assertEqual(num_frames - 1, 0, f"Writer was activated `{num_frames - 1}` additional times, expected `0`.")

        # Verify trigger graph is removed
        writer.detach()
        stage = omni.usd.get_context().get_stage()
        scheduler_graph_prim = stage.GetPrimAtPath("/WriterOrchestrator")
        self.assertFalse(scheduler_graph_prim.IsValid(), f"Writer scheduler graph elements remain after writer detach")

    async def test_writer_on_function(self):
        def ball_is_high():
            import omni.usd

            stage = omni.usd.get_context().get_stage()
            ball = stage.GetPrimAtPath("/Replicator/Sphere_Xform")
            ball_height = ball.GetAttribute("xformOp:translate").Get()[1]
            return ball_height > 500.0

        ball = rep.create.sphere()

        writer = CounterWriter()
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer.attach(rp, trigger=ball_is_high)

        # Verify writer does not trigger when ball is low
        for _ in range(3):
            await rep.orchestrator.step_async()
        self.assertEqual(writer.counter, 0, f"Writer was activated `{writer.counter}` times, expected `0`.")

        # Move ball high
        ball.get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Set((0, 1000, 0))

        # Verify writer is triggered
        for i in range(1, 4):
            await rep.orchestrator.step_async()
            # self.assertEqual(writer.counter, i, f"Writer was activated `{writer.counter}` times, expected `{i}`.")

        # Verify payload contents
        payload = writer.get_data()
        self.assertTrue("LdrColor" in payload, f"`LdrColor` data missing from payload, got {payload.keys()}")

        # Move ball low
        ball.get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Set((0, -1000, 0))

        # Verify writer does not trigger additional times
        for _ in range(2):
            await rep.orchestrator.step_async()
        self.assertEqual(
            writer.counter - i, 0, f"Writer was activated `{writer.counter - i}` additional times, expected `0`."
        )

    async def test_attach_writer_capture_on_play_playing(self):
        """Test whether annotator is capturing data when attached on playing scene with capture on play enabled."""
        rep.orchestrator.set_capture_on_play(True)
        rep.orchestrator._orchestrator._timeline.play()
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))

        await omni.kit.app.get_app().next_update_async()

        writer = rep.writers.get("BasicWriter")
        writer.initialize(output_dir="_out", rgb=True)
        writer.attach(rp)

        for _ in range(3):
            await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        writer_data = writer.get_data()

        self.assertTrue(writer_data is not None, "Writer data is empty, expected data received")

    async def test_writer_scheduler(self):
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))

        writer = CounterWriter()
        for i in range(5):
            writer.attach(rp, trigger="omni.replicator.core.OgnOnFrame")

            await rep.orchestrator.step_async()

            self.assertEqual(writer.counter, i + 1, f"Writer missed a frame, got {writer.counter} and expected {i + 1}")

            writer.detach()

    async def test_layered_workflow(self):
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        base_layer = Sdf.Layer.CreateAnonymous("Test1")
        root_layer.subLayerPaths.append(base_layer.identifier)
        stage.SetEditTarget(root_layer)

        rep.orchestrator.set_capture_on_play(True)

        # Getting Writer
        camera_resolution = (1920, 1080)

        rgb_writer = rep.WriterRegistry.get("BasicWriter")
        rgb_writer.initialize(output_dir=self.out_dir, rgb=True)

        # Add randomization
        cube = rep.create.cube()
        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(position=rep.distribution.sequence([(i, i, i) for i in range(6)]))

        camera = rep.create.camera()
        RENDERPRODUCT = rep.create.render_product(camera, camera_resolution)

        await rep.orchestrator.preview_async()
        for i in range(6):
            # create layer
            variation_layer = Sdf.Layer.CreateAnonymous("variation")
            root_layer.subLayerPaths.insert(0, variation_layer.identifier)
            stage.SetEditTarget(variation_layer)

            omni.timeline.get_timeline_interface().play()

            # Render frame
            rgb_writer.attach(RENDERPRODUCT)
            await rep.orchestrator.step_async()

            rgb_writer.detach()

            # Save variation layer to file
            stage.SetEditTarget(root_layer)
            variation_layer.Export(os.path.join(self.out_dir, f"variation_{i}.usda"), "")

            # close
            stage.SetEditTarget(root_layer)
            variation_layer.Clear()
            root_layer.subLayerPaths.remove(variation_layer.identifier)

        # Verify variation layers are correct
        for i in range(6):
            path = os.path.join(self.out_dir, f"variation_{i}.usda")
            with open(path, "r") as f:
                lines = f.readlines()

            line_num = 14 if i == 0 else 6

            self.assertGreater(len(lines), 9)
            self.assertEqual(lines[line_num], f"        double3 xformOp:translate = ({i}, {i}, {i})\n")

    async def test_resolution_change(self):
        rp = rep.create.render_product(rep.create.camera(), (256, 256))
        writer = rep.writers.get("BasicWriter", init_params={"rgb": True, "output_dir": "_out"}, render_products=rp)

        def get_rgb(writer):
            writer_data = writer.get_data()
            for _rp in writer_data["annotators"]["rgb"]:
                return writer_data["annotators"]["rgb"][_rp]["data"]

        await rep.orchestrator.step_async()
        self.assertEqual(get_rgb(writer).shape[:2], (256, 256))

        # Detach
        writer.detach()

        # Change resolution
        rp.hydra_texture.set_width(1024)
        rp.hydra_texture.set_height(1024)

        # Re-attach
        writer.attach(rp)

        await rep.orchestrator.step_async()

        self.assertEqual(get_rgb(writer).shape[:2], (1024, 1024))

        # Test without detaching

        # Change resolution
        rp.hydra_texture.set_width(512)
        rp.hydra_texture.set_height(512)

        await rep.orchestrator.step_async()

        self.assertEqual(get_rgb(writer).shape[:2], (512, 512))

    async def test_data_structure_legacy_single(self):
        class AnnotatorWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]

            def write(self, data):
                pass

        writer = AnnotatorWriter()
        writer.initialize()
        writer.attach(rep.create.render_product(rep.create.camera(name="Cam0"), (512, 256), name="Testing"))

        await rep.orchestrator.step_async()

        writer_data = writer.get_data()

        self.assertTrue("LdrColor" in writer_data, "Unable to find `LdrColor` key in writer data.")
        self.assertTrue("camera" in writer_data["rp_Testing"], "Unable to find `camera` key in writer data.")
        self.assertTrue("resolution" in writer_data["rp_Testing"], "Unable to find `resolution` key in writer data.")

    async def test_data_structure_annotators_single(self):
        class AnnotatorWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]
                self.data_structure = "annotator"

            def write(self, data):
                pass

        writer = AnnotatorWriter()
        writer.initialize()
        writer.attach(rep.create.render_product(rep.create.camera(name="Cam0"), (512, 256), name="Testing"))

        await rep.orchestrator.step_async()

        writer_data = writer.get_data()

        self.assertTrue("annotators" in writer_data, "Unable to find `annotators` key in writer data.")
        self.assertTrue("camera" in writer_data["annotators"], "Unable to find `camera` key in writer data.")
        self.assertTrue("resolution" in writer_data["annotators"], "Unable to find `resolution` key in writer data.")
        self.assertTrue("LdrColor" in writer_data["annotators"], "Unable to find `LdrColor` key in writer data.")
        self.assertTrue(
            "Testing" in writer_data["annotators"]["camera"],
            "Unable to find `Testing` key in writer data.",
        )
        self.assertTrue(
            "Testing" in writer_data["annotators"]["resolution"],
            "Unable to find `Testing` key in writer data.",
        )
        self.assertTrue(
            "Testing" in writer_data["annotators"]["LdrColor"],
            "Unable to find `Testing` key in writer data.",
        )

    async def test_data_structure_renderProduct_single(self):
        class AnnotatorWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]
                self.data_structure = "renderProduct"

            def write(self, data):
                pass

        writer = AnnotatorWriter()
        writer.initialize()
        writer.attach(rep.create.render_product(rep.create.camera(name="Cam0"), (512, 256), name="Testing"))

        await rep.orchestrator.step_async()

        writer_data = writer.get_data()

        self.assertTrue("renderProducts" in writer_data, "Unable to find `annotators` key in writer data.")
        self.assertTrue(
            "camera" in writer_data["renderProducts"]["Testing"],
            "Unable to find `camera` key in writer data.",
        )
        self.assertTrue(
            "resolution" in writer_data["renderProducts"]["Testing"],
            "Unable to find `resolution` key in writer data.",
        )
        self.assertTrue(
            "LdrColor" in writer_data["renderProducts"]["Testing"],
            "Unable to find `LdrColor` key in writer data.",
        )

    async def test_data_structure_legacy_multi(self):
        class AnnotatorWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]

            def write(self, data):
                pass

        writer = AnnotatorWriter()
        writer.initialize()
        rp0 = rep.create.render_product(rep.create.camera(name="Cam0"), (512, 256), name="Testing0")
        rp1 = rep.create.render_product(rep.create.camera(name="Cam1"), (123, 456), name="Testing1")
        writer.attach([rp0, rp1])

        await rep.orchestrator.step_async()

        writer_data = writer.get_data()

        for idx, res, cam in zip([0, 1], [(512, 256), (123, 456)], ["Cam0", "Cam1"]):
            self.assertTrue(
                f"rp_Testing{idx}" in writer_data,
                f"Unable to find `rp_Testing{idx}` key in writer data.",
            )
            self.assertTrue(
                f"LdrColor-Testing{idx}" in writer_data,
                f"Unable to find `LdrColor-Testing{idx}` key in writer data.",
            )
            self.assertTrue("camera" in writer_data[f"rp_Testing{idx}"], "Unable to find `camera` key in writer data.")
            self.assertTrue(
                "resolution" in writer_data[f"rp_Testing{idx}"],
                "Unable to find `resolution` key in writer data.",
            )
            self.assertEqual(writer_data[f"rp_Testing{idx}"]["camera"], f"/Replicator/{cam}_Xform/{cam}")
            self.assertEqual(tuple(writer_data[f"rp_Testing{idx}"]["resolution"]), res)

    async def test_data_structure_annotators_multi(self):
        class AnnotatorWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]
                self.data_structure = "annotator"

            def write(self, data):
                pass

        writer = AnnotatorWriter()
        writer.initialize()
        rp0 = rep.create.render_product(rep.create.camera(name="Cam0"), (512, 256), name="Testing0")
        rp1 = rep.create.render_product(rep.create.camera(name="Cam1"), (123, 456), name="Testing1")
        writer.attach([rp0, rp1])

        await rep.orchestrator.step_async()

        writer_data = writer.get_data()

        self.assertTrue("annotators" in writer_data, "Unable to find `annotators` key in writer data.")
        self.assertTrue("camera" in writer_data["annotators"], "Unable to find `camera` key in writer data.")
        self.assertTrue("resolution" in writer_data["annotators"], "Unable to find `resolution` key in writer data.")
        self.assertTrue("LdrColor" in writer_data["annotators"], "Unable to find `LdrColor` key in writer data.")
        for idx, res, cam in zip([0, 1], [(512, 256), (123, 456)], ["Cam0", "Cam1"]):
            self.assertTrue(
                f"Testing{idx}" in writer_data["annotators"]["camera"],
                f"Unable to find `Testing{idx}` key in writer data.",
            )
            self.assertTrue(
                f"Testing{idx}" in writer_data["annotators"]["resolution"],
                f"Unable to find `Testing{idx}` key in writer data.",
            )
            self.assertTrue(
                f"Testing{idx}" in writer_data["annotators"]["LdrColor"],
                f"Unable to find `Testing{idx}` key in writer data.",
            )
            self.assertEqual(writer_data["annotators"]["camera"][f"Testing{idx}"], f"/Replicator/{cam}_Xform/{cam}")
            self.assertEqual(tuple(writer_data["annotators"]["resolution"][f"Testing{idx}"]), res)

    async def test_data_structure_renderProduct_multi(self):
        class AnnotatorWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]
                self.data_structure = "renderProduct"

            def write(self, data):
                pass

        writer = AnnotatorWriter()
        writer.initialize()
        rp0 = rep.create.render_product(rep.create.camera(name="Cam0"), (512, 256), name="Testing0")
        rp1 = rep.create.render_product(rep.create.camera(name="Cam1"), (123, 456), name="Testing1")
        writer.attach([rp0, rp1])

        await rep.orchestrator.step_async()

        writer_data = writer.get_data()

        self.assertTrue("renderProducts" in writer_data, "Unable to find `annotators` key in writer data.")
        for idx, res, cam in zip([0, 1], [(512, 256), (123, 456)], ["Cam0", "Cam1"]):
            self.assertTrue(
                "camera" in writer_data["renderProducts"][f"Testing{idx}"],
                "Unable to find `camera` key in writer data.",
            )
            self.assertTrue(
                "resolution" in writer_data["renderProducts"][f"Testing{idx}"],
                "Unable to find `resolution` key in writer data.",
            )
            self.assertTrue(
                "LdrColor" in writer_data["renderProducts"][f"Testing{idx}"],
                "Unable to find `LdrColor` key in writer data.",
            )
            self.assertEqual(writer_data["renderProducts"][f"Testing{idx}"]["camera"], f"/Replicator/{cam}_Xform/{cam}")
            self.assertEqual(tuple(writer_data["renderProducts"][f"Testing{idx}"]["resolution"]), res)

    async def test_node_connection_template(self):
        hydra_texture = rep.create.render_product("/OmniverseKit_Persp", [1, 1])

        rep.writers.register_node_writer(
            name="test_writer",
            node_type_id="omni.replicator.core.OgnGetPrims",
            annotators=[
                "RtxSensorCpu" + "Ptr",
                omni.syntheticdata.SyntheticData.NodeConnectionTemplate("PostProcessDispatcher"),
            ],
            category="Test",
        )
        writer = rep.writers.get("test_writer")
        writer.initialize()
        writer.attach([hydra_texture])
        await rep.orchestrator.step_async()

    async def test_writer_memory_leak(self):
        # Ensure that repeated writer attach/detach does not leak memory (NVBug-5319074)
        # Set MB threshold
        memory_threshold = 1.0

        # Initialize writer and take one step
        rp = rep.create.render_product(rep.create.camera(), (1024, 1024))

        async def writer_loop():
            writer = rep.writers.get("BasicWriter")
            writer.initialize(output_dir=self.out_dir, rgb=True)
            writer.attach(rp)

            await rep.orchestrator.step_async()

            writer.detach()

        # A few frames are needed for memory use to stabilize
        warmup_period = 5
        for _ in range(warmup_period):
            await writer_loop()

            mem = get_memory_usage(os.getpid())
            print(f"Memory usage: {mem} MB")

        # Get memory usage
        memory_start = get_memory_usage(os.getpid())

        # Render a step
        await writer_loop()

        # Get memory usage
        gc.collect()
        memory_end = get_memory_usage(os.getpid())
        self.assertLess(
            memory_end, memory_start + memory_threshold, f"Memory usage increased by {memory_end - memory_start} MB"
        )

    async def test_writer_with_two_identical_annotators(self):
        """NVBug-5493371"""
        rp = rep.create.render_product(rep.create.camera(), (512, 512))

        class MyWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor", "LdrColor"]

            def write(self, data):
                pass

        writer = MyWriter()
        writer.initialize()
        writer.attach(rp)
        writer.detach()

    async def test_annotator_list_property(self):
        class Writer1(rep.Writer):
            """Ensure annotator lists are instance-specific. (NVBug-5383689)"""

            def __init__(self):
                self.annotators.append("LdrColor")

            def write(self, data):
                pass

        class Writer2(rep.Writer):
            def __init__(self):
                self.annotators.append("HdrColor")

            def write(self, data):
                pass

        writer1 = Writer1()
        writer2 = Writer2()

        self.assertTrue("HdrColor" not in writer1.annotators, writer1.annotators)
        self.assertTrue("LdrColor" not in writer2.annotators, writer2.annotators)

    async def test_writer_attach_detach(self):
        rep.create.cube(semantics=[("class", "cube")])
        rep.create.sphere(position=(1, 1, 0), semantics=[("class", "sphere")])
        basic_writer = rep.WriterRegistry.get("BasicWriter")
        basic_writer.initialize(
            output_dir=self.out_dir,
            rgb=True,
            bounding_box_2d_tight=True,
            bounding_box_2d_loose=True,
            semantic_segmentation=True,
            colorize_semantic_segmentation=True,
            instance_id_segmentation=True,
            colorize_instance_id_segmentation=True,
            instance_segmentation=True,
            colorize_instance_segmentation=True,
            distance_to_camera=True,
            distance_to_image_plane=True,
            bounding_box_3d=True,
        )
        render_product = rep.create.render_product("/OmniverseKit_Persp", (1024, 512))
        for _ in range(2):
            basic_writer.attach(render_product)
            await rep.orchestrator._orchestrator._initialize_async()
            await rep.orchestrator.step_async()
            await rep.orchestrator.step_async()
            await omni.kit.app.get_app().next_update_async()
            for i in range(2):
                print(f"  Step {i}")
                await rep.orchestrator.step_async()
            await rep.orchestrator.wait_until_complete_async()

            basic_writer.detach()

        # Ensure all annotators were detached
        stage = omni.usd.get_context().get_stage()
        session_layer = stage.GetSessionLayer()
        with Usd.EditContext(stage, session_layer):
            post_process_children = stage.GetPrimAtPath("/Render/PostProcess").GetChildren()
            self.assertEqual(len(post_process_children), 0, "PostProcess nodes remain after writer detach")
            post_render_children = stage.GetPrimAtPath(f"{render_product.path}/PostRender").GetChildren()
            self.assertEqual(len(post_render_children), 0, "PostRender nodes remain after writer detach")
