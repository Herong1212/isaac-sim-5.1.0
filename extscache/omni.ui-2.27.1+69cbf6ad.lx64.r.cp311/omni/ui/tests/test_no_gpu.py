## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestNoGPU"]

import omni.kit.test
import omni.ui as ui


class TestNoGPU(omni.kit.test.AsyncTestCase):
    def test_workspace(self):
        """Test using ui.Workspace will not crash if no GPUs are present."""
        windows = ui.Workspace.get_windows()

        # Pass on release or odder debug builds
        self.assertTrue((windows == []) or (f"{windows}" == "[Debug##Default]"))

        # Test this call doesn't crash
        ui.Workspace.clear()

    def test_window(self):
        """Test using ui.Window will not crash if no GPUs are present."""
        window = ui.Window("Name", width=512, height=512)
        # Test is not that window holds anything of value, just that app has not crashed
