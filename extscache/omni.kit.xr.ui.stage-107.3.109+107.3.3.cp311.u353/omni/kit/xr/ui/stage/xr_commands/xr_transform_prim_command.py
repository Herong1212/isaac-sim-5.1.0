# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Optional

import omni.kit.commands
import omni.usd
from omni.kit.xr.core import XRCore
from pxr import Gf

# This command records a transform manipulation by the current xr tools
# The command needs the name of the prim, the layer on which to edit,
# the new and old transform and whether to remove the prim spec from the layer on undo


class XRTransformPrimCommand(omni.kit.commands.Command):
    """
    Command issued when grab or move tool modify a prim.
    """

    def __init__(
        self,
        prim_path: str,
        layer_identifier: Optional[str],
        new_transform: Gf.Matrix4d,
        old_transform: Gf.Matrix4d,
        remove_from_layer: bool,
    ):
        # Name of the prim that needs to be changed
        self.__prim_path: str = prim_path

        # The name of the layer that the change needs to be recorded on
        self.__layer_identifier: Optional[str] = layer_identifier

        # The new transform
        self.__new_transform = new_transform

        # The old transform (needed for usdrt/session layer when the preview of the change is on the layer that needs to be edited )
        self.__old_transform = old_transform

        # If undo is just removing prim spec from layer
        # Right now our method is approximate an undo. It does not handle the case where transform is spread out over multiple
        # layers including the one that is being editted.
        self.__remove_from_layer = remove_from_layer

    def do(self) -> None:
        """
        Function called to make the change in the position of the prim.
        """

        xrcore: XRCore = XRCore.get_singleton()

        if self.__layer_identifier is None:
            # usdrt update
            xrcore.set_world_transform_matrix(self.__prim_path, self.__new_transform)
        else:
            # normal usd update, we need to specify the layer where the change is going to be made
            xrcore.set_world_transform_matrix(self.__prim_path, self.__new_transform, self.__layer_identifier)

    def undo(self) -> None:
        """
        Function called to undo the change in the position of the prim
        """

        xrcore: XRCore = XRCore.get_singleton()

        if self.__layer_identifier is None:
            # usdrt update
            xrcore.set_world_transform_matrix(self.__prim_path, self.__old_transform)
        else:
            if self.__remove_from_layer:
                # If no transform existed on the layer before do, then remove prim spec from layer
                # This avoids setting it to old value in the edit layer, where the no opinion was present to start with
                xrcore.remove_prim_from_layer(self.__prim_path, self.__layer_identifier)
            else:
                # This will undo the transform by writing out the old transform on the edit layer
                xrcore.set_world_transform_matrix(self.__prim_path, self.__old_transform, self.__layer_identifier)


# Register with kit
omni.kit.commands.register_all_commands_in_module(__name__)
