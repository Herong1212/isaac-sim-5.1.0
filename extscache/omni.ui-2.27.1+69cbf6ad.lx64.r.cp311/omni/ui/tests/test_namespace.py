## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
import omni.ui as ui


def one():
    return 1


class TestNamespace(OmniUiTest):
    """Testing ui.Workspace"""

    async def test_namespace(self):
        """Testing window selection callback"""

        subscription = ui.add_to_namespace(one)
        self.assertIn("one", dir(ui))
        self.assertEqual(ui.one(), 1)
        del subscription
        subscription = None
        self.assertNotIn("one", dir(ui))

        # Testing module=None
        ui.add_to_namespace()
