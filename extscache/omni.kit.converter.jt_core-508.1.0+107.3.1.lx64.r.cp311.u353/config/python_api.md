# Public API for module omni.kit.converter.jt_core:

## Classes

- class JtCoreConverterExt(ICadCoreExtBase)
  - FILTER_DATA: JT_CORE_FILTER_DATA
  - OPTIONS_CLS: JTConverterOptions
  - SERVICE_TITLE: str
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def create_converter_task(self, input_path: str, output_path: str, file_format_args: dict[str, str])

- class JtConverterHelper
  - CONVERTER_EXT_NAME: str
  - def __init__(self)
  - def destroy(self)
  - def get_node_type_counts(self)
  - async def create_import_task(self, input_path: str, output_path: str, file_format_args: dict[str, str]) -> Tuple[str, ConverterStatus]

- class JTConverterOptions(omni.converter.jtk.Parameters)
  - bInstancing: bool
  - bOptimize: bool
  - bConvertHidden: bool
  - materialSelection: Unknown
  - sOptimizeConfig: str
  - iUpAxis: int
  - dMetersPerUnit: float
  - def __init__(self)
  - def parse(self, args: dict[str, str])
  - def toArgs(self) -> dict[str, str]

## Functions

- def get_instance() -> Optional[JtCoreConverterExt]

## Variables

- JT_CORE_FILTER_DATA: List

# Public API for module omni.converter.jtk:

## Classes

- class Converter
  - def __init__(self, params: Parameters)
  - def convert(self, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]
  - def convert(self, inputPath: str, layer: pxr.Sdf.Layer) -> typing.Tuple[int, str]

- class InstancingStyle
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eInstanceableReference: omni.converter.jtk._omni_converter_jtk.InstancingStyle
  - eNone: omni.converter.jtk._omni_converter_jtk.InstancingStyle
  - eReference: omni.converter.jtk._omni_converter_jtk.InstancingStyle

- class LayerFilterStyle
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eDeactivate: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle
  - eHide: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle
  - eNone: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle
  - eOmit: omni.converter.jtk._omni_converter_jtk.LayerFilterStyle

- class MaterialType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - eNone: omni.converter.jtk._omni_converter_jtk.MaterialType
  - ePreviewSurface: omni.converter.jtk._omni_converter_jtk.MaterialType
  - ePreviewSurface_OmniPBR: omni.converter.jtk._omni_converter_jtk.MaterialType

- class Parameters
  - def __init__(self)
  - def __init__(self, args: typing.Dict[str, str])
  - def toArgs(self) -> typing.Dict[str, str]
  - [property] def convertCurves(self) -> bool
  - [convertCurves.setter] def convertCurves(self, arg0: bool)
  - [property] def creator(self) -> str
  - [creator.setter] def creator(self, arg0: str)
  - [property] def fallbackTessParamAngular(self) -> float
  - [fallbackTessParamAngular.setter] def fallbackTessParamAngular(self, arg0: float)
  - [property] def fallbackTessParamChordal(self) -> float
  - [fallbackTessParamChordal.setter] def fallbackTessParamChordal(self, arg0: float)
  - [property] def fallbackTessParamHoleRemovalFraction(self) -> float
  - [fallbackTessParamHoleRemovalFraction.setter] def fallbackTessParamHoleRemovalFraction(self, arg0: float)
  - [property] def fallbackTessParamLength(self) -> float
  - [fallbackTessParamLength.setter] def fallbackTessParamLength(self, arg0: float)
  - [property] def fallbackTessParamMaxAspect(self) -> float
  - [fallbackTessParamMaxAspect.setter] def fallbackTessParamMaxAspect(self, arg0: float)
  - [property] def fallbackTessParamMinAngle(self) -> float
  - [fallbackTessParamMinAngle.setter] def fallbackTessParamMinAngle(self, arg0: float)
  - [property] def fallbackTessParamMinEdgeLength(self) -> float
  - [fallbackTessParamMinEdgeLength.setter] def fallbackTessParamMinEdgeLength(self, arg0: float)
  - [property] def fallbackTessParamTrimSuppress(self) -> bool
  - [fallbackTessParamTrimSuppress.setter] def fallbackTessParamTrimSuppress(self, arg0: bool)
  - [property] def flatten(self) -> bool
  - [flatten.setter] def flatten(self, arg0: bool)
  - [property] def instancingStyle(self) -> InstancingStyle
  - [instancingStyle.setter] def instancingStyle(self, arg0: InstancingStyle)
  - [property] def layerFilterStyle(self) -> LayerFilterStyle
  - [layerFilterStyle.setter] def layerFilterStyle(self, arg0: LayerFilterStyle)
  - [property] def materialType(self) -> MaterialType
  - [materialType.setter] def materialType(self, arg0: MaterialType)
  - [property] def overrideTessellationGeometry(self) -> bool
  - [overrideTessellationGeometry.setter] def overrideTessellationGeometry(self, arg0: bool)
  - [property] def overrideTessellationParameters(self) -> bool
  - [overrideTessellationParameters.setter] def overrideTessellationParameters(self, arg0: bool)
  - [property] def progressLogging(self) -> bool
  - [progressLogging.setter] def progressLogging(self, arg0: bool)

## Functions

- def convert(params: Parameters, inputPath: str, outputPath: str, args: typing.Dict[str, str] = {}) -> typing.Tuple[int, str]
- def shutdown()

# Public API for module omni.converter.jtk.tokens:

## Variables

- nodeType: str
