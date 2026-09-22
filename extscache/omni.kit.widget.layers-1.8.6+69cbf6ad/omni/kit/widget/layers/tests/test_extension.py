import omni.kit.test
from pxr import Sdf
from .base import TestLayerUIBase


class TestLayerExtension(TestLayerUIBase):

    async def setUp(self):
        await super().setUp()
        self.stage = await self.prepare_empty_stage()

    async def tearDown(self):
        await self.usd_context.close_stage_async()

    async def test_layer_insert(self):
        layer = Sdf.Layer.CreateAnonymous()
        root_layer = self.stage.GetRootLayer()

        self.layers_instance._on_icon_menu_click(None, layer.identifier)
        self.assertEqual(len(root_layer.subLayerPaths), 1)
        self.assertEqual(root_layer.subLayerPaths[0], layer.identifier)

        # Dont allow to insert root layer
        self.layers_instance._on_icon_menu_click(None, root_layer.identifier)
        self.assertEqual(len(root_layer.subLayerPaths), 1)
        self.assertEqual(root_layer.subLayerPaths[0], layer.identifier)

        # Don't allow to insert duplicate layer
        self.layers_instance._on_icon_menu_click(None, layer.identifier)
        self.assertEqual(len(root_layer.subLayerPaths), 1)
        self.assertEqual(root_layer.subLayerPaths[0], layer.identifier)
