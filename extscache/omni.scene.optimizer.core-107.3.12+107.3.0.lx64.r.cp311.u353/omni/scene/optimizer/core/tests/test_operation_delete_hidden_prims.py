__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


from pxr import UsdGeom

from .test_utils import Test_Operation


def _count_hidden(stage):
    """Count hidden prims in a stage"""
    count = 0
    for prim in stage.Traverse():
        imageable = UsdGeom.Imageable(prim)
        if imageable:
            vis_attr = imageable.GetVisibilityAttr()
            if vis_attr.Get() == UsdGeom.Tokens.invisible:
                count += 1

    return count


class Test_Operation_Delete_Hidden_Prims(Test_Operation):

    OPERATION = "deleteHiddenPrims"

    async def test_delete_hidden_prims(self):
        """Test basic deletion of hidden prims"""

        stage = self._open_stage("deleteHiddenPrims.usda")

        count = _count_hidden(stage)
        self.assertEqual(count, 3)

        self._execute_command({})

        count = _count_hidden(stage)
        self.assertEqual(count, 0)
