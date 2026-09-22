# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.graph.core as og

from .catalog_delegate import OmniGraphCatalogTreeDelegate
from .catalog_model import OmniGraphNodeQuickSearchModel, OmniGraphNodeTypeCatalogModel

# Deprecated. Will be removed once we no longer need to support apps using
# omni.graph < 1.53.
from .extension import OmniGraphWindowCoreExtension, _is_kit_version_or_greater, register_stage_graph_opener
from .graph_commands import (
    ConnectAttrWithSubgraphCommand,
    CreatePortCommand,
    DisconnectAttrWithSubgraphCommand,
    SubdivideConnectionCommand,
)
from .graph_delegate import OmniGraphNodeDelegate
from .graph_model import OmniGraphModel
from .graph_widget import OmniGraphWidget
from .graph_window import OmniGraphWindow

# Not available prior to Kit 105 releases.
_kit_major_version, _ = og.get_kit_version()
if _kit_major_version >= 105:
    from .actions import OmniGraphActions
    from .hotkeys import OmniGraphHotkeys
