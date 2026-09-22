# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides a command to disconnect inputs from their sources within the USD shading system."""


__all__ = [
    "UsdShadeDisconnectCommand",
]

import omni.kit.commands
from pxr import UsdShade


class UsdShadeDisconnectCommand(omni.kit.commands.Command):
    """A command to disconnect a target input from its source in USD's shading system.

    This command handles the disconnection of a UsdShade Input from either an Output or another Input that it is connected to. It is capable of storing the source information for undo operations.

    Args:
        target (:obj:`UsdShade.Input`): The input to be disconnected from its source."""

    def __init__(self, target: UsdShade.Input):
        """Initializes the command to disconnect a shading input."""
        super().__init__()
        self._target = target
        self._source = None

    def do(self):
        """Executes the disconnection of a shading input."""
        # Get source for undo
        if self._target.HasConnectedSource():
            # The result is (<pxr.UsdShade.ConnectableAPI>, 'out', pxr.UsdShade.AttributeType.Output)
            source, source_name, source_type = self._target.GetConnectedSource()

            if source_type == UsdShade.AttributeType.Output:
                self._source = source.GetOutput(source_name)
            else:  # UsdShade.AttributeType.Input
                # Input-to-input connections. In UsdShade it's possible.
                self._source = source.GetInput(source_name)

            # Disconnect
            self._target.DisconnectSource()

    def undo(self):
        """Reverts the disconnection of a shading input."""
        if not self._target or not self._source:  # pragma: no cover
            # It wasn't connected
            return

        self._target.ConnectToSource(self._source)
