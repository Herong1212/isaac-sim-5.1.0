from __future__ import annotations
import omni.sensors.nv.lidar._lidar
import typing

__all__ = [
    "BeamProfile",
    "EmitterError",
    "ErrorProfile",
    "ILidarPCConverter",
    "ILidarPCConverterFactory",
    "IntensityMappingParam",
    "LidarIntensityMapping",
    "LidarIntensityProcessing",
    "LidarMetaData",
    "LidarPCConverterCfg",
    "LidarPCConverterMode",
    "LidarPCConverterRunMode",
    "LidarProfile",
    "LidarRayType",
    "LidarScanType",
    "Transformation",
    "acquire_pcconverter_interface",
    "computeEmitterPeakPower",
    "getChannelsOfBinFileHeader",
    "getConstDetector",
    "getLidarBinFileHeader",
    "getLidarProfileFromBuffer",
    "getParameterString",
    "getSizeOfBinPacketHeader",
    "getSizeOfLidarBinFileHeader",
    "propagateSimple",
    "release_pcconverter_interface"
]


class BeamProfile():
    def __init__(self) -> None: ...
    @property
    def Msquared(self) -> float:
        """
        :type: float
        """
    @Msquared.setter
    def Msquared(self, arg0: float) -> None:
        pass
    @property
    def aspectRatio(self) -> float:
        """
        :type: float
        """
    @aspectRatio.setter
    def aspectRatio(self, arg0: float) -> None:
        pass
    @property
    def beamWaistHorM(self) -> float:
        """
        :type: float
        """
    @beamWaistHorM.setter
    def beamWaistHorM(self, arg0: float) -> None:
        pass
    @property
    def beamWaistVertM(self) -> float:
        """
        :type: float
        """
    @beamWaistVertM.setter
    def beamWaistVertM(self, arg0: float) -> None:
        pass
    @property
    def divHorRad(self) -> float:
        """
        :type: float
        """
    @divHorRad.setter
    def divHorRad(self, arg0: float) -> None:
        pass
    @property
    def divVertRad(self) -> float:
        """
        :type: float
        """
    @divVertRad.setter
    def divVertRad(self, arg0: float) -> None:
        pass
    @property
    def focusDistM(self) -> float:
        """
        :type: float
        """
    @focusDistM.setter
    def focusDistM(self, arg0: float) -> None:
        pass
    @property
    def wavelengthNm(self) -> float:
        """
        :type: float
        """
    @wavelengthNm.setter
    def wavelengthNm(self, arg0: float) -> None:
        pass
    pass
class EmitterError():
    def __init__(self) -> None: ...
    @property
    def elevation(self) -> ErrorProfile:
        """
        :type: ErrorProfile
        """
    @elevation.setter
    def elevation(self, arg0: ErrorProfile) -> None:
        pass
    @property
    def origin(self) -> typing.List[ErrorProfile]:
        """
        :type: typing.List[ErrorProfile]
        """
    @origin.setter
    def origin(self, arg1: typing.List[ErrorProfile]) -> None:
        pass
    @property
    def std(self) -> ErrorProfile:
        """
        :type: ErrorProfile
        """
    @std.setter
    def std(self, arg0: ErrorProfile) -> None:
        pass
    pass
class ErrorProfile():
    def __init__(self) -> None: ...
    @property
    def mean(self) -> float:
        """
        :type: float
        """
    @mean.setter
    def mean(self, arg0: float) -> None:
        pass
    @property
    def std(self) -> float:
        """
        :type: float
        """
    @std.setter
    def std(self, arg0: float) -> None:
        pass
    pass
class ILidarPCConverter():
    def convertBuffer(self, frameId: int = -1) -> bool: ...
    def convertBufferPython(self, arg0: buffer, arg1: int, arg2: int, arg3: bool) -> None: ...
    def convertPacket(self, arg0: str, arg1: str, arg2: int) -> None: ...
    def getMaxPoints(self) -> int: ...
    def getPacketTime(self, arg0: str) -> int: ...
    @staticmethod
    def getPointCloud(*args, **kwargs) -> typing.Any: ...
    def init(self, arg0: LidarPCConverterCfg) -> None: ...
    def isPacketOfNewScan(self, arg0: str) -> bool: ...
    def setStaticTransformation(self, arg0: typing.List[float], arg1: typing.List[float]) -> None: ...
    @typing.overload
    def setTransformation(self, transformation: Transformation, stream: capsule = None) -> None: ...
    @staticmethod
    @typing.overload
    def setTransformation(*args, **kwargs) -> typing.Any: ...
    def sizeOfVendorPacket(self) -> int: ...
    pass
class ILidarPCConverterFactory():
    def createInstance(self) -> ILidarPCConverter: ...
    pass
class IntensityMappingParam():
    def __init__(self) -> None: ...
    @property
    def decoding(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def elCountDec(self) -> int:
        """
        :type: int
        """
    @elCountDec.setter
    def elCountDec(self, arg0: int) -> None:
        pass
    @property
    def elCountEnc(self) -> int:
        """
        :type: int
        """
    @elCountEnc.setter
    def elCountEnc(self, arg0: int) -> None:
        pass
    @property
    def encoding(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def intensityScalePercent(self) -> float:
        """
        :type: float
        """
    @intensityScalePercent.setter
    def intensityScalePercent(self, arg0: float) -> None:
        pass
    @property
    def type(self) -> LidarIntensityMapping:
        """
        :type: LidarIntensityMapping
        """
    @type.setter
    def type(self, arg0: LidarIntensityMapping) -> None:
        pass
    pass
class LidarIntensityMapping():
    """
    Members:

      LINEAR

      NONLINEAR

      NONLINEAR_ENCODING_ONLY

      NONLINEAR_DECODING_ONLY
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
    LINEAR: omni.sensors.nv.lidar._lidar.LidarIntensityMapping # value = <LidarIntensityMapping.LINEAR: 0>
    NONLINEAR: omni.sensors.nv.lidar._lidar.LidarIntensityMapping # value = <LidarIntensityMapping.NONLINEAR: 1>
    NONLINEAR_DECODING_ONLY: omni.sensors.nv.lidar._lidar.LidarIntensityMapping # value = <LidarIntensityMapping.NONLINEAR_DECODING_ONLY: 3>
    NONLINEAR_ENCODING_ONLY: omni.sensors.nv.lidar._lidar.LidarIntensityMapping # value = <LidarIntensityMapping.NONLINEAR_ENCODING_ONLY: 2>
    __members__: dict # value = {'LINEAR': <LidarIntensityMapping.LINEAR: 0>, 'NONLINEAR': <LidarIntensityMapping.NONLINEAR: 1>, 'NONLINEAR_ENCODING_ONLY': <LidarIntensityMapping.NONLINEAR_ENCODING_ONLY: 2>, 'NONLINEAR_DECODING_ONLY': <LidarIntensityMapping.NONLINEAR_DECODING_ONLY: 3>}
    pass
class LidarIntensityProcessing():
    """
    Members:

      kCorrection

      kRaw

      kNormalization

      kCalibrated

      kPointType

      kNum
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
    __members__: dict # value = {'kCorrection': <LidarIntensityProcessing.kCorrection: 0>, 'kRaw': <LidarIntensityProcessing.kRaw: 1>, 'kNormalization': <LidarIntensityProcessing.kNormalization: 2>, 'kCalibrated': <LidarIntensityProcessing.kCalibrated: 3>, 'kPointType': <LidarIntensityProcessing.kPointType: 4>, 'kNum': <LidarIntensityProcessing.kNum: 5>}
    kCalibrated: omni.sensors.nv.lidar._lidar.LidarIntensityProcessing # value = <LidarIntensityProcessing.kCalibrated: 3>
    kCorrection: omni.sensors.nv.lidar._lidar.LidarIntensityProcessing # value = <LidarIntensityProcessing.kCorrection: 0>
    kNormalization: omni.sensors.nv.lidar._lidar.LidarIntensityProcessing # value = <LidarIntensityProcessing.kNormalization: 2>
    kNum: omni.sensors.nv.lidar._lidar.LidarIntensityProcessing # value = <LidarIntensityProcessing.kNum: 5>
    kPointType: omni.sensors.nv.lidar._lidar.LidarIntensityProcessing # value = <LidarIntensityProcessing.kPointType: 4>
    kRaw: omni.sensors.nv.lidar._lidar.LidarIntensityProcessing # value = <LidarIntensityProcessing.kRaw: 1>
    pass
class LidarMetaData():
    def __init__(self) -> None: ...
    @property
    def dataSize(self) -> int:
        """
        :type: int
        """
    @dataSize.setter
    def dataSize(self, arg0: int) -> None:
        pass
    @property
    def endTimeNs(self) -> int:
        """
        :type: int
        """
    @endTimeNs.setter
    def endTimeNs(self, arg0: int) -> None:
        pass
    @property
    def numPoints(self) -> int:
        """
        :type: int
        """
    @numPoints.setter
    def numPoints(self, arg0: int) -> None:
        pass
    @property
    def scanStartTimeNs(self) -> int:
        """
        :type: int
        """
    @scanStartTimeNs.setter
    def scanStartTimeNs(self, arg0: int) -> None:
        pass
    @property
    def startTimeNs(self) -> int:
        """
        :type: int
        """
    @startTimeNs.setter
    def startTimeNs(self, arg0: int) -> None:
        pass
    pass
class LidarPCConverterCfg():
    def __init__(self) -> None: ...
    @property
    def clientName(self) -> str:
        """
        :type: str
        """
    @clientName.setter
    def clientName(self, arg1: str) -> None:
        pass
    @property
    def constantValue(self) -> float:
        """
        :type: float
        """
    @constantValue.setter
    def constantValue(self, arg0: float) -> None:
        pass
    @property
    def desiredCoordsType(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @desiredCoordsType.setter
    def desiredCoordsType(*args, **kwargs) -> None:
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
    def groupName(self) -> str:
        """
        :type: str
        """
    @groupName.setter
    def groupName(self, arg1: str) -> None:
        pass
    @property
    def maxPoints(self) -> int:
        """
        :type: int
        """
    @maxPoints.setter
    def maxPoints(self, arg0: int) -> None:
        pass
    @property
    def mode(self) -> LidarPCConverterMode:
        """
        :type: LidarPCConverterMode
        """
    @mode.setter
    def mode(self, arg0: LidarPCConverterMode) -> None:
        pass
    @property
    def outputOnGPU(self) -> bool:
        """
        :type: bool
        """
    @outputOnGPU.setter
    def outputOnGPU(self, arg0: bool) -> None:
        pass
    @property
    def profileName(self) -> str:
        """
        :type: str
        """
    @profileName.setter
    def profileName(self, arg1: str) -> None:
        pass
    @property
    def runMode(self) -> LidarPCConverterRunMode:
        """
        :type: LidarPCConverterRunMode
        """
    @runMode.setter
    def runMode(self, arg0: LidarPCConverterRunMode) -> None:
        pass
    @property
    def scanFrequencyHz(self) -> int:
        """
        :type: int
        """
    @scanFrequencyHz.setter
    def scanFrequencyHz(self, arg0: int) -> None:
        pass
    @property
    def syncMode(self) -> bool:
        """
        :type: bool
        """
    @syncMode.setter
    def syncMode(self, arg0: bool) -> None:
        pass
    pass
class LidarPCConverterMode():
    """
    Members:

      GENERIC

      GENERIC_FILE

      PACKETS
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
    GENERIC: omni.sensors.nv.lidar._lidar.LidarPCConverterMode # value = <LidarPCConverterMode.GENERIC: 0>
    GENERIC_FILE: omni.sensors.nv.lidar._lidar.LidarPCConverterMode # value = <LidarPCConverterMode.GENERIC_FILE: 1>
    PACKETS: omni.sensors.nv.lidar._lidar.LidarPCConverterMode # value = <LidarPCConverterMode.PACKETS: 2>
    __members__: dict # value = {'GENERIC': <LidarPCConverterMode.GENERIC: 0>, 'GENERIC_FILE': <LidarPCConverterMode.GENERIC_FILE: 1>, 'PACKETS': <LidarPCConverterMode.PACKETS: 2>}
    pass
class LidarPCConverterRunMode():
    """
    Members:

      CPU
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
    CPU: omni.sensors.nv.lidar._lidar.LidarPCConverterRunMode # value = <LidarPCConverterRunMode.CPU: 0>
    __members__: dict # value = {'CPU': <LidarPCConverterRunMode.CPU: 0>}
    pass
class LidarProfile():
    def __init__(self) -> None: ...
    @property
    def aerosolAtmosParam(self) -> AerosolAtmosProfileParam:
        """
        :type: AerosolAtmosProfileParam
        """
    @aerosolAtmosParam.setter
    def aerosolAtmosParam(self, arg0: AerosolAtmosProfileParam) -> None:
        pass
    @property
    def avgPowerW(self) -> float:
        """
        :type: float
        """
    @avgPowerW.setter
    def avgPowerW(self, arg0: float) -> None:
        pass
    @property
    def beamProfile(self) -> BeamProfile:
        """
        :type: BeamProfile
        """
    @beamProfile.setter
    def beamProfile(self, arg0: BeamProfile) -> None:
        pass
    @property
    def bitDepthResolution(self) -> float:
        """
        :type: float
        """
    @bitDepthResolution.setter
    def bitDepthResolution(self, arg0: float) -> None:
        pass
    @property
    def calibrationGain(self) -> float:
        """
        :type: float
        """
    @calibrationGain.setter
    def calibrationGain(self, arg0: float) -> None:
        pass
    @property
    def dwId(self) -> int:
        """
        :type: int
        """
    @dwId.setter
    def dwId(self, arg0: int) -> None:
        pass
    @property
    def effectiveApertureSize(self) -> float:
        """
        :type: float
        """
    @effectiveApertureSize.setter
    def effectiveApertureSize(self, arg0: float) -> None:
        pass
    @property
    def emitterError(self) -> EmitterError:
        """
        :type: EmitterError
        """
    @emitterError.setter
    def emitterError(self, arg0: EmitterError) -> None:
        pass
    @property
    def emitterProfileAzimuthDeg(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileBank(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileChannelId(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileDistanceCorrectionM(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileElevationDeg(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileFireTimeNs(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileFocalDistM(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileFocalSlope(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileHorOffsetM(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileIsROI(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileIsROIState(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileMaxRange(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileMinRange(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileNumRaysPerLine(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileRangeId(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileReportRateDiv(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterProfileVertOffsetM(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def emitterStateCount(self) -> int:
        """
        :type: int
        """
    @emitterStateCount.setter
    def emitterStateCount(self, arg0: int) -> None:
        pass
    @property
    def farRangeM(self) -> float:
        """
        :type: float
        """
    @farRangeM.setter
    def farRangeM(self, arg0: float) -> None:
        pass
    @property
    def intensityMapping(self) -> IntensityMappingParam:
        """
        :type: IntensityMappingParam
        """
    @intensityMapping.setter
    def intensityMapping(self, arg0: IntensityMappingParam) -> None:
        pass
    @property
    def intensityProcessing(self) -> LidarIntensityProcessing:
        """
        :type: LidarIntensityProcessing
        """
    @intensityProcessing.setter
    def intensityProcessing(self, arg0: LidarIntensityProcessing) -> None:
        pass
    @property
    def maxAzimuthROI(self) -> float:
        """
        :type: float
        """
    @maxAzimuthROI.setter
    def maxAzimuthROI(self, arg0: float) -> None:
        pass
    @property
    def maxReturns(self) -> int:
        """
        :type: int
        """
    @maxReturns.setter
    def maxReturns(self, arg0: int) -> None:
        pass
    @property
    def minAzimuthROI(self) -> float:
        """
        :type: float
        """
    @minAzimuthROI.setter
    def minAzimuthROI(self, arg0: float) -> None:
        pass
    @property
    def minDistBetweenEchos(self) -> float:
        """
        :type: float
        """
    @minDistBetweenEchos.setter
    def minDistBetweenEchos(self, arg0: float) -> None:
        pass
    @property
    def minReflectance(self) -> float:
        """
        :type: float
        """
    @minReflectance.setter
    def minReflectance(self, arg0: float) -> None:
        pass
    @property
    def minReflectanceRange(self) -> float:
        """
        :type: float
        """
    @minReflectanceRange.setter
    def minReflectanceRange(self, arg0: float) -> None:
        pass
    @property
    def nearRangeM(self) -> float:
        """
        :type: float
        """
    @nearRangeM.setter
    def nearRangeM(self, arg0: float) -> None:
        pass
    @property
    def numLines(self) -> int:
        """
        :type: int
        """
    @numLines.setter
    def numLines(self, arg0: int) -> None:
        pass
    @property
    def numberOfChannels(self) -> int:
        """
        :type: int
        """
    @numberOfChannels.setter
    def numberOfChannels(self, arg0: int) -> None:
        pass
    @property
    def numberOfEmitters(self) -> int:
        """
        :type: int
        """
    @numberOfEmitters.setter
    def numberOfEmitters(self, arg0: int) -> None:
        pass
    @property
    def pixelPitch(self) -> float:
        """
        :type: float
        """
    @pixelPitch.setter
    def pixelPitch(self, arg0: float) -> None:
        pass
    @property
    def pulseTimeNs(self) -> int:
        """
        :type: int
        """
    @pulseTimeNs.setter
    def pulseTimeNs(self, arg0: int) -> None:
        pass
    @property
    def quantumEfficiency(self) -> float:
        """
        :type: float
        """
    @quantumEfficiency.setter
    def quantumEfficiency(self, arg0: float) -> None:
        pass
    @property
    def rangeAccuracyM(self) -> float:
        """
        :type: float
        """
    @rangeAccuracyM.setter
    def rangeAccuracyM(self, arg0: float) -> None:
        pass
    @property
    def rangeCount(self) -> int:
        """
        :type: int
        """
    @rangeCount.setter
    def rangeCount(self, arg0: int) -> None:
        pass
    @property
    def rangeResolutionM(self) -> float:
        """
        :type: float
        """
    @rangeResolutionM.setter
    def rangeResolutionM(self, arg0: float) -> None:
        pass
    @property
    def rayFiringsParam(self) -> RayFiringsParam:
        """
        :type: RayFiringsParam
        """
    @rayFiringsParam.setter
    def rayFiringsParam(self, arg0: RayFiringsParam) -> None:
        pass
    @property
    def rayType(self) -> LidarRayType:
        """
        :type: LidarRayType
        """
    @rayType.setter
    def rayType(self, arg0: LidarRayType) -> None:
        pass
    @property
    def reflectionPowerFraction(self) -> float:
        """
        :type: float
        """
    @reflectionPowerFraction.setter
    def reflectionPowerFraction(self, arg0: float) -> None:
        pass
    @property
    def reportRateBaseHz(self) -> int:
        """
        :type: int
        """
    @reportRateBaseHz.setter
    def reportRateBaseHz(self, arg0: int) -> None:
        pass
    @property
    def scanRateBaseHz(self) -> int:
        """
        :type: int
        """
    @scanRateBaseHz.setter
    def scanRateBaseHz(self, arg0: int) -> None:
        pass
    @property
    def scanType(self) -> LidarScanType:
        """
        :type: LidarScanType
        """
    @scanType.setter
    def scanType(self, arg0: LidarScanType) -> None:
        pass
    @property
    def startAzimuthOffsetDeg(self) -> float:
        """
        :type: float
        """
    @startAzimuthOffsetDeg.setter
    def startAzimuthOffsetDeg(self, arg0: float) -> None:
        pass
    @property
    def stateResolutionStep(self) -> int:
        """
        :type: int
        """
    @stateResolutionStep.setter
    def stateResolutionStep(self, arg0: int) -> None:
        pass
    @property
    def transmissionPowerFraction(self) -> float:
        """
        :type: float
        """
    @transmissionPowerFraction.setter
    def transmissionPowerFraction(self, arg0: float) -> None:
        pass
    @property
    def validEndAzimuthDeg(self) -> float:
        """
        :type: float
        """
    @validEndAzimuthDeg.setter
    def validEndAzimuthDeg(self, arg0: float) -> None:
        pass
    @property
    def validStartAzimuthDeg(self) -> float:
        """
        :type: float
        """
    @validStartAzimuthDeg.setter
    def validStartAzimuthDeg(self, arg0: float) -> None:
        pass
    @property
    def weatherAtmosParam(self) -> AtmosProfileParam:
        """
        :type: AtmosProfileParam
        """
    @weatherAtmosParam.setter
    def weatherAtmosParam(self, arg0: AtmosProfileParam) -> None:
        pass
    pass
class LidarRayType():
    """
    Members:

      IDEALIZED

      GAUSSIAN_BEAM

      UNIFORM_BEAM
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
    GAUSSIAN_BEAM: omni.sensors.nv.lidar._lidar.LidarRayType # value = <LidarRayType.GAUSSIAN_BEAM: 1>
    IDEALIZED: omni.sensors.nv.lidar._lidar.LidarRayType # value = <LidarRayType.IDEALIZED: 0>
    UNIFORM_BEAM: omni.sensors.nv.lidar._lidar.LidarRayType # value = <LidarRayType.UNIFORM_BEAM: 2>
    __members__: dict # value = {'IDEALIZED': <LidarRayType.IDEALIZED: 0>, 'GAUSSIAN_BEAM': <LidarRayType.GAUSSIAN_BEAM: 1>, 'UNIFORM_BEAM': <LidarRayType.UNIFORM_BEAM: 2>}
    pass
class LidarScanType():
    """
    Members:

      kUnknown

      kRotary

      kLinear

      kSolidState

      kNum
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
    __members__: dict # value = {'kUnknown': <LidarScanType.kUnknown: 0>, 'kRotary': <LidarScanType.kRotary: 1>, 'kLinear': <LidarScanType.kLinear: 2>, 'kSolidState': <LidarScanType.kSolidState: 3>, 'kNum': <LidarScanType.kNum: 4>}
    kLinear: omni.sensors.nv.lidar._lidar.LidarScanType # value = <LidarScanType.kLinear: 2>
    kNum: omni.sensors.nv.lidar._lidar.LidarScanType # value = <LidarScanType.kNum: 4>
    kRotary: omni.sensors.nv.lidar._lidar.LidarScanType # value = <LidarScanType.kRotary: 1>
    kSolidState: omni.sensors.nv.lidar._lidar.LidarScanType # value = <LidarScanType.kSolidState: 3>
    kUnknown: omni.sensors.nv.lidar._lidar.LidarScanType # value = <LidarScanType.kUnknown: 0>
    pass
class Transformation():
    def __init__(self) -> None: ...
    @property
    def desiredCoordsType(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @desiredCoordsType.setter
    def desiredCoordsType(*args, **kwargs) -> None:
        pass
    @property
    def desiredFrameOfReference(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @desiredFrameOfReference.setter
    def desiredFrameOfReference(*args, **kwargs) -> None:
        pass
    @property
    def frameEnd(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @frameEnd.setter
    def frameEnd(*args, **kwargs) -> None:
        pass
    @property
    def frameStart(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @frameStart.setter
    def frameStart(*args, **kwargs) -> None:
        pass
    @property
    def interpolationFactor(self) -> float:
        """
        :type: float
        """
    @interpolationFactor.setter
    def interpolationFactor(self, arg0: float) -> None:
        pass
    @property
    def pose(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @pose.setter
    def pose(*args, **kwargs) -> None:
        pass
    pass
def acquire_pcconverter_interface(plugin_name: str = None, library_path: str = None) -> ILidarPCConverterFactory:
    pass
def computeEmitterPeakPower(arg0: LidarProfile, arg1: int, arg2: int) -> float:
    pass
def getChannelsOfBinFileHeader(arg0: str) -> typing.Dict[int, typing.List[float]]:
    pass
def getConstDetector(arg0: LidarProfile) -> float:
    pass
def getLidarBinFileHeader(*args, **kwargs) -> typing.Any:
    """
    Get lidar bin file header with filled beam angles.
    """
def getLidarProfileFromBuffer(arg0: buffer) -> LidarProfile:
    """
    Get lidar profile casted from binary buffer.
    """
def getParameterString(arg0: buffer) -> str:
    """
    Get parameter string of LidarBinFileHeader.
    """
def getSizeOfBinPacketHeader() -> int:
    """
    Get size of DwBinPacketHeader.
    """
def getSizeOfLidarBinFileHeader() -> int:
    """
    Get size of LidarBinFileHeader.
    """
def propagateSimple(arg0: float, arg1: float, arg2: float, arg3: float, arg4: BeamProfile) -> float:
    pass
def release_pcconverter_interface(arg0: ILidarPCConverterFactory) -> None:
    pass
