# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import os
import unittest
import omni.kit.test
from omni.kit.viewport.utility import get_active_viewport
from omni.syntheticdata import SyntheticData

# Test the semantic filter

class TestDisplayRenderVar(omni.kit.test.AsyncTestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.render_product_path = get_active_viewport().render_product_path
        await omni.kit.app.get_app().next_update_async()

    async def wait_for_frames(self):
        wait_iterations = 6
        for _ in range(wait_iterations):
            await omni.kit.app.get_app().next_update_async()

    async def test_valid_ldrcolor_texture(self):
        SyntheticData.Get().activate_node_template("LdrColorDisplay", 0, [self.render_product_path])
        await self.wait_for_frames()
        display_output_names = ["outputs:rpResourcePtr", "outputs:width", "outputs:height", "outputs:format"]
        display_outputs = SyntheticData.Get().get_node_attributes("LdrColorDisplay", display_output_names, self.render_product_path)
        assert(display_outputs and all(o in display_outputs for o in display_output_names) and display_outputs["outputs:rpResourcePtr"] != 0 and display_outputs["outputs:format"] == 11)
        SyntheticData.Get().deactivate_node_template("LdrColorDisplay", 0, [self.render_product_path])

    async def test_valid_bbox3d_texture(self):
        SyntheticData.Get().activate_node_template("BoundingBox3DDisplay", 0, [self.render_product_path])
        await self.wait_for_frames()
        display_output_names = ["outputs:rpResourcePtr", "outputs:width", "outputs:height", "outputs:format"]
        display_outputs = SyntheticData.Get().get_node_attributes("BoundingBox3DDisplay", display_output_names, self.render_product_path)
        assert(display_outputs and all(o in display_outputs for o in display_output_names) and display_outputs["outputs:rpResourcePtr"] != 0 and display_outputs["outputs:format"] == 11)
        SyntheticData.Get().deactivate_node_template("BoundingBox3DDisplay", 0, [self.render_product_path])

    async def test_valid_cam3dpos_texture(self):
        SyntheticData.Get().activate_node_template("Camera3dPositionDisplay", 0, [self.render_product_path])
        await self.wait_for_frames()
        display_output_names = ["outputs:rpResourcePtr", "outputs:width", "outputs:height", "outputs:format"]
        display_outputs = SyntheticData.Get().get_node_attributes("Camera3dPositionDisplay", display_output_names, self.render_product_path)
        assert(display_outputs and all(o in display_outputs for o in display_output_names) and display_outputs["outputs:rpResourcePtr"] != 0 and display_outputs["outputs:format"] == 11)
        SyntheticData.Get().deactivate_node_template("Camera3dPositionDisplay", 0, [self.render_product_path])
    