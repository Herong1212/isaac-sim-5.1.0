# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "CreatePortCommand",
    "ConnectAttrWithSubgraphCommand",
    "DisconnectAttrWithSubgraphCommand",
    "SubdivideConnectionCommand",
]

from typing import List

import carb
import omni.kit.commands
from omni.usd.commands import UsdStageHelper
from pxr import Sdf


class CreatePortCommand(omni.kit.commands.Command, UsdStageHelper):
    """
    Create port on the subgraph prim, since og doesn't support subgraph attribute yet

    ### Arguments:

        `prim_path : Sdf.Path`
            The path of the prim we need to add the new port.

        `port_name : str`
            The name of the port. The attribute name will be `outputs:port_name`.

        `port_type : Sdf.ValueTypeName`
            The type of the port.

        `stage : Optional[int]`
            The stage it's necessary to add the new port. If None, it takes
            the stage from the USD Context.
    """

    def __init__(
        self,
        prim_path: Sdf.Path,
        port_name: str,
        port_type: Sdf.ValueTypeName,
        stage=None,
    ):
        UsdStageHelper.__init__(self, stage)
        self._prim_path = prim_path
        self._port_name = port_name
        self._port_type = port_type
        self._created_attr_name = None

    def _create_port(self, prim):
        input_port = prim.CreateAttribute(self._port_name, self._port_type)
        if input_port:
            return input_port.GetName()

        carb.log_error(f"Failed to generate port {self._port_name} for {prim} with type {self._port_type}")
        return None

    def do(self):
        stage = self._get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)

        self._created_attr_name = self._create_port(prim)

    def undo(self):
        if self._created_attr_name is None:
            return

        stage = self._get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)
        prim.RemoveProperty(self._created_attr_name)


class ConnectAttrWithSubgraphCommand(omni.kit.commands.Command, UsdStageHelper):
    """
    Connect with subgraph attribute, since og doesn't support subgraph attribute yet,
    we cant use `og.cmds.ConnectAttrs`

    ### Arguments:

        `src_path : Sdf.Path`
            The src path of the connection.

        `dest_path : Sdf.Path`
            The dest path of the connection.

        `stage : Optional[int]`
            The stage it's necessary to create new connection. If None, it takes
            the stage from the USD Context.
    """

    def __init__(
        self,
        src_path: Sdf.Path,
        dest_path: Sdf.Path,
        allow_remove: bool = True,
        stage=None,
    ):
        UsdStageHelper.__init__(self, stage)
        self._src_path = src_path
        self._dest_path = dest_path
        self._allow_remove = allow_remove
        self._dest_attr = None

    def do(self):
        stage = self._get_stage()
        self._dest_attr = stage.GetAttributeAtPath(self._dest_path)

        if self._dest_attr:
            self._dest_attr.AddConnection(self._src_path)

    def undo(self):
        if self._allow_remove and self._dest_attr:
            self._dest_attr.RemoveConnection(self._src_path)


class DisconnectAttrWithSubgraphCommand(omni.kit.commands.Command, UsdStageHelper):
    """
    Disconnect with subgraph attribute, since og doesn't support subgraph attribute yet,
    we can't use `og.cmds.DisconnectAttrs`

    ### Arguments:

        `src_path : Sdf.Path`
            The src path of the connection.

        `dest_path : Sdf.Path`
            The dest path of the connection.

        `stage : Optional[int]`
            The stage it's necessary to create new connection. If None, it takes
            the stage from the USD Context.
    """

    def __init__(
        self,
        src_path: Sdf.Path,
        dest_path: Sdf.Path,
        stage=None,
    ):
        UsdStageHelper.__init__(self, stage)
        self._src_path = src_path
        self._dest_path = dest_path
        self._dest_attr = None

    def do(self):
        stage = self._get_stage()
        self._dest_attr = stage.GetAttributeAtPath(self._dest_path)

        if self._dest_attr:
            self._dest_attr.RemoveConnection(self._src_path)

    def undo(self):
        if not self._dest_attr:
            return

        self._dest_attr.AddConnection(self._src_path)


class SubdivideConnectionCommand(omni.kit.commands.Command, UsdStageHelper):
    """
    Example: graph: A->B->C->D->E->F, if A and F are the actual connection, while B and C are the user disconnect ports
    from ui. src_to_actual_src will be [B, A] and dest_to_actual_dest will be [C, D, E, F]. While we try to disconnect A
    and F, we need to create the sub-connections between A and F first. This is followed by a `og.cmds.DisconnectAttrs`
    command
    ### Arguments:

        `src_to_actual_src : List[Sdf.Path]`
            This is a list of Sdf.Path from the ui src port until the connected actual src port

        `dest_to_actual_dest : List[Sdf.Path]`
            This is a list of Sdf.Path from the ui dest port until the connected actual dest port

        `stage : Optional[int]`
            The stage it's necessary to create new connection. If None, it takes
            the stage from the USD Context.
    """

    def __init__(
        self,
        src_to_actual_src: List[Sdf.Path],
        dest_to_actual_dest: List[Sdf.Path],
        stage=None,
    ):
        UsdStageHelper.__init__(self, stage)
        self._src_to_actual_src = src_to_actual_src
        self._dest_to_actual_dest = dest_to_actual_dest
        self._actual_dest_attr = None
        self._actual_src_to_actual_dest = None

    def do(self):
        stage = self._get_stage()
        self._actual_dest_attr = stage.GetAttributeAtPath(self._dest_to_actual_dest[-1])
        if not self._actual_dest_attr:
            return

        # presume all the type are the same
        dest_type = self._actual_dest_attr.GetTypeName()

        actual_src_to_src = self._src_to_actual_src.copy()
        actual_src_to_src.reverse()
        self._actual_src_to_actual_dest = actual_src_to_src + self._dest_to_actual_dest

        if len(self._actual_src_to_actual_dest) > 2:
            for src, dest in zip(self._actual_src_to_actual_dest[:-1], self._actual_src_to_actual_dest[1:]):
                dest_prim = stage.GetPrimAtPath(dest.GetPrimPath())
                dest_name = dest.name
                dest_attr = dest_prim.GetAttribute(dest_name)
                if not dest_attr:
                    dest_attr = dest_prim.CreateAttribute(dest_name, dest_type)
                if dest_attr:
                    dest_attr.AddConnection(src)

    def undo(self):
        # we want to keep the new created port and sub connections
        pass


#  _____   ______  _____   _____   ______  _____         _______  ______  _____
# |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
# | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
# | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
# | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
# |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/

import re  # noqa: PLC0411,E402

from omni.graph.tools import DeprecateMessage  # noqa: PLC0412,E402


class _FilterStackTrace:
    # Use this context manager to filter low level omni.kit.commands calls out of DeprecationMessage's
    # traceback so that it focuses on where the command was being called from. E.g:
    #
    #   with FilterStackTrace():
    #       DeprecateMessage.deprecated("Use new_cmd instead.")
    #
    def __enter__(self):
        self.filter = DeprecateMessage.RE_IGNORE  # noqa: PLW0201
        DeprecateMessage.RE_IGNORE = re.compile(DeprecateMessage.RE_IGNORE.pattern + r"|omni\.kit\.commands")

    def __exit__(self, *args, **kwargs):
        DeprecateMessage.RE_IGNORE = self.filter
