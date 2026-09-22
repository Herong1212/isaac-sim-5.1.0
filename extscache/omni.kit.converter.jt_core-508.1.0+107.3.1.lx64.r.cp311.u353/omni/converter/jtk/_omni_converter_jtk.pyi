from __future__ import annotations
import omni.converter.jtk._omni_converter_jtk
import typing
import pxr.Sdf

__all__ = [
    "Converter",
    "InstancingStyle",
    "LayerFilterStyle",
    "MaterialType",
    "Parameters",
    "convert",
    "shutdown"
]


class Converter():
    """
    Manager class to configure and perform conversions
    """
    def __init__(self, params: Parameters) -> None: ...
    @typing.overload
    def convert(self, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]: 
        """
        Convert the contents of a JT file to USD

        Args:
            inputPath: Path of JT file to read
            outputPath: Path of the USD file to write
            outputArgs: Additional arguments may be supplied to control behavior specific to converter and the layer's file format.

        Returns:
            A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.




        Convert the contents of a JT file to USD

        Args:
            inputPath: Path of JT file to read
            outputLayer: USD layer to write to

        Returns:
            A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.
        """
    @typing.overload
    def convert(self, inputPath: str, layer: pxr.Sdf.Layer) -> typing.Tuple[int, str]: ...
    pass
class InstancingStyle():
    """
    Instancing Style

    Members:

      eNone : No Instancing

      eReference : Reference

      eInstanceableReference : Instanceable Reference
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eNone': <InstancingStyle.eNone: 0>, 'eReference': <InstancingStyle.eReference: 1>, 'eInstanceableReference': <InstancingStyle.eInstanceableReference: 2>}
    eInstanceableReference: omni.converter.jtk._omni_converter_jtk.InstancingStyle # value = <InstancingStyle.eInstanceableReference: 2>
    eNone: omni.converter.jtk._omni_converter_jtk.InstancingStyle # value = <InstancingStyle.eNone: 0>
    eReference: omni.converter.jtk._omni_converter_jtk.InstancingStyle # value = <InstancingStyle.eReference: 1>
    pass
class LayerFilterStyle():
    """
    Layer Filter Style

    Members:

      eNone : No filtering

      eOmit : Omit filtered entities

      eDeactivate : Deactivate filtered entities

      eHide : Hide filtered entities
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eNone': <LayerFilterStyle.eNone: 0>, 'eOmit': <LayerFilterStyle.eOmit: 1>, 'eDeactivate': <LayerFilterStyle.eDeactivate: 2>, 'eHide': <LayerFilterStyle.eHide: 3>}
    eDeactivate: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle # value = <LayerFilterStyle.eDeactivate: 2>
    eHide: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle # value = <LayerFilterStyle.eHide: 3>
    eNone: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle # value = <LayerFilterStyle.eNone: 0>
    eOmit: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle # value = <LayerFilterStyle.eOmit: 1>
    pass
class MaterialType():
    """
    Material Type

    Members:

      eNone : None

      ePreviewSurface : Preview Surface

      ePreviewSurface_OmniPBR : OmniPBR + Preview Surface
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eNone': <MaterialType.eNone: 0>, 'ePreviewSurface': <MaterialType.ePreviewSurface: 1>, 'ePreviewSurface_OmniPBR': <MaterialType.ePreviewSurface_OmniPBR: 2>}
    eNone: omni.converter.jtk._omni_converter_jtk.MaterialType # value = <MaterialType.eNone: 0>
    ePreviewSurface: omni.converter.jtk._omni_converter_jtk.MaterialType # value = <MaterialType.ePreviewSurface: 1>
    ePreviewSurface_OmniPBR: omni.converter.jtk._omni_converter_jtk.MaterialType # value = <MaterialType.ePreviewSurface_OmniPBR: 2>
    pass
class Parameters():
    """
    Container class for parameters to control conversion
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, args: typing.Dict[str, str]) -> None: ...
    def toArgs(self) -> typing.Dict[str, str]: 
        """
        Create file format arguments that could be used to recreate these conversion parameters.
        """
    @property
    def convertCurves(self) -> bool:
        """
        :type: bool
        """
    @convertCurves.setter
    def convertCurves(self, arg0: bool) -> None:
        pass
    @property
    def creator(self) -> str:
        """
                        Creator version string in major.minor.patch format.
                    

        :type: str
        """
    @creator.setter
    def creator(self, arg0: str) -> None:
        """
        Creator version string in major.minor.patch format.
        """
    @property
    def fallbackTessParamAngular(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamAngular.setter
    def fallbackTessParamAngular(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamChordal(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamChordal.setter
    def fallbackTessParamChordal(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamHoleRemovalFraction(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamHoleRemovalFraction.setter
    def fallbackTessParamHoleRemovalFraction(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamLength(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamLength.setter
    def fallbackTessParamLength(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamMaxAspect(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamMaxAspect.setter
    def fallbackTessParamMaxAspect(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamMinAngle(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamMinAngle.setter
    def fallbackTessParamMinAngle(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamMinEdgeLength(self) -> float:
        """
        :type: float
        """
    @fallbackTessParamMinEdgeLength.setter
    def fallbackTessParamMinEdgeLength(self, arg0: float) -> None:
        pass
    @property
    def fallbackTessParamTrimSuppress(self) -> bool:
        """
        :type: bool
        """
    @fallbackTessParamTrimSuppress.setter
    def fallbackTessParamTrimSuppress(self, arg0: bool) -> None:
        pass
    @property
    def flatten(self) -> bool:
        """
        :type: bool
        """
    @flatten.setter
    def flatten(self, arg0: bool) -> None:
        pass
    @property
    def instancingStyle(self) -> InstancingStyle:
        """
                        Style of instancing to use in USD when handling instanced Parts and Assemblies in the JT file.
                    

        :type: InstancingStyle
        """
    @instancingStyle.setter
    def instancingStyle(self, arg0: InstancingStyle) -> None:
        """
        Style of instancing to use in USD when handling instanced Parts and Assemblies in the JT file.
        """
    @property
    def layerFilterStyle(self) -> LayerFilterStyle:
        """
                        Style of filtering to use for entities that do not match the layer filters.
                    

        :type: LayerFilterStyle
        """
    @layerFilterStyle.setter
    def layerFilterStyle(self, arg0: LayerFilterStyle) -> None:
        """
        Style of filtering to use for entities that do not match the layer filters.
        """
    @property
    def materialType(self) -> MaterialType:
        """
                        Type of material to use for various renderer contexts.
                    

        :type: MaterialType
        """
    @materialType.setter
    def materialType(self, arg0: MaterialType) -> None:
        """
        Type of material to use for various renderer contexts.
        """
    @property
    def overrideTessellationGeometry(self) -> bool:
        """
                        If true, embedded tessellation geometry will be ignored in favour for explicit tessellation of surface geometry.
                    

        :type: bool
        """
    @overrideTessellationGeometry.setter
    def overrideTessellationGeometry(self, arg0: bool) -> None:
        """
        If true, embedded tessellation geometry will be ignored in favour for explicit tessellation of surface geometry.
        """
    @property
    def overrideTessellationParameters(self) -> bool:
        """
                        If true, embedded tessellation parameters will be ignored in favour for explicit tessellation parameters.
                    

        :type: bool
        """
    @overrideTessellationParameters.setter
    def overrideTessellationParameters(self, arg0: bool) -> None:
        """
        If true, embedded tessellation parameters will be ignored in favour for explicit tessellation parameters.
        """
    @property
    def progressLogging(self) -> bool:
        """
                        If true, conversion progress will be reported.
                    

        :type: bool
        """
    @progressLogging.setter
    def progressLogging(self, arg0: bool) -> None:
        """
        If true, conversion progress will be reported.
        """
    pass
@typing.overload
def convert(params: Parameters, inputPath: str, outputLayer: pxr.Sdf.Layer) -> typing.Tuple[int, str]:
    """
    Convert the contents of a JT file to USD

    Args:
        params: Conversion parameters to use
        inputPath: Path of JT file to read
        outputLayer: USD layer to write to

    Returns:
        A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.




    Convert the contents of a JT file to USD

    Args:
        params: Conversion parameters to use
        inputPath: Path of JT file to read
        outputPath: Path of the USD file to write
        outputArgs: Additional arguments may be supplied to control behavior specific to converter and the layer's file format.

    Returns:
        A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.
    """
@typing.overload
def convert(params: Parameters, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]:
    pass
def shutdown() -> None:
    """
    Shutdown the JT Open Toolkit

    Only call this once, when the entire program is terminating.
    Once shutdown the connection to JT Open Toolkit cannot be restarted in the same process.
    """
