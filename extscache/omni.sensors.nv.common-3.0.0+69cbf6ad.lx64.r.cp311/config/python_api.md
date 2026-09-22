# Public API for module omni.sensors.nv.common:

## Classes

- class DWPodAccessType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - READ: omni.sensors.nv.common._common.DWPodAccessType
  - WRITE: omni.sensors.nv.common._common.DWPodAccessType

- class DWPodIOConfig
  - def __init__(self)
  - [property] def accessType(self) -> DWPodAccessType
  - [accessType.setter] def accessType(self, arg0: DWPodAccessType)
  - [property] def desiredTrackId(self) -> int
  - [desiredTrackId.setter] def desiredTrackId(self, arg0: int)
  - [property] def fileName(self) -> str
  - [fileName.setter] def fileName(self, arg1: str)
  - [property] def trackHeaderDataBuffer(self) -> TimedDataBuffer
  - [trackHeaderDataBuffer.setter] def trackHeaderDataBuffer(self, arg0: TimedDataBuffer)

- class IAtmosCfgProvider
  - static def calcAerosolCfg(*args, **kwargs) -> typing.Any
  - def calcRefrIndexOfWater(self, arg0: float, arg1: float, arg2: float)
  - def calcWeatherCfg(self, arg0: float, arg1: float, arg2: int, arg3: float, arg4: float) -> WeatherCfg

- class IAtmosCfgProviderFactory
  - def createInstance(self) -> IAtmosCfgProvider

- class IDWPodIO
  - def dumpPacket(self, arg0: capsule, arg1: int, arg2: capsule, arg3: int, arg4: int)
  - def getCfg(self) -> DWPodIOConfig
  - def init(self, arg0: DWPodIOConfig)
  - def readNextPacket(self) -> TimedDataBuffer

- class IDWPodIOFactory
  - def createInstance(self) -> IDWPodIO

- class IProfileReader
  - def dataSizeProfile(self) -> int
  - def init(self, arg0: str, arg1: ProfileType)
  - def isValid(self) -> bool
  - def name(self) -> str
  - def update(self, arg0: buffer)

- class IProfileReaderFactory
  - def createInstance(self) -> IProfileReader

- class MieCfg
  - def __init__(self)
  - [property] def Qbsca(self) -> float
  - [Qbsca.setter] def Qbsca(self, arg0: float)
  - [property] def Qext(self) -> float
  - [Qext.setter] def Qext(self, arg0: float)
  - [property] def Qsca(self) -> float
  - [Qsca.setter] def Qsca(self, arg0: float)
  - [property] def S1(self) -> float
  - [S1.setter] def S1(self, arg0: float)
  - [property] def S2(self) -> float
  - [S2.setter] def S2(self, arg0: float)
  - [property] def alpha(self) -> float
  - [alpha.setter] def alpha(self, arg0: float)
  - [property] def backScatter(self) -> float
  - [backScatter.setter] def backScatter(self, arg0: float)
  - [property] def beta(self) -> float
  - [beta.setter] def beta(self, arg0: float)
  - [property] def betaFValue(self) -> float
  - [betaFValue.setter] def betaFValue(self, arg0: float)
  - [property] def g(self) -> float
  - [g.setter] def g(self, arg0: float)
  - [property] def gammaExt(self) -> float
  - [gammaExt.setter] def gammaExt(self, arg0: float)

- class ParticulateCfg
  - def __init__(self)
  - [property] def Dg(self) -> float
  - [Dg.setter] def Dg(self, arg0: float)
  - [property] def Nt(self) -> float
  - [Nt.setter] def Nt(self, arg0: float)
  - [property] def dropSizeMax(self) -> float
  - [dropSizeMax.setter] def dropSizeMax(self, arg0: float)
  - [property] def dropSizeMin(self) -> float
  - [dropSizeMin.setter] def dropSizeMin(self, arg0: float)
  - [property] def sigma(self) -> float
  - [sigma.setter] def sigma(self, arg0: float)

- class Point
  - def __init__(self)
  - [property] def pos(self) -> float3
  - [pos.setter] def pos(self, arg0: float3)
  - [property] def value(self) -> float
  - [value.setter] def value(self, arg0: float)

- class ProfileType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - LIDAR: omni.sensors.nv.common._common.ProfileType
  - RADAR: omni.sensors.nv.common._common.ProfileType
  - USS: omni.sensors.nv.common._common.ProfileType
  - WPM_RADAR: omni.sensors.nv.common._common.ProfileType

- class TimedDataBuffer
  - def __init__(self)
  - def getDataSize(self) -> int
  - [property] def dataBuffer(self) -> numpy.ndarray
  - [property] def timestampNs(self) -> int
  - [timestampNs.setter] def timestampNs(self, arg0: int)

- class WeatherCfg
  - def __init__(self)
  - [property] def R(self) -> float
  - [R.setter] def R(self, arg0: float)
  - [property] def mieCfg(self) -> MieCfg
  - [mieCfg.setter] def mieCfg(self, arg0: MieCfg)
  - [property] def particulateCfg(self) -> ParticulateCfg
  - [particulateCfg.setter] def particulateCfg(self, arg0: ParticulateCfg)

- class float2
  - def __init__(self)
  - def make_float2(self, arg0: float) -> float2
  - [property] def x(self) -> float
  - [x.setter] def x(self, arg0: float)
  - [property] def y(self) -> float
  - [y.setter] def y(self, arg0: float)

- class float3
  - def __init__(self)
  - def make_float3(self, arg0: float, arg1: float) -> float3
  - [property] def x(self) -> float
  - [x.setter] def x(self, arg0: float)
  - [property] def y(self) -> float
  - [y.setter] def y(self, arg0: float)
  - [property] def z(self) -> float
  - [z.setter] def z(self, arg0: float)

- class float4
  - def __init__(self)
  - def make_float4(self, arg0: float, arg1: float, arg2: float) -> float4
  - [property] def w(self) -> float
  - [w.setter] def w(self, arg0: float)
  - [property] def x(self) -> float
  - [x.setter] def x(self, arg0: float)
  - [property] def y(self) -> float
  - [y.setter] def y(self, arg0: float)
  - [property] def z(self) -> float
  - [z.setter] def z(self, arg0: float)

## Functions

- def ND(arg0: float, arg1: float, arg2: float, arg3: float) -> float
- def NDInt(arg0: ParticulateCfg, arg1: int) -> float
- def acquire_atmos_cfg_provider_interface(plugin_name: str = None, library_path: str = None) -> IAtmosCfgProviderFactory
- def acquire_dwpod_io_interface(plugin_name: str = None, library_path: str = None) -> IDWPodIOFactory
- def acquire_profile_reader_interface(plugin_name: str = None, library_path: str = None) -> IProfileReaderFactory
- def crossBScaInt(arg0: WeatherCfg, arg1: int) -> float
- def fillQs(arg0: WeatherCfg, arg1: float, arg2: float)
- def fillWeatherBasics(arg0: MieCfg, arg1: ParticulateCfg, arg2: float)
- def getRefrIndexOfWater(arg0: float) -> complex
- def getTransmissionFactor(arg0: float, arg1: float) -> float
- def release_atmos_cfg_provider_interface(arg0: IAtmosCfgProviderFactory)
- def release_dwpod_io_interface(arg0: IDWPodIOFactory)
- def release_profile_reader_interface(arg0: IProfileReaderFactory)
