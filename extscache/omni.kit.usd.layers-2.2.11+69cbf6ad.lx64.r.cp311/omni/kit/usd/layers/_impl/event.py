# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LayerEventType"]

import carb

from enum import IntEnum
from .._omni_kit_usd_layers import LayerEventType as NativeLayerEventType


class DerivedLayerEventType(IntEnum):
    AUTO_RELOAD_LAYERS_CHANGED = carb.events.type_from_string("omni.kit.usd.layers@auto_reload_layers")


__all_name_values = [(name, int(value)) for name, value in NativeLayerEventType.__members__.items()]
__all_name_values.extend([(name, int(value)) for name, value in DerivedLayerEventType.__members__.items()])

LayerEventType = IntEnum("LayerEventType", __all_name_values)
LayerEventType.__doc__ = NativeLayerEventType.__doc__
