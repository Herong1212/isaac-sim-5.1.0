from __future__ import annotations
import omni.converter.hoops._omni_converter_hoops
import typing
import pxr.Sdf

__all__ = [
    "Converter",
    "InstancingStyle",
    "MaterialType",
    "Parameters",
    "convert"
]


class Converter():
    """
            
    """
    def __init__(self, parameters: Parameters) -> None: ...
    @typing.overload
    def convert(self, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]: 
        """
        Convert CAD file to USD.

        Args:
            inputPath: Path of CAD file to read
            outputPath: Path of the USD file to write
            args: Additional arguments may be supplied to control behavior specific to converter and the layer's file format.
        Returns:
            A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.




        Convert CAD file to USD.

        Args:
            inputPath: Path of CAD file to read
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
    eInstanceableReference: omni.converter.hoops._omni_converter_hoops.InstancingStyle # value = <InstancingStyle.eInstanceableReference: 2>
    eNone: omni.converter.hoops._omni_converter_hoops.InstancingStyle # value = <InstancingStyle.eNone: 0>
    eReference: omni.converter.hoops._omni_converter_hoops.InstancingStyle # value = <InstancingStyle.eReference: 1>
    pass
class MaterialType():
    """
    Material Type

    Members:

      eNone : None

      ePreviewSurface : Preview Surface

      ePreviewSurface_OmniPBR : Preview Surface + OmniPBR
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
    eNone: omni.converter.hoops._omni_converter_hoops.MaterialType # value = <MaterialType.eNone: 0>
    ePreviewSurface: omni.converter.hoops._omni_converter_hoops.MaterialType # value = <MaterialType.ePreviewSurface: 1>
    ePreviewSurface_OmniPBR: omni.converter.hoops._omni_converter_hoops.MaterialType # value = <MaterialType.ePreviewSurface_OmniPBR: 2>
    pass
class Parameters():
    """
    HOOPS Converter Parameters Class.
    """
    def __init__(self) -> None: ...
    def parseArgs(self, args: typing.Dict[str, str] = {}) -> None: 
        """
        Parse SdfLayer::FileFormatArguments to populate this Parameters instance

        Args:
            pxr::SdfLayer::FileFormatArguments: FileFormatArguments which represent convert options.
        """
    def toArgs(self) -> typing.Dict[str, str]: 
        """
        Create file format arguments that could be used to recreate these conversion parameters.
        """
    @property
    def accurateSurfaceCurvatures(self) -> bool:
        """
        (bool): Consider surface curvature to control triangles elongation direction

        :type: bool
        """
    @accurateSurfaceCurvatures.setter
    def accurateSurfaceCurvatures(self, arg0: bool) -> None:
        """
        (bool): Consider surface curvature to control triangles elongation direction
        """
    @property
    def accurateTessellation(self) -> bool:
        """
        (bool): If false, tessellate for visualization. If true, tessellate for analysis.

        :type: bool
        """
    @accurateTessellation.setter
    def accurateTessellation(self, arg0: bool) -> None:
        """
        (bool): If false, tessellate for visualization. If true, tessellate for analysis.
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
        (bool): If false, ignore hidden or non-visible parts during conversion. If true, convert all parts and maintain visibility settings

        :type: bool
        """
    @convertHidden.setter
    def convertHidden(self, arg0: bool) -> None:
        """
        (bool): If false, ignore hidden or non-visible parts during conversion. If true, convert all parts and maintain visibility settings
        """
    @property
    def convertMetadata(self) -> bool:
        """
        (bool): If true then metadata, including PMI, are imported as USD Attributes. If false, then we skip and do not Import any metadata to USD. 

        :type: bool
        """
    @convertMetadata.setter
    def convertMetadata(self, arg0: bool) -> None:
        """
        (bool): If true then metadata, including PMI, are imported as USD Attributes. If false, then we skip and do not Import any metadata to USD. 
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
    def dedup(self) -> bool:
        """
        (bool): Deduplicate mesh vertices and normals (welds mesh)

        :type: bool
        """
    @dedup.setter
    def dedup(self, arg0: bool) -> None:
        """
        (bool): Deduplicate mesh vertices and normals (welds mesh)
        """
    @property
    def globalXforms(self) -> bool:
        """
        (bool): When instancing = false, this flag controls whether globalXforms are composited. If false local transforms are applied

        :type: bool
        """
    @globalXforms.setter
    def globalXforms(self, arg0: bool) -> None:
        """
        (bool): When instancing = false, this flag controls whether globalXforms are composited. If false local transforms are applied
        """
    @property
    def instancingStyle(self) -> InstancingStyle:
        """
                        Style of instancing to use in USD.
                    

        :type: InstancingStyle
        """
    @instancingStyle.setter
    def instancingStyle(self, arg0: InstancingStyle) -> None:
        """
        Style of instancing to use in USD.
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
    def reportProgress(self) -> bool:
        """
        (bool): If true then we report import/export progress

        :type: bool
        """
    @reportProgress.setter
    def reportProgress(self, arg0: bool) -> None:
        """
        (bool): If true then we report import/export progress
        """
    @property
    def reportProgressFreq(self) -> float:
        """
        (int): Progress reporting frequency in Hz.

        :type: float
        """
    @reportProgressFreq.setter
    def reportProgressFreq(self, arg0: float) -> None:
        """
        (int): Progress reporting frequency in Hz.
        """
    @property
    def tessLOD(self) -> int:
        """
        (int): Tessellation Level of Detail (LOD) presets: 0=kA3DTessLODExtraLow, 1=kA3DTessLODLow,2=kA3DTessLODMedium, 3=kA3DTessLODHigh, 4=kA3DTessLODExtraHigh

        :type: int
        """
    @tessLOD.setter
    def tessLOD(self, arg0: int) -> None:
        """
        (int): Tessellation Level of Detail (LOD) presets: 0=kA3DTessLODExtraLow, 1=kA3DTessLODLow,2=kA3DTessLODMedium, 3=kA3DTessLODHigh, 4=kA3DTessLODExtraHigh
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
    @property
    def useNormals(self) -> bool:
        """
        (bool): If true then we pass normals to USD. if false, then we do not.

        :type: bool
        """
    @useNormals.setter
    def useNormals(self, arg0: bool) -> None:
        """
        (bool): If true then we pass normals to USD. if false, then we do not.
        """
    pass
@typing.overload
def convert(parameters: Parameters, inputPath: str, outputLayer: pxr.Sdf.Layer) -> typing.Tuple[int, str]:
    """
    Convert CAD file to USD.

    Args:
        params: Conversion parameters to use
        inputPath: Path of CAD file to read
        outputLayer: USD layer to write to

    Returns:
        A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.



    Convert CAD file to USD.

    Args:
        params: Conversion parameters to use
        inputPath: Path of CAD file to read
        outputPath: Path of the USD file to write
        outputArgs: Additional arguments may be supplied to control behavior specific to converter and the layer's file format.

    Returns:
        A (bool, string) tuple with bool indicating if the conversion was successful and string indicating error message if any.
    """
@typing.overload
def convert(parameters: Parameters, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]:
    pass
