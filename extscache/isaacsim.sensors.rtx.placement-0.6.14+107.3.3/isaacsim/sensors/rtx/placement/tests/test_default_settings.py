import omni.kit
import omni.kit.test
import omni.usd
from isaacsim.sensors.rtx.placement.camera_placement.camera_placement_utils import CameraPlacementUtils

class TestCameraSettings(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_camera_range_settings(self):
        """
        Test all settings related to the camera placment.
        """
        # check whether the default camera height range, lookdown angle range and camera distance ranges are correct
        camera_placement_setting_info_list = list(CameraPlacementUtils.get_camera_info_setting())
        for camera_placement_range in camera_placement_setting_info_list:
            self.assertLess(camera_placement_range[0] ,  camera_placement_range[1])
