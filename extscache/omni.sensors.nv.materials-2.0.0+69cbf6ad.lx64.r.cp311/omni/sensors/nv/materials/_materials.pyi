from __future__ import annotations
import omni.sensors.nv.materials._materials
import typing
import omni.sensors.nv.common._common

__all__ = [
    "BulkProperties",
    "CoatingVariantProperties",
    "IMaterialReader",
    "IMaterialReaderFactory",
    "IMaterialUtilBSDF",
    "IMaterialUtilBSDFFactory",
    "NvMatInFlags",
    "NvMatInput",
    "NvMatOutput",
    "NvMatRayProps",
    "NvPolarizedRayProps",
    "PaintVariantProperties",
    "SpectralProperties",
    "WaveType",
    "acquire_material_profile_reader_interface",
    "acquire_material_util_bsdf_interface",
    "calcSolidAngleForMat",
    "calcSolidAngleForMatPolarized",
    "release_material_profile_reader_interface",
    "release_material_util_bsdf_interface"
]


class BulkProperties():
    def __init__(self) -> None: ...
    @property
    def compressibility(self) -> float:
        """
        :type: float
        """
    @compressibility.setter
    def compressibility(self, arg0: float) -> None:
        pass
    @property
    def density(self) -> float:
        """
        :type: float
        """
    @density.setter
    def density(self, arg0: float) -> None:
        pass
    @property
    def porosity(self) -> float:
        """
        :type: float
        """
    @porosity.setter
    def porosity(self, arg0: float) -> None:
        pass
    @property
    def solarAbsorptivity(self) -> float:
        """
        :type: float
        """
    @solarAbsorptivity.setter
    def solarAbsorptivity(self, arg0: float) -> None:
        pass
    @property
    def specificHeat(self) -> float:
        """
        :type: float
        """
    @specificHeat.setter
    def specificHeat(self, arg0: float) -> None:
        pass
    @property
    def thermalConductivity(self) -> float:
        """
        :type: float
        """
    @thermalConductivity.setter
    def thermalConductivity(self, arg0: float) -> None:
        pass
    @property
    def thickness(self) -> float:
        """
        :type: float
        """
    @thickness.setter
    def thickness(self, arg0: float) -> None:
        pass
    pass
class CoatingVariantProperties():
    def __init__(self) -> None: ...
    @property
    def diffuseAlbedo(self) -> float:
        """
        :type: float
        """
    @diffuseAlbedo.setter
    def diffuseAlbedo(self, arg0: float) -> None:
        pass
    @property
    def lobewidthFraction(self) -> float:
        """
        :type: float
        """
    @lobewidthFraction.setter
    def lobewidthFraction(self, arg0: float) -> None:
        pass
    @property
    def permeabilityImag(self) -> float:
        """
        :type: float
        """
    @permeabilityImag.setter
    def permeabilityImag(self, arg0: float) -> None:
        pass
    @property
    def permeabilityReal(self) -> float:
        """
        :type: float
        """
    @permeabilityReal.setter
    def permeabilityReal(self, arg0: float) -> None:
        pass
    @property
    def permittivityImag(self) -> float:
        """
        :type: float
        """
    @permittivityImag.setter
    def permittivityImag(self, arg0: float) -> None:
        pass
    @property
    def permittivityReal(self) -> float:
        """
        :type: float
        """
    @permittivityReal.setter
    def permittivityReal(self, arg0: float) -> None:
        pass
    @property
    def refractiveIndexImag(self) -> float:
        """
        :type: float
        """
    @refractiveIndexImag.setter
    def refractiveIndexImag(self, arg0: float) -> None:
        pass
    @property
    def refractiveIndexReal(self) -> float:
        """
        :type: float
        """
    @refractiveIndexReal.setter
    def refractiveIndexReal(self, arg0: float) -> None:
        pass
    @property
    def thickness(self) -> float:
        """
        :type: float
        """
    @thickness.setter
    def thickness(self, arg0: float) -> None:
        pass
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    @wavelength.setter
    def wavelength(self, arg0: float) -> None:
        pass
    pass
class IMaterialReader():
    def getNumPaintVariantProperties(self, arg0: float, arg1: float) -> int: ...
    def initialize(self) -> None: ...
    def parseCoatingVariantJson(self, arg0: str) -> None: ...
    def parseJson(self, arg0: str) -> None: ...
    def parsePaintVariantJson(self, arg0: str) -> None: ...
    def readAndParseCoatingVariantJsonFile(self, arg0: str) -> None: ...
    def readAndParseJsonFile(self, arg0: str) -> None: ...
    def readAndParsePaintVariantJsonFile(self, arg0: str) -> None: ...
    @staticmethod
    def readJsonFile(*args, **kwargs) -> typing.Any: ...
    def readMaterialProperties(self, arg0: BulkProperties, arg1: SpectralProperties, arg2: float, arg3: float, arg4: WaveType) -> bool: ...
    def readVariantProperties(self, arg0: CoatingVariantProperties, arg1: PaintVariantProperties, arg2: float, arg3: float, arg4: WaveType) -> bool: ...
    pass
class IMaterialReaderFactory():
    def createInstance(self) -> IMaterialReader: ...
    pass
class IMaterialUtilBSDF():
    def computeBSDF(self, arg0: NvMatInput, arg1: NvMatOutput, arg2: NvPolarizedRayProps, arg3: NvPolarizedRayProps, arg4: NvPolarizedRayProps, arg5: NvPolarizedRayProps, arg6: BulkProperties, arg7: SpectralProperties, arg8: bool) -> float: ...
    def initialize(self, arg0: int) -> None: ...
    def initializePaintVariants(self, arg0: PaintVariantProperties) -> None: ...
    def setCoatingAndPaintVariants(self, arg0: CoatingVariantProperties, arg1: PaintVariantProperties) -> None: ...
    def uninitializePaintVariants(self, arg0: PaintVariantProperties) -> None: ...
    def useRandomState(self, arg0: bool) -> None: ...
    pass
class IMaterialUtilBSDFFactory():
    def createInstance(self) -> IMaterialUtilBSDF: ...
    pass
class NvMatInFlags():
    """
    Members:

      CALC_R

      CALC_T

      CALC_PHASE_AND_POLARIZED

      CALC_INTERNAL_TERMS
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
    CALC_INTERNAL_TERMS: omni.sensors.nv.materials._materials.NvMatInFlags # value = <NvMatInFlags.CALC_INTERNAL_TERMS: 8>
    CALC_PHASE_AND_POLARIZED: omni.sensors.nv.materials._materials.NvMatInFlags # value = <NvMatInFlags.CALC_PHASE_AND_POLARIZED: 4>
    CALC_R: omni.sensors.nv.materials._materials.NvMatInFlags # value = <NvMatInFlags.CALC_R: 1>
    CALC_T: omni.sensors.nv.materials._materials.NvMatInFlags # value = <NvMatInFlags.CALC_T: 2>
    __members__: dict # value = {'CALC_R': <NvMatInFlags.CALC_R: 1>, 'CALC_T': <NvMatInFlags.CALC_T: 2>, 'CALC_PHASE_AND_POLARIZED': <NvMatInFlags.CALC_PHASE_AND_POLARIZED: 4>, 'CALC_INTERNAL_TERMS': <NvMatInFlags.CALC_INTERNAL_TERMS: 8>}
    pass
class NvMatInput():
    def __init__(self) -> None: ...
    @property
    def customPropsSize(self) -> int:
        """
        :type: int
        """
    @customPropsSize.setter
    def customPropsSize(self, arg0: int) -> None:
        pass
    @property
    def diffuseRefl(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @diffuseRefl.setter
    def diffuseRefl(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def distPrevHit(self) -> float:
        """
        :type: float
        """
    @distPrevHit.setter
    def distPrevHit(self, arg0: float) -> None:
        pass
    @property
    def flags(self) -> int:
        """
        :type: int
        """
    @flags.setter
    def flags(self, arg0: int) -> None:
        pass
    @property
    def hitPoint(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @hitPoint.setter
    def hitPoint(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def incRayDir(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @incRayDir.setter
    def incRayDir(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def incRayProps(self) -> NvMatRayProps:
        """
        :type: NvMatRayProps
        """
    @incRayProps.setter
    def incRayProps(self, arg0: NvMatRayProps) -> None:
        pass
    @property
    def lookupRayDir(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @lookupRayDir.setter
    def lookupRayDir(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def matNormal(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @matNormal.setter
    def matNormal(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def materialId(self) -> int:
        """
        :type: int
        """
    @materialId.setter
    def materialId(self, arg0: int) -> None:
        pass
    @property
    def preserveMaterialFlags(self) -> int:
        """
        :type: int
        """
    @preserveMaterialFlags.setter
    def preserveMaterialFlags(self, arg0: int) -> None:
        pass
    @property
    def randomState(self) -> int:
        """
        :type: int
        """
    @randomState.setter
    def randomState(self, arg1: int) -> None:
        pass
    @property
    def roughness(self) -> float:
        """
        :type: float
        """
    @roughness.setter
    def roughness(self, arg0: float) -> None:
        pass
    @property
    def sourceDivergence(self) -> float:
        """
        :type: float
        """
    @sourceDivergence.setter
    def sourceDivergence(self, arg0: float) -> None:
        pass
    @property
    def thickness(self) -> float:
        """
        :type: float
        """
    @thickness.setter
    def thickness(self, arg0: float) -> None:
        pass
    @property
    def vertexNormals(self) -> typing.List[omni.sensors.nv.common._common.float3]:
        """
        :type: typing.List[omni.sensors.nv.common._common.float3]
        """
    @vertexNormals.setter
    def vertexNormals(self, arg1: typing.List[float]) -> None:
        pass
    @property
    def vertices(self) -> typing.List[omni.sensors.nv.common._common.float3]:
        """
        :type: typing.List[omni.sensors.nv.common._common.float3]
        """
    @vertices.setter
    def vertices(self, arg1: typing.List[float]) -> None:
        pass
    pass
class NvMatOutput():
    def __init__(self) -> None: ...
    @property
    def distThroughCurMat(self) -> float:
        """
        :type: float
        """
    @distThroughCurMat.setter
    def distThroughCurMat(self, arg0: float) -> None:
        pass
    @property
    def exitPoint(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @exitPoint.setter
    def exitPoint(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def lookupRayProps(self) -> NvMatRayProps:
        """
        :type: NvMatRayProps
        """
    @lookupRayProps.setter
    def lookupRayProps(self, arg0: NvMatRayProps) -> None:
        pass
    @property
    def materialId(self) -> int:
        """
        :type: int
        """
    @materialId.setter
    def materialId(self, arg0: int) -> None:
        pass
    @property
    def outDivergence(self) -> float:
        """
        :type: float
        """
    @outDivergence.setter
    def outDivergence(self, arg0: float) -> None:
        pass
    @property
    def reflRayDir(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @reflRayDir.setter
    def reflRayDir(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def reflRayProps(self) -> NvMatRayProps:
        """
        :type: NvMatRayProps
        """
    @reflRayProps.setter
    def reflRayProps(self, arg0: NvMatRayProps) -> None:
        pass
    @property
    def transRayDir(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @transRayDir.setter
    def transRayDir(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    @property
    def transRayProps(self) -> NvMatRayProps:
        """
        :type: NvMatRayProps
        """
    @transRayProps.setter
    def transRayProps(self, arg0: NvMatRayProps) -> None:
        pass
    pass
class NvPolarizedRayProps(NvMatRayProps):
    def __init__(self) -> None: ...
    @property
    def coherent(self) -> omni.sensors.nv.common._common.float4:
        """
        :type: omni.sensors.nv.common._common.float4
        """
    @coherent.setter
    def coherent(self, arg0: omni.sensors.nv.common._common.float4) -> None:
        pass
    @property
    def crossCoherent(self) -> omni.sensors.nv.common._common.float4:
        """
        :type: omni.sensors.nv.common._common.float4
        """
    @crossCoherent.setter
    def crossCoherent(self, arg0: omni.sensors.nv.common._common.float4) -> None:
        pass
    @property
    def crossDiffuse(self) -> omni.sensors.nv.common._common.float2:
        """
        :type: omni.sensors.nv.common._common.float2
        """
    @crossDiffuse.setter
    def crossDiffuse(self, arg0: omni.sensors.nv.common._common.float2) -> None:
        pass
    @property
    def diffuse(self) -> omni.sensors.nv.common._common.float2:
        """
        :type: omni.sensors.nv.common._common.float2
        """
    @diffuse.setter
    def diffuse(self, arg0: omni.sensors.nv.common._common.float2) -> None:
        pass
    pass
class NvMatRayProps():
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: omni.sensors.nv.common._common.float3) -> None: ...
    @property
    def vector(self) -> omni.sensors.nv.common._common.float3:
        """
        :type: omni.sensors.nv.common._common.float3
        """
    @vector.setter
    def vector(self, arg0: omni.sensors.nv.common._common.float3) -> None:
        pass
    pass
class PaintVariantProperties():
    def __init__(self) -> None: ...
    @property
    def diffuseAlbedo(self) -> float:
        """
        :type: float
        """
    @diffuseAlbedo.setter
    def diffuseAlbedo(self, arg0: float) -> None:
        pass
    @property
    def lobewidthFraction(self) -> float:
        """
        :type: float
        """
    @lobewidthFraction.setter
    def lobewidthFraction(self, arg0: float) -> None:
        pass
    @property
    def numPaintVariants(self) -> int:
        """
        :type: int
        """
    @numPaintVariants.setter
    def numPaintVariants(self, arg0: int) -> None:
        pass
    @property
    def permeabilityImag(self) -> float:
        """
        :type: float
        """
    @permeabilityImag.setter
    def permeabilityImag(self, arg0: float) -> None:
        pass
    @property
    def permeabilityReal(self) -> float:
        """
        :type: float
        """
    @permeabilityReal.setter
    def permeabilityReal(self, arg0: float) -> None:
        pass
    @property
    def permittivityImag(self) -> float:
        """
        :type: float
        """
    @permittivityImag.setter
    def permittivityImag(self, arg0: float) -> None:
        pass
    @property
    def permittivityReal(self) -> float:
        """
        :type: float
        """
    @permittivityReal.setter
    def permittivityReal(self, arg0: float) -> None:
        pass
    @property
    def refractiveIndexImag(self) -> float:
        """
        :type: float
        """
    @refractiveIndexImag.setter
    def refractiveIndexImag(self, arg0: float) -> None:
        pass
    @property
    def refractiveIndexReal(self) -> float:
        """
        :type: float
        """
    @refractiveIndexReal.setter
    def refractiveIndexReal(self, arg0: float) -> None:
        pass
    @property
    def thickness(self) -> float:
        """
        :type: float
        """
    @thickness.setter
    def thickness(self, arg0: float) -> None:
        pass
    @property
    def visibleColor(self) -> float:
        """
        :type: float
        """
    @visibleColor.setter
    def visibleColor(self, arg0: float) -> None:
        pass
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    @wavelength.setter
    def wavelength(self, arg0: float) -> None:
        pass
    pass
class SpectralProperties():
    def __init__(self) -> None: ...
    @property
    def baseRCS(self) -> float:
        """
        :type: float
        """
    @baseRCS.setter
    def baseRCS(self, arg0: float) -> None:
        pass
    @property
    def diffuseAlbedo(self) -> float:
        """
        :type: float
        """
    @diffuseAlbedo.setter
    def diffuseAlbedo(self, arg0: float) -> None:
        pass
    @property
    def emissivity(self) -> float:
        """
        :type: float
        """
    @emissivity.setter
    def emissivity(self, arg0: float) -> None:
        pass
    @property
    def lobewidth(self) -> float:
        """
        :type: float
        """
    @lobewidth.setter
    def lobewidth(self, arg0: float) -> None:
        pass
    @property
    def permeabilityImag(self) -> float:
        """
        :type: float
        """
    @permeabilityImag.setter
    def permeabilityImag(self, arg0: float) -> None:
        pass
    @property
    def permeabilityReal(self) -> float:
        """
        :type: float
        """
    @permeabilityReal.setter
    def permeabilityReal(self, arg0: float) -> None:
        pass
    @property
    def permittivityImag(self) -> float:
        """
        :type: float
        """
    @permittivityImag.setter
    def permittivityImag(self, arg0: float) -> None:
        pass
    @property
    def permittivityReal(self) -> float:
        """
        :type: float
        """
    @permittivityReal.setter
    def permittivityReal(self, arg0: float) -> None:
        pass
    @property
    def refractiveIndexImag(self) -> float:
        """
        :type: float
        """
    @refractiveIndexImag.setter
    def refractiveIndexImag(self, arg0: float) -> None:
        pass
    @property
    def refractiveIndexReal(self) -> float:
        """
        :type: float
        """
    @refractiveIndexReal.setter
    def refractiveIndexReal(self, arg0: float) -> None:
        pass
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    @wavelength.setter
    def wavelength(self, arg0: float) -> None:
        pass
    pass
class WaveType():
    """
    Members:

      WAVE_MECHANICAL

      WAVE_ELECTROMAGNETIC
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
    WAVE_ELECTROMAGNETIC: omni.sensors.nv.materials._materials.WaveType # value = <WaveType.WAVE_ELECTROMAGNETIC: 1>
    WAVE_MECHANICAL: omni.sensors.nv.materials._materials.WaveType # value = <WaveType.WAVE_MECHANICAL: 0>
    __members__: dict # value = {'WAVE_MECHANICAL': <WaveType.WAVE_MECHANICAL: 0>, 'WAVE_ELECTROMAGNETIC': <WaveType.WAVE_ELECTROMAGNETIC: 1>}
    pass
def acquire_material_profile_reader_interface(plugin_name: str = None, library_path: str = None) -> IMaterialReaderFactory:
    pass
def acquire_material_util_bsdf_interface(plugin_name: str = None, library_path: str = None) -> IMaterialUtilBSDFFactory:
    pass
def calcSolidAngleForMat(arg0: SpectralProperties, arg1: SpectralProperties, arg2: NvMatInput) -> omni.sensors.nv.common._common.float2:
    pass
def calcSolidAngleForMatPolarized(arg0: SpectralProperties, arg1: SpectralProperties, arg2: NvMatInput) -> omni.sensors.nv.common._common.float2:
    pass
def release_material_profile_reader_interface(arg0: IMaterialReaderFactory) -> None:
    pass
def release_material_util_bsdf_interface(arg0: IMaterialUtilBSDFFactory) -> None:
    pass
