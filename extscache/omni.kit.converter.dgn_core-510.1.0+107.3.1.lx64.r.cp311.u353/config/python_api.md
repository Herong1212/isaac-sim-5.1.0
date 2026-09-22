# Public API for module omni.kit.converter.dgn_core:

## Classes

- class DgnConverter(ICadCoreExtBase)
  - FILTER_DATA: DGN_CORE_FILTER_DATA
  - OPTIONS_CLS: OdaDgnOptions
  - SERVICE_TITLE: str
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def create_converter_task(self, input_path: str, output_path: str, file_format_args: dict[str, str])

- class DgnConverterCoreHelper
  - CONVERTER_EXT_NAME: str
  - def __init__(self)
  - def destroy(self)

- class OdaDgnOptions(omni.converter.dgn.Parameters)
  - def __init__(self)
  - def parse(self, args: dict[str, str])
  - def toArgs(self) -> dict[str:str]

## Functions

- def get_instance() -> Optional[DgnConverter]

## Variables

- DGN_CONVERTER_SUPPORTED_FORMATS: List
- DGN_CORE_FILTER_DATA: List

# Public API for module omni.converter.dgn:

## Classes

- class Converter
  - def __init__(self, parameters: Parameters)
  - def convert(self, inputPath: str, outputPath: str, outputArgs: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]
  - def convert(self, inputPath: str, outputLayer: pxr.Sdf.Layer) -> typing.Tuple[int, str]

- class FilterStyle
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eDeactivate: omni.converter.dgn._omni_converter_dgn.FilterStyle
  - eHide: omni.converter.dgn._omni_converter_dgn.FilterStyle
  - eNone: omni.converter.dgn._omni_converter_dgn.FilterStyle
  - eOmit: omni.converter.dgn._omni_converter_dgn.FilterStyle

- class InstancingStyle
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eNone: omni.converter.dgn._omni_converter_dgn.InstancingStyle
  - eScenegraphInstancing: omni.converter.dgn._omni_converter_dgn.InstancingStyle

- class MaterialType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eNone: omni.converter.dgn._omni_converter_dgn.MaterialType
  - ePreviewSurface: omni.converter.dgn._omni_converter_dgn.MaterialType
  - ePreviewSurface_OmniPBR: omni.converter.dgn._omni_converter_dgn.MaterialType

- class MergedAttributeStyle
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eNone: omni.converter.dgn._omni_converter_dgn.MergedAttributeStyle
  - ePrimvar: omni.converter.dgn._omni_converter_dgn.MergedAttributeStyle
  - eSubset: omni.converter.dgn._omni_converter_dgn.MergedAttributeStyle

- class Parameters
  - def __init__(self)
  - def parseArgs(self, args: typing.Dict[str, str] = {}) -> bool
  - def toArgs(self) -> typing.Dict[str, str]
  - [property] def applyGlobalOrigin(self) -> bool
  - [applyGlobalOrigin.setter] def applyGlobalOrigin(self, arg0: bool)
  - [property] def attributes(self) -> typing.List[typing.List[str]]
  - [attributes.setter] def attributes(self, arg0: typing.List[typing.List[str]])
  - [property] def convertCurves(self) -> bool
  - [convertCurves.setter] def convertCurves(self, arg0: bool)
  - [property] def convertHidden(self) -> bool
  - [convertHidden.setter] def convertHidden(self, arg0: bool)
  - [property] def creator(self) -> str
  - [creator.setter] def creator(self, arg0: str)
  - [property] def fallbackCurveWidth(self) -> float
  - [fallbackCurveWidth.setter] def fallbackCurveWidth(self, arg0: float)
  - [property] def hiddenLevels(self) -> typing.List[str]
  - [hiddenLevels.setter] def hiddenLevels(self, arg0: typing.List[str])
  - [property] def hideLevelsByList(self) -> bool
  - [hideLevelsByList.setter] def hideLevelsByList(self, arg0: bool)
  - [property] def importAttributesByList(self) -> bool
  - [importAttributesByList.setter] def importAttributesByList(self, arg0: bool)
  - [property] def instancing(self) -> bool
  - [instancing.setter] def instancing(self, arg0: bool)
  - [property] def instancingStyle(self) -> InstancingStyle
  - [instancingStyle.setter] def instancingStyle(self, arg0: InstancingStyle)
  - [property] def levelExcludes(self) -> typing.List[str]
  - [levelExcludes.setter] def levelExcludes(self, arg0: typing.List[str])
  - [property] def levelFilterStyle(self) -> FilterStyle
  - [levelFilterStyle.setter] def levelFilterStyle(self, arg0: FilterStyle)
  - [property] def levelIncludes(self) -> typing.List[str]
  - [levelIncludes.setter] def levelIncludes(self, arg0: typing.List[str])
  - [property] def materialType(self) -> MaterialType
  - [materialType.setter] def materialType(self, arg0: MaterialType)
  - [property] def mergeCurves(self) -> bool
  - [mergeCurves.setter] def mergeCurves(self, arg0: bool)
  - [property] def mergeMeshes(self) -> bool
  - [mergeMeshes.setter] def mergeMeshes(self, arg0: bool)
  - [property] def mergedAttributeStyle(self) -> MergedAttributeStyle
  - [mergedAttributeStyle.setter] def mergedAttributeStyle(self, arg0: MergedAttributeStyle)
  - [property] def modelNamePatterns(self) -> typing.List[str]
  - [modelNamePatterns.setter] def modelNamePatterns(self, arg0: typing.List[str])
  - [property] def progressLogging(self) -> bool
  - [progressLogging.setter] def progressLogging(self, arg0: bool)
  - [property] def surfaceTolerance(self) -> float
  - [surfaceTolerance.setter] def surfaceTolerance(self, arg0: float)
  - [property] def tessLOD(self) -> int
  - [tessLOD.setter] def tessLOD(self, arg0: int)
  - [property] def triangulate(self) -> bool
  - [triangulate.setter] def triangulate(self, arg0: bool)
  - [property] def useMaterials(self) -> bool
  - [useMaterials.setter] def useMaterials(self, arg0: bool)

## Functions

- def convert(*args, **kwargs) -> typing.Any

# Public API for module omni.converter.dgn.tokens:

## Variables

- Arc: str
- BSplineCurve: str
- CellHeader: str
- ComplexShape: str
- Cone: str
- Ellipse: str
- ExtendedElement: str
- Line: str
- LineString: str
- Mesh: str
- Model: str
- Shape: str
- SharedCellDefinition: str
- SharedCellReference: str
- SmartSolid: str
- SmartSurface: str
- Solid: str
- Surface: str
- elementColor: str
- elementFillColor: str
- elementId: str
- elementIdPrimvar: str
- elementType: str
- levelName: str
- metadata: str
- modelGlobalOrigin: str
- name: str
