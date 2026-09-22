from __future__ import annotations
import omni.sensors.nv.common._common
import typing

__all__ = [
    "DWPodAccessType",
    "DWPodIOConfig",
    "IAtmosCfgProvider",
    "IAtmosCfgProviderFactory",
    "IDWPodIO",
    "IDWPodIOFactory",
    "IProfileReader",
    "IProfileReaderFactory",
    "MieCfg",
    "ND",
    "NDInt",
    "ParticulateCfg",
    "Point",
    "ProfileType",
    "TimedDataBuffer",
    "WeatherCfg",
    "acquire_atmos_cfg_provider_interface",
    "acquire_dwpod_io_interface",
    "acquire_profile_reader_interface",
    "crossBScaInt",
    "fillQs",
    "fillWeatherBasics",
    "float2",
    "float3",
    "float4",
    "getRefrIndexOfWater",
    "getTransmissionFactor",
    "release_atmos_cfg_provider_interface",
    "release_dwpod_io_interface",
    "release_profile_reader_interface"
]


class DWPodAccessType():
    """
    Members:

      READ

      WRITE
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
    READ: omni.sensors.nv.common._common.DWPodAccessType # value = <DWPodAccessType.READ: 0>
    WRITE: omni.sensors.nv.common._common.DWPodAccessType # value = <DWPodAccessType.WRITE: 1>
    __members__: dict # value = {'READ': <DWPodAccessType.READ: 0>, 'WRITE': <DWPodAccessType.WRITE: 1>}
    pass
class DWPodIOConfig():
    def __init__(self) -> None: ...
    @property
    def accessType(self) -> DWPodAccessType:
        """
        :type: DWPodAccessType
        """
    @accessType.setter
    def accessType(self, arg0: DWPodAccessType) -> None:
        pass
    @property
    def desiredTrackId(self) -> int:
        """
        :type: int
        """
    @desiredTrackId.setter
    def desiredTrackId(self, arg0: int) -> None:
        pass
    @property
    def fileName(self) -> str:
        """
        :type: str
        """
    @fileName.setter
    def fileName(self, arg1: str) -> None:
        pass
    @property
    def trackHeaderDataBuffer(self) -> TimedDataBuffer:
        """
        :type: TimedDataBuffer
        """
    @trackHeaderDataBuffer.setter
    def trackHeaderDataBuffer(self, arg0: TimedDataBuffer) -> None:
        pass
    pass
class IAtmosCfgProvider():
    @staticmethod
    def calcAerosolCfg(*args, **kwargs) -> typing.Any: ...
    def calcRefrIndexOfWater(self, arg0: float, arg1: float, arg2: float) -> None: ...
    def calcWeatherCfg(self, arg0: float, arg1: float, arg2: int, arg3: float, arg4: float) -> WeatherCfg: ...
    pass
class IAtmosCfgProviderFactory():
    def createInstance(self) -> IAtmosCfgProvider: ...
    pass
class IDWPodIO():
    def dumpPacket(self, arg0: capsule, arg1: int, arg2: capsule, arg3: int, arg4: int) -> None: ...
    def getCfg(self) -> DWPodIOConfig: ...
    def init(self, arg0: DWPodIOConfig) -> None: ...
    def readNextPacket(self) -> TimedDataBuffer: ...
    pass
class IDWPodIOFactory():
    def createInstance(self) -> IDWPodIO: ...
    pass
class IProfileReader():
    def dataSizeProfile(self) -> int: ...
    def init(self, arg0: str, arg1: ProfileType) -> None: ...
    def isValid(self) -> bool: ...
    def name(self) -> str: ...
    def update(self, arg0: buffer) -> None: ...
    pass
class IProfileReaderFactory():
    def createInstance(self) -> IProfileReader: ...
    pass
class MieCfg():
    def __init__(self) -> None: ...
    @property
    def Qbsca(self) -> float:
        """
        :type: float
        """
    @Qbsca.setter
    def Qbsca(self, arg0: float) -> None:
        pass
    @property
    def Qext(self) -> float:
        """
        :type: float
        """
    @Qext.setter
    def Qext(self, arg0: float) -> None:
        pass
    @property
    def Qsca(self) -> float:
        """
        :type: float
        """
    @Qsca.setter
    def Qsca(self, arg0: float) -> None:
        pass
    @property
    def S1(self) -> float:
        """
        :type: float
        """
    @S1.setter
    def S1(self, arg0: float) -> None:
        pass
    @property
    def S2(self) -> float:
        """
        :type: float
        """
    @S2.setter
    def S2(self, arg0: float) -> None:
        pass
    @property
    def alpha(self) -> float:
        """
        :type: float
        """
    @alpha.setter
    def alpha(self, arg0: float) -> None:
        pass
    @property
    def backScatter(self) -> float:
        """
        :type: float
        """
    @backScatter.setter
    def backScatter(self, arg0: float) -> None:
        pass
    @property
    def beta(self) -> float:
        """
        :type: float
        """
    @beta.setter
    def beta(self, arg0: float) -> None:
        pass
    @property
    def betaFValue(self) -> float:
        """
        :type: float
        """
    @betaFValue.setter
    def betaFValue(self, arg0: float) -> None:
        pass
    @property
    def g(self) -> float:
        """
        :type: float
        """
    @g.setter
    def g(self, arg0: float) -> None:
        pass
    @property
    def gammaExt(self) -> float:
        """
        :type: float
        """
    @gammaExt.setter
    def gammaExt(self, arg0: float) -> None:
        pass
    pass
class ParticulateCfg():
    def __init__(self) -> None: ...
    @property
    def Dg(self) -> float:
        """
        :type: float
        """
    @Dg.setter
    def Dg(self, arg0: float) -> None:
        pass
    @property
    def Nt(self) -> float:
        """
        :type: float
        """
    @Nt.setter
    def Nt(self, arg0: float) -> None:
        pass
    @property
    def dropSizeMax(self) -> float:
        """
        :type: float
        """
    @dropSizeMax.setter
    def dropSizeMax(self, arg0: float) -> None:
        pass
    @property
    def dropSizeMin(self) -> float:
        """
        :type: float
        """
    @dropSizeMin.setter
    def dropSizeMin(self, arg0: float) -> None:
        pass
    @property
    def sigma(self) -> float:
        """
        :type: float
        """
    @sigma.setter
    def sigma(self, arg0: float) -> None:
        pass
    pass
class Point():
    def __init__(self) -> None: ...
    @property
    def pos(self) -> float3:
        """
        :type: float3
        """
    @pos.setter
    def pos(self, arg0: float3) -> None:
        pass
    @property
    def value(self) -> float:
        """
        :type: float
        """
    @value.setter
    def value(self, arg0: float) -> None:
        pass
    pass
class ProfileType():
    """
    Members:

      LIDAR

      USS

      RADAR

      WPM_RADAR
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
    LIDAR: omni.sensors.nv.common._common.ProfileType # value = <ProfileType.LIDAR: 0>
    RADAR: omni.sensors.nv.common._common.ProfileType # value = <ProfileType.RADAR: 3>
    USS: omni.sensors.nv.common._common.ProfileType # value = <ProfileType.USS: 1>
    WPM_RADAR: omni.sensors.nv.common._common.ProfileType # value = <ProfileType.WPM_RADAR: 4>
    __members__: dict # value = {'LIDAR': <ProfileType.LIDAR: 0>, 'USS': <ProfileType.USS: 1>, 'RADAR': <ProfileType.RADAR: 3>, 'WPM_RADAR': <ProfileType.WPM_RADAR: 4>}
    pass
class TimedDataBuffer():
    def __init__(self) -> None: ...
    def getDataSize(self) -> int: ...
    @property
    def dataBuffer(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def timestampNs(self) -> int:
        """
        :type: int
        """
    @timestampNs.setter
    def timestampNs(self, arg0: int) -> None:
        pass
    pass
class WeatherCfg():
    def __init__(self) -> None: ...
    @property
    def R(self) -> float:
        """
        :type: float
        """
    @R.setter
    def R(self, arg0: float) -> None:
        pass
    @property
    def mieCfg(self) -> MieCfg:
        """
        :type: MieCfg
        """
    @mieCfg.setter
    def mieCfg(self, arg0: MieCfg) -> None:
        pass
    @property
    def particulateCfg(self) -> ParticulateCfg:
        """
        :type: ParticulateCfg
        """
    @particulateCfg.setter
    def particulateCfg(self, arg0: ParticulateCfg) -> None:
        pass
    pass
class float2():
    def __init__(self) -> None: ...
    def make_float2(self, arg0: float) -> float2: ...
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        pass
    pass
class float3():
    def __init__(self) -> None: ...
    def make_float3(self, arg0: float, arg1: float) -> float3: ...
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        pass
    @property
    def z(self) -> float:
        """
        :type: float
        """
    @z.setter
    def z(self, arg0: float) -> None:
        pass
    pass
class float4():
    def __init__(self) -> None: ...
    def make_float4(self, arg0: float, arg1: float, arg2: float) -> float4: ...
    @property
    def w(self) -> float:
        """
        :type: float
        """
    @w.setter
    def w(self, arg0: float) -> None:
        pass
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: float) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: float) -> None:
        pass
    @property
    def z(self) -> float:
        """
        :type: float
        """
    @z.setter
    def z(self, arg0: float) -> None:
        pass
    pass
def ND(arg0: float, arg1: float, arg2: float, arg3: float) -> float:
    """
    Function which calculates the number of drops per unit volume.
    """
def NDInt(arg0: ParticulateCfg, arg1: int) -> float:
    """
    ND integrated value
    """
def acquire_atmos_cfg_provider_interface(plugin_name: str = None, library_path: str = None) -> IAtmosCfgProviderFactory:
    pass
def acquire_dwpod_io_interface(plugin_name: str = None, library_path: str = None) -> IDWPodIOFactory:
    pass
def acquire_profile_reader_interface(plugin_name: str = None, library_path: str = None) -> IProfileReaderFactory:
    pass
def crossBScaInt(arg0: WeatherCfg, arg1: int) -> float:
    """
    cross integrated value
    """
def fillQs(arg0: WeatherCfg, arg1: float, arg2: float) -> None:
    pass
def fillWeatherBasics(arg0: MieCfg, arg1: ParticulateCfg, arg2: float) -> None:
    pass
def getRefrIndexOfWater(arg0: float) -> complex:
    """
    Gets refr index of water for given wavelength.

    Gets refr index of water for given wavelength.
    """
def getTransmissionFactor(arg0: float, arg1: float) -> float:
    pass
def release_atmos_cfg_provider_interface(arg0: IAtmosCfgProviderFactory) -> None:
    pass
def release_dwpod_io_interface(arg0: IDWPodIOFactory) -> None:
    pass
def release_profile_reader_interface(arg0: IProfileReaderFactory) -> None:
    pass
