from __future__ import annotations
import omni.converter.dgn._omni_converter_dgn
import typing
import pxr.Sdf

__all__ = [
    "Converter",
    "FilterStyle",
    "InstancingStyle",
    "MaterialType",
    "MergedAttributeStyle",
    "Parameters",
    "convert"
]


class Converter():
    """
            
    """
    def __init__(self, parameters: Parameters) -> None: ...
    @typing.overload
    def convert(self, inputPath: str, outputPath: str, outputArgs: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]: 
        """
        Convert to USD.

        Args:
            inputPath: Path of .dgn file to read
            outputPath: Output file path
            outputArgs: File format arguments to pass to the output layer

        Returns:
            Tuple where first value represents conversion success bool flag and second value represents error message.



        Convert to USD.

        Args:
            inputPath: Path of .dgn file to read
            outputLayer: Output layer

        Returns:
            Tuple where first value represents conversion success bool flag and second value represents error message.
        """
    @typing.overload
    def convert(self, inputPath: str, outputLayer: pxr.Sdf.Layer) -> typing.Tuple[int, str]: ...
    pass
class FilterStyle():
    """
    Styles that can be used to handle filtered elements

    Members:

      eNone : Apply no filtering

      eOmit : Do not convert the filtered element or its descendants

      eDeactivate : Convert all elements and deactivate the ones that were filtered

      eHide : Convert all elements and hide the ones that were filtered
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
    __members__: dict # value = {'eNone': <FilterStyle.eNone: 0>, 'eOmit': <FilterStyle.eOmit: 1>, 'eDeactivate': <FilterStyle.eDeactivate: 2>, 'eHide': <FilterStyle.eHide: 3>}
    eDeactivate: omni.converter.dgn._omni_converter_dgn.FilterStyle # value = <FilterStyle.eDeactivate: 2>
    eHide: omni.converter.dgn._omni_converter_dgn.FilterStyle # value = <FilterStyle.eHide: 3>
    eNone: omni.converter.dgn._omni_converter_dgn.FilterStyle # value = <FilterStyle.eNone: 0>
    eOmit: omni.converter.dgn._omni_converter_dgn.FilterStyle # value = <FilterStyle.eOmit: 1>
    pass
class InstancingStyle():
    """
    Instancing Style

    Members:

      eNone : No Instancing

      eScenegraphInstancing : Scene Graph Instancing
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
    __members__: dict # value = {'eNone': <InstancingStyle.eNone: 0>, 'eScenegraphInstancing': <InstancingStyle.eScenegraphInstancing: 1>}
    eNone: omni.converter.dgn._omni_converter_dgn.InstancingStyle # value = <InstancingStyle.eNone: 0>
    eScenegraphInstancing: omni.converter.dgn._omni_converter_dgn.InstancingStyle # value = <InstancingStyle.eScenegraphInstancing: 1>
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
    eNone: omni.converter.dgn._omni_converter_dgn.MaterialType # value = <MaterialType.eNone: 0>
    ePreviewSurface: omni.converter.dgn._omni_converter_dgn.MaterialType # value = <MaterialType.ePreviewSurface: 1>
    ePreviewSurface_OmniPBR: omni.converter.dgn._omni_converter_dgn.MaterialType # value = <MaterialType.ePreviewSurface_OmniPBR: 2>
    pass
class MergedAttributeStyle():
    """
    Merged Attribute Style

    Members:

      eNone : Discard Attributes

      ePrimvar : Store as a Primvar

      eSubset : Store on a metadata Subset
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
    __members__: dict # value = {'eNone': <MergedAttributeStyle.eNone: 0>, 'ePrimvar': <MergedAttributeStyle.ePrimvar: 1>, 'eSubset': <MergedAttributeStyle.eSubset: 2>}
    eNone: omni.converter.dgn._omni_converter_dgn.MergedAttributeStyle # value = <MergedAttributeStyle.eNone: 0>
    ePrimvar: omni.converter.dgn._omni_converter_dgn.MergedAttributeStyle # value = <MergedAttributeStyle.ePrimvar: 1>
    eSubset: omni.converter.dgn._omni_converter_dgn.MergedAttributeStyle # value = <MergedAttributeStyle.eSubset: 2>
    pass
class Parameters():
    """
    DGN Converter Options Class.
    """
    def __init__(self) -> None: ...
    def parseArgs(self, args: typing.Dict[str, str] = {}) -> bool: 
        """
        Parse SdfLayer::FileFormatArguments to populate the Parameters

        Args:
            str: JSON formatted string
        """
    def toArgs(self) -> typing.Dict[str, str]: 
        """
        Create file format arguments that could be used to recreate these conversion parameters.
        """
    @property
    def applyGlobalOrigin(self) -> bool:
        """
        (bool): Whether the global origin of Models are applied as an XformOp

        :type: bool
        """
    @applyGlobalOrigin.setter
    def applyGlobalOrigin(self, arg0: bool) -> None:
        """
        (bool): Whether the global origin of Models are applied as an XformOp
        """
    @property
    def attributes(self) -> typing.List[typing.List[str]]:
        """
        (dict): Attributes to import where key = attribute name and value=custom attribute name to use in USD

        :type: typing.List[typing.List[str]]
        """
    @attributes.setter
    def attributes(self, arg0: typing.List[typing.List[str]]) -> None:
        """
        (dict): Attributes to import where key = attribute name and value=custom attribute name to use in USD
        """
    @property
    def convertCurves(self) -> bool:
        """
        (bool): If true then curve objects are imported as USD BasisCurves. If false, then we skip and do not Import any curve object to USD. 

        :type: bool
        """
    @convertCurves.setter
    def convertCurves(self, arg0: bool) -> None:
        """
        (bool): If true then curve objects are imported as USD BasisCurves. If false, then we skip and do not Import any curve object to USD. 
        """
    @property
    def convertHidden(self) -> bool:
        """
        (bool): If true then hidden data is imported, it will be hidden in the USD Stage until activated/unhidden. If false, then we skip and do not Import the hidden data to USD. 

        :type: bool
        """
    @convertHidden.setter
    def convertHidden(self, arg0: bool) -> None:
        """
        (bool): If true then hidden data is imported, it will be hidden in the USD Stage until activated/unhidden. If false, then we skip and do not Import the hidden data to USD. 
        """
    @property
    def creator(self) -> str:
        """
        (str): Creator version string

        :type: str
        """
    @creator.setter
    def creator(self, arg0: str) -> None:
        """
        (str): Creator version string
        """
    @property
    def fallbackCurveWidth(self) -> float:
        """
        (float): sets a fallback width for curve segments that do not have an explicit width set. If the fallback width is not set or <= 0 or omitted, no widths primvar is authored and the renderer’s default is used.

        :type: float
        """
    @fallbackCurveWidth.setter
    def fallbackCurveWidth(self, arg0: float) -> None:
        """
        (float): sets a fallback width for curve segments that do not have an explicit width set. If the fallback width is not set or <= 0 or omitted, no widths primvar is authored and the renderer’s default is used.
        """
    @property
    def hiddenLevels(self) -> typing.List[str]:
        """
        (str[]): List of level names to hide

        :type: typing.List[str]
        """
    @hiddenLevels.setter
    def hiddenLevels(self, arg0: typing.List[str]) -> None:
        """
        (str[]): List of level names to hide
        """
    @property
    def hideLevelsByList(self) -> bool:
        """
        (bool): Whether to hide defined levels based on the listed level names

        :type: bool
        """
    @hideLevelsByList.setter
    def hideLevelsByList(self, arg0: bool) -> None:
        """
        (bool): Whether to hide defined levels based on the listed level names
        """
    @property
    def importAttributesByList(self) -> bool:
        """
        (bool): Whether to import defined attributes 

        :type: bool
        """
    @importAttributesByList.setter
    def importAttributesByList(self, arg0: bool) -> None:
        """
        (bool): Whether to import defined attributes 
        """
    @property
    def instancing(self) -> bool:
        """
        (bool): If true, enable instancing

        :type: bool
        """
    @instancing.setter
    def instancing(self, arg0: bool) -> None:
        """
        (bool): If true, enable instancing
        """
    @property
    def instancingStyle(self) -> InstancingStyle:
        """
        (enum): Style of instancing to use in USD when handling Shared Cell References

        :type: InstancingStyle
        """
    @instancingStyle.setter
    def instancingStyle(self, arg0: InstancingStyle) -> None:
        """
        (enum): Style of instancing to use in USD when handling Shared Cell References
        """
    @property
    def levelExcludes(self) -> typing.List[str]:
        """
        List of level names to exclude during filtering

        :type: typing.List[str]
        """
    @levelExcludes.setter
    def levelExcludes(self, arg0: typing.List[str]) -> None:
        """
        List of level names to exclude during filtering
        """
    @property
    def levelFilterStyle(self) -> FilterStyle:
        """
        Styles to used to handle filtered levels

        :type: FilterStyle
        """
    @levelFilterStyle.setter
    def levelFilterStyle(self, arg0: FilterStyle) -> None:
        """
        Styles to used to handle filtered levels
        """
    @property
    def levelIncludes(self) -> typing.List[str]:
        """
        List of level names to include during filtering

        :type: typing.List[str]
        """
    @levelIncludes.setter
    def levelIncludes(self, arg0: typing.List[str]) -> None:
        """
        List of level names to include during filtering
        """
    @property
    def materialType(self) -> MaterialType:
        """
        (enum): Material type: ePreviewSurface (compatible with USD-enabled DCCs), ePreviewSurface_OmniPBR (optimized for RTX rendering and USD DCCs).

        :type: MaterialType
        """
    @materialType.setter
    def materialType(self, arg0: MaterialType) -> None:
        """
        (enum): Material type: ePreviewSurface (compatible with USD-enabled DCCs), ePreviewSurface_OmniPBR (optimized for RTX rendering and USD DCCs).
        """
    @property
    def mergeCurves(self) -> bool:
        """
        (bool): If true then curve segments are merged if they have the same 'width'. If false then curve merging is skipped

        :type: bool
        """
    @mergeCurves.setter
    def mergeCurves(self, arg0: bool) -> None:
        """
        (bool): If true then curve segments are merged if they have the same 'width'. If false then curve merging is skipped
        """
    @property
    def mergeMeshes(self) -> bool:
        """
        (bool): If true then meshes that share the same level and color are merged for optimization. If false then mesh merging is skipped

        :type: bool
        """
    @mergeMeshes.setter
    def mergeMeshes(self, arg0: bool) -> None:
        """
        (bool): If true then meshes that share the same level and color are merged for optimization. If false then mesh merging is skipped
        """
    @property
    def mergedAttributeStyle(self) -> MergedAttributeStyle:
        """
        (enum): The style in which the values of attributes that differ between merged elements are stored

        :type: MergedAttributeStyle
        """
    @mergedAttributeStyle.setter
    def mergedAttributeStyle(self, arg0: MergedAttributeStyle) -> None:
        """
        (enum): The style in which the values of attributes that differ between merged elements are stored
        """
    @property
    def modelNamePatterns(self) -> typing.List[str]:
        """
        (str[]): List of model names patterns for resolving DGN models to convert; model names can include wildcard characters ("*") to complete the rest of the model name during conversion wildcard characters can be placed at the beginning ("*ault"), ending ("Def*"), or both ("*fau*"); if the user provides patterns that do not match any models in the DGN file, then the file is not converted

        :type: typing.List[str]
        """
    @modelNamePatterns.setter
    def modelNamePatterns(self, arg0: typing.List[str]) -> None:
        """
        (str[]): List of model names patterns for resolving DGN models to convert; model names can include wildcard characters ("*") to complete the rest of the model name during conversion wildcard characters can be placed at the beginning ("*ault"), ending ("Def*"), or both ("*fau*"); if the user provides patterns that do not match any models in the DGN file, then the file is not converted
        """
    @property
    def progressLogging(self) -> bool:
        """
        (bool): If true then conversion progress will be reported

        :type: bool
        """
    @progressLogging.setter
    def progressLogging(self, arg0: bool) -> None:
        """
        (bool): If true then conversion progress will be reported
        """
    @property
    def surfaceTolerance(self) -> float:
        """
        (double): the maximum distance between the tessellated mesh and actual surface; the more precise the value (e.g., 0.1) the more refined the resulting mesh; acceptable value range = [0.1, 1.0]; this overrides the value determined by tessLOD

        :type: float
        """
    @surfaceTolerance.setter
    def surfaceTolerance(self, arg0: float) -> None:
        """
        (double): the maximum distance between the tessellated mesh and actual surface; the more precise the value (e.g., 0.1) the more refined the resulting mesh; acceptable value range = [0.1, 1.0]; this overrides the value determined by tessLOD
        """
    @property
    def tessLOD(self) -> int:
        """
        (int): Tessellation Level of Detail (LOD) presets: 0 for 1.0 surface tolerance,  1 for 0.1 surface tolerance, 2 for 0.01 surface tolerance, 3 for 0.001 surface tolerance, 4 for 0.0001 surface tolerance

        :type: int
        """
    @tessLOD.setter
    def tessLOD(self, arg0: int) -> None:
        """
        (int): Tessellation Level of Detail (LOD) presets: 0 for 1.0 surface tolerance,  1 for 0.1 surface tolerance, 2 for 0.01 surface tolerance, 3 for 0.001 surface tolerance, 4 for 0.0001 surface tolerance
        """
    @property
    def triangulate(self) -> bool:
        """
        (bool): Whether to triangulate Meshes

        :type: bool
        """
    @triangulate.setter
    def triangulate(self, arg0: bool) -> None:
        """
        (bool): Whether to triangulate Meshes
        """
    @property
    def useMaterials(self) -> bool:
        """
        (bool): If true then use specified modes of materials. if false, then use only basic display colors

        :type: bool
        """
    @useMaterials.setter
    def useMaterials(self, arg0: bool) -> None:
        """
        (bool): If true then use specified modes of materials. if false, then use only basic display colors
        """
    pass
@typing.overload
def convert(parameters: Parameters, inputPath: str, outputLayer: pxr.Sdf.Layer) -> typing.Tuple[int, str]:
    """
    Convert .dgn to USD.

    Args:
        parameters: Conversion parameters
        inputPath: Path of .dgn file to read
        outputLayer: SdfLayerHandle to write to

    Returns:
        Tuple where first value represents conversion success bool flag and second value represents error message.



    Convert .dgn to USD.

    Args:
        parameters: Conversion parameters
        inputPath: Path of .dgn file to read
        outputPath: Path of the USD file to write
        outputArgs: File format arguments to pass to the output layer

    Returns:
        Tuple where first value represents conversion success bool flag and second value represents error message.
    """
@typing.overload
def convert(*args, **kwargs) -> typing.Any:
    pass
