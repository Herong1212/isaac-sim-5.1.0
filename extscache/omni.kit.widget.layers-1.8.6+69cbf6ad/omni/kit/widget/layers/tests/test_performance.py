import omni.kit.test
import time
from .base import TestLayerUIBase
from pxr import Sdf, Usd


class TestLayerPerformance(TestLayerUIBase):
    async def setUp(self):
        await super().setUp()
        self.stage = await self.prepare_empty_stage()

    async def tearDown(self):
        await self.usd_context.close_stage_async()
        await super().tearDown()

    async def test_create_10_sublayers(self):
        start_time = time.monotonic()
        root_layer = self.stage.GetRootLayer()
        self.create_sublayers(root_layer, [10])
        print(f"Time costed to create 10 sublayers: {time.monotonic() - start_time}")

    async def test_search_1000_prim_specs(self):
        temp_layer = Sdf.Layer.CreateAnonymous()
        temp_stage = Usd.Stage.Open(temp_layer)
        self.create_prim_specs(temp_stage, Sdf.Path.absoluteRootPath, [1000])
        await self.usd_context.attach_stage_async(temp_stage)
        start_time = time.monotonic()
        layer_model = self.layers_instance.get_layer_model()
        layer_model.filter_by_text("xform")
        print(f"Time costed to search 1000 prim specs: {time.monotonic() - start_time}")
