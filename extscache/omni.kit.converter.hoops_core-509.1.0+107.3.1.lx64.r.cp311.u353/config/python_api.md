# Public API for module omni.kit.converter.hoops_core:

## Classes

- class HoopsCoreConverter(ICadCoreExtBase)
  - FILTER_DATA: HOOPS_CORE_FILTER_DATA
  - OPTIONS_CLS: HoopsOptions
  - SERVICE_TITLE: str
  - def on_startup(self, ext_id: str)
  - def on_shutdown(self)
  - def create_converter_task(self, input_path: str, output_path: str, file_format_args: dict[str, str])

- class HoopsConverterHelper
  - CONVERTER_EXT_NAME: str
  - def __init__(self)
  - def destroy(self)
  - async def create_import_task(self, input_path: str, output_path: str, file_format_args: dict[str, str]) -> Tuple[str, ConverterStatus]

- class HoopsOptions(omni.converter.hoops.Parameters)
  - def __init__(self)
  - def parse(self, args: dict[str, str])
  - def toArgs(self) -> dict[str:str]

## Functions

- def get_instance() -> Optional[HoopsCoreConverter]
- def is_format_supported(input_file_path: str) -> bool

## Variables

- HOOPS_CORE_FILTER_DATA: List

# Public API for module omni.converter.hoops:

## Classes

- class Converter
  - def __init__(self, parameters: Parameters)
  - def convert(self, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]
  - def convert(self, inputPath: str, layer: pxr.Sdf.Layer) -> typing.Tuple[int, str]

- class InstancingStyle
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eInstanceableReference: omni.converter.hoops._omni_converter_hoops.InstancingStyle
  - eNone: omni.converter.hoops._omni_converter_hoops.InstancingStyle
  - eReference: omni.converter.hoops._omni_converter_hoops.InstancingStyle

- class MaterialType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eNone: omni.converter.hoops._omni_converter_hoops.MaterialType
  - ePreviewSurface: omni.converter.hoops._omni_converter_hoops.MaterialType
  - ePreviewSurface_OmniPBR: omni.converter.hoops._omni_converter_hoops.MaterialType

- class Parameters
  - def __init__(self)
  - def parseArgs(self, args: typing.Dict[str, str] = {})
  - def toArgs(self) -> typing.Dict[str, str]
  - [property] def accurateSurfaceCurvatures(self) -> bool
  - [accurateSurfaceCurvatures.setter] def accurateSurfaceCurvatures(self, arg0: bool)
  - [property] def accurateTessellation(self) -> bool
  - [accurateTessellation.setter] def accurateTessellation(self, arg0: bool)
  - [property] def convertCurves(self) -> bool
  - [convertCurves.setter] def convertCurves(self, arg0: bool)
  - [property] def convertHidden(self) -> bool
  - [convertHidden.setter] def convertHidden(self, arg0: bool)
  - [property] def convertMetadata(self) -> bool
  - [convertMetadata.setter] def convertMetadata(self, arg0: bool)
  - [property] def creator(self) -> str
  - [creator.setter] def creator(self, arg0: str)
  - [property] def dedup(self) -> bool
  - [dedup.setter] def dedup(self, arg0: bool)
  - [property] def globalXforms(self) -> bool
  - [globalXforms.setter] def globalXforms(self, arg0: bool)
  - [property] def instancingStyle(self) -> InstancingStyle
  - [instancingStyle.setter] def instancingStyle(self, arg0: InstancingStyle)
  - [property] def materialType(self) -> MaterialType
  - [materialType.setter] def materialType(self, arg0: MaterialType)
  - [property] def reportProgress(self) -> bool
  - [reportProgress.setter] def reportProgress(self, arg0: bool)
  - [property] def reportProgressFreq(self) -> float
  - [reportProgressFreq.setter] def reportProgressFreq(self, arg0: float)
  - [property] def tessLOD(self) -> int
  - [tessLOD.setter] def tessLOD(self, arg0: int)
  - [property] def useMaterials(self) -> bool
  - [useMaterials.setter] def useMaterials(self, arg0: bool)
  - [property] def useNormals(self) -> bool
  - [useNormals.setter] def useNormals(self, arg0: bool)

## Functions

- def convert(parameters: Parameters, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]

# Public API for module omni.converter.hoops.tokens:

## Variables

- aggregates: str
- assignsToGroup: str
- connectsPathElements: str
- containedInSpatialStructure: str
- fillsElement: str
- spaceBoundary: str
- voidsElement: str
