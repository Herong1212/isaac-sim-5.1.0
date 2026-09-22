# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb

from enum import Enum
from pxr import Usd, Sdf


class Value_On_Layer(Enum):
    """Enum for the strength type of an attribute value."""

    No_Value = 0
    """No value is authored to the stage."""

    ON_CURRENT_LAYER = 0
    """Value is authored to the current edit target."""

    ON_STRONGER_LAYER = 1
    """Value is authored to a stronger layer than the current edit target."""

    ON_WEAKER_LAYER = 2
    """Value is authored to a weaker layer than the current edit target."""


def get_frame_time_code(time, fps):
    """Internal. Utility to convert fps into time code."""

    if fps <= 0:
        fps = 24
    return round(time * fps)


def get_frame_time(time_code, fps):
    """Internal. Utility to convert time code into frame time."""
    if fps <= 0:
        fps = 24
    return round(time_code) / fps


def attr_has_timesample_on_key(attr: Usd.Attribute, time_code: Usd.TimeCode):
    """Internal. If attribute has authored value to the specific time code."""

    if not isinstance(attr, Usd.Attribute) or not isinstance(attr, Usd.TimeCode) or time_code.IsDefault():
        return False
    time_samples = attr.GetTimeSamples()
    time_code_value = time_code.GetValue()
    if round(time_code_value) != time_code_value:
        carb.log_warn(f"Error: TimeSample Value {time_code_value} should be without decimal part.")
        return False
    return time_code_value in time_samples


def get_attribute_effective_timesample_layer_info(stage, attr: Usd.Attribute):
    """Internal. Gets the strength type and layer for the timesamples of the attribute."""

    if attr.GetNumTimeSamples() == 0:
        return Value_On_Layer.No_Value, None
    attr_layers = attr.GetResolveInfo().GetNode().layerStack.layers
    authoring_layer = stage.GetEditTarget().GetLayer()
    isOnStrongerLayer = True
    for layer in attr_layers:
        attr_spec = layer.GetAttributeAtPath(attr.GetPath())
        if attr_spec and len(attr_spec.GetInfo("timeSamples")) > 0:
            if layer == authoring_layer:
                return Value_On_Layer.ON_CURRENT_LAYER, layer
            elif isOnStrongerLayer:
                return Value_On_Layer.ON_STRONGER_LAYER, layer
            else:
                return Value_On_Layer.ON_WEAKER_LAYER, layer
        else:  # no attrSpec or no timesample
            if layer == authoring_layer:
                isOnStrongerLayer = False

    return Value_On_Layer.No_Value, None


def get_attribute_effective_defaultvalue_layer_info(stage, attr: Usd.Attribute):
    """Internal. Gets the strength type and layer for the default value of the attribute."""

    # if an attribute doesn't have any authoring value, GetNode() assert out
    # guard it with this HasAuthoredValue() to prevent from crashing
    if not attr or not attr.HasAuthoredValue():
        return Value_On_Layer.No_Value, None
    attr_layers = attr.GetResolveInfo().GetNode().layerStack.layers
    authoring_layer = stage.GetEditTarget().GetLayer()
    isOnStrongerLayer = True
    for layer in attr_layers:
        attr_spec = layer.GetAttributeAtPath(attr.GetPath())
        if attr_spec and attr_spec.GetInfo("default"):
            if layer == authoring_layer:
                return Value_On_Layer.ON_CURRENT_LAYER, layer
            elif isOnStrongerLayer:
                return Value_On_Layer.ON_STRONGER_LAYER, layer
            else:
                return Value_On_Layer.ON_WEAKER_LAYER, layer
        else:  # no attrSpec or no timesample
            if layer == authoring_layer:
                isOnStrongerLayer = False

    return Value_On_Layer.No_Value, None

def get_attribute_effective_value_layer_info(stage, attr: Usd.Attribute):
    """Internal. Gets the strength type and layer for the default value or timesamples of the attribute."""

    # if an attribute doesn't have any authoring value, GetNode() assert out
    # guard it with this HasAuthoredValue() to prevent from crashing
    if not attr or not attr.HasAuthoredValue():
        return Value_On_Layer.No_Value, None
    attr_layers = attr.GetResolveInfo().GetNode().layerStack.layers
    authoring_layer = stage.GetEditTarget().GetLayer()
    isOnStrongerLayer = True
    for layer in attr_layers:
        attr_spec = layer.GetAttributeAtPath(attr.GetPath())
        if attr_spec and (attr_spec.GetInfo("default") or len(attr_spec.GetInfo("timeSamples")) > 0):
            if layer == authoring_layer:
                return Value_On_Layer.ON_CURRENT_LAYER, layer
            elif isOnStrongerLayer:
                return Value_On_Layer.ON_STRONGER_LAYER, layer
            else:
                return Value_On_Layer.ON_WEAKER_LAYER, layer
        else:  # no attrSpec or no timesample
            if layer == authoring_layer:
                isOnStrongerLayer = False

    return Value_On_Layer.No_Value, None


def copy_timesamples_from_weaker_layer(stage, attr: Usd.Attribute):
    """Internal. Copy timesamples of the attribute from weak layer to the current edit target."""

    layer_info, layer = get_attribute_effective_timesample_layer_info(stage, attr)
    if layer_info == Value_On_Layer.ON_WEAKER_LAYER:
        time_samples = attr.GetMetadata("timeSamples")
        for key, value in time_samples.items():
            attr.Set(value, key)


def get_timesamples_count_in_authoring_layer(stage, attr_path: Sdf.Path):
    """Internal. Gets the count of timesamples of the attribute in the current edit target."""

    authoring_layer = stage.GetEditTarget().GetLayer()
    if authoring_layer == stage.GetSessionLayer():
        return 0
    attr_spec = authoring_layer.GetAttributeAtPath(attr_path) if authoring_layer else None
    new_key_count = len(attr_spec.GetInfo("timeSamples")) if attr_spec else 0
    return new_key_count
