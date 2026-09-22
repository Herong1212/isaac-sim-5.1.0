"""
        This module contains python bindings to the C++ omni::usd IMetricsAssembler interface.
    """
from __future__ import annotations
import omni.metrics.assembler.core.bindings._metricsAssembler
import typing

__all__ = [
    "MetricsAssembler",
    "SETTINGS_METRICS_ASSEMBLER_CONFORM_TO_XFORM_COMMON_API",
    "SETTINGS_METRICS_ASSEMBLER_OPERATION_MODE",
    "SETTINGS_METRICS_ASSEMBLER_PARAMS_CHANGE_LISTENER_ENABLED",
    "SETTINGS_METRICS_ASSEMBLER_SHOW_UNITS_OVERLAY",
    "UnitsInfo",
    "acquire_metrics_assembler_interface",
    "release_metrics_assembler_interface",
    "release_metrics_assembler_interface_scripting"
]


class MetricsAssembler():
    def change_stage_units(self, arg0: int, arg1: UnitsInfo) -> bool: 
        """
        Change stage units

        note This operation is destructive and will happen with the current active target layer
             Additionally the xformOpCommonAPI is used for the xformOp stack transformation.

        stageId USD stage id.
        newUnits New desired units for the stage
        return True if operation was succesfull.
        """
    def check_layers(self, layer0Identifier: str, layer1Identifier: str, stage_id: int) -> dict: 
        """
        Check units divergency on given two layers. The inputs are layer indentifiers.

        Returns:
            Return a dictionary with info::

                'ret_val': bool - whether layers are divergent
                'units_info0': UnitsInfo - layer0 units
                'units_info1': UnitsInfo - layer1 units
        """
    def check_stage(self, arg0: int) -> bool: 
        """
        Check units divergency on given stage.
        """
    def register_custom_callback(self, resolve_start_fn: typing.Callable[[int], None], resolve_end_fn: typing.Callable[[int], None], resolve_prim_fn: typing.Callable[[str, UnitsInfo, UnitsInfo], bool], resolve_attribute_fn: typing.Callable[[str, str, UnitsInfo, UnitsInfo, int, int], tuple], attribute_tokens: typing.List[str] = []) -> int: 
        """
        Register custom callback.

        Resolve_start_fn: long stageId

        Resolve_end_fn: long stageId

        Resolve_prim_fn: const char* usdPrimPath, const UnitsInfo& stageUnits, const UnitsInfo& resolveUnits,
                int& metersExponent, int& kilogramsExponent

        Resolve_attribute_fn: const char* usdPrimPath, const char* attributeName, const UnitsInfo& stageUnits, const UnitsInfo& resolveUnits,
                int& metersExponent, int& kilogramsExponent

        Attribute_tokens: list of attribute tokens that will filter the resolve_attribute_fn, only attributes with these token names will
                fire the callback. If None all attributes will be send to the custom resolve function, note that this will have performance impact
        """
    def register_custom_resolve_rule(self, attribute_name: str, meters_exponent: int, kilograms_exponent: int) -> int: 
        """
        Register custom resolve rule.

        The applied rule works like this:
        resolvedValue = value * (MPU/stageMPU)^metersExponent * (KGPU/stageKGPU)^kilogramsExponent
        """
    def resolve_hierarchy(self, stage_id: int, prim_path: str) -> bool: 
        """
        Resolve given stage hierarchy from given path.
        """
    def resolve_stage(self, arg0: int) -> bool: 
        """
        Resolve given stage.
        """
    def set_resolve_layer(self, arg0: str) -> None: 
        """
        Set resolve layer.
        """
    def unregister_custom_callback(self, registry_id: int) -> None: 
        """
        Unregister custom callback.
        """
    def unregister_custom_resolve_rule(self, arg0: int) -> None: 
        """
        Unregister custom resolve rule.
        """
    pass
class UnitsInfo():
    """
    Units info.
    """
    def __init__(self) -> None: ...
    def __str__(self) -> str: ...
    @property
    def kilograms_per_unit(self) -> float:
        """
        Kilograms Per Unit.

        :type: float
        """
    @kilograms_per_unit.setter
    def kilograms_per_unit(self, arg0: float) -> None:
        """
        Kilograms Per Unit.
        """
    @property
    def meters_per_unit(self) -> float:
        """
        Meters Per Unit.

        :type: float
        """
    @meters_per_unit.setter
    def meters_per_unit(self, arg0: float) -> None:
        """
        Meters Per Unit.
        """
    @property
    def up_axis(self) -> str:
        """
        Up axis.

        :type: str
        """
    @up_axis.setter
    def up_axis(self, arg1: str) -> None:
        """
        Up axis.
        """
    pass
def acquire_metrics_assembler_interface(plugin_name: str = None, library_path: str = None) -> MetricsAssembler:
    pass
def release_metrics_assembler_interface(arg0: MetricsAssembler) -> None:
    pass
def release_metrics_assembler_interface_scripting(arg0: MetricsAssembler) -> None:
    pass
SETTINGS_METRICS_ASSEMBLER_CONFORM_TO_XFORM_COMMON_API = '/metricsAssembler/conformToXformCommonAPI'
SETTINGS_METRICS_ASSEMBLER_OPERATION_MODE = '/metricsAssembler/operationMode'
SETTINGS_METRICS_ASSEMBLER_PARAMS_CHANGE_LISTENER_ENABLED = '/metricsAssembler/changeListenerEnabled'
SETTINGS_METRICS_ASSEMBLER_SHOW_UNITS_OVERLAY = '/metricsAssembler/showUnitsOverlay'
