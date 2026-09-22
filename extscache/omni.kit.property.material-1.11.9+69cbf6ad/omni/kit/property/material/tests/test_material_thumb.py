from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialThumb(MaterialPropertiesTestBase):
    async def test_material_thumb(self):
        scene_file_path = self._get_scene_path("thumbnail_test.usda")
        await self._load_scene(scene_file_path)
        await self._dock_test_window(450, 285)
        await self._select_prims(["/World/Sphere"])
        await self._golden_image_compare("test_thumb_with_alpha.png")
