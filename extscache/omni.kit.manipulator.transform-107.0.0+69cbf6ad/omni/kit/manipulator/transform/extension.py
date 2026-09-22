# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Transform manipulator extension"""

import omni.ext

from .style import get_default_style

SHOW_EXAMPLE = False


class TransformManipulatorExt(omni.ext.IExt):
    """A class that represents the Transform Manipulator Extension.

    This class handles the lifecycle of the transform manipulator extension by defining startup and shutdown behaviors.
    """

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        """Initializes the extension.

        Args:
            ext_id (str): The ID of the current extension used with the extension manager.
        """
        if SHOW_EXAMPLE:
            from .example import SimpleManipulatorExample

            self._example = SimpleManipulatorExample()

    def on_shutdown(self):
        """Performs cleanup operations as the extension shuts down."""
        if SHOW_EXAMPLE:
            self._example.destroy()
            self._example = None
