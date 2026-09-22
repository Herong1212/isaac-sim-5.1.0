// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <GenericModelOutputTypes.h>
#include <cstdint>
#include <vector>


//-----------------------------------------------------------------------------
constexpr float LIDAR_ROT_START = 0.f; /**< globally defined start azimuth */
constexpr float LIDAR_ROT_END = 360.f; /**< globally defined end azimuth */


/**
 * Mapping Type
 */
enum LidarIntensityMapping
{
    LINEAR = 0, /**< only scaling will be applied*/
    NONLINEAR = 1, /**< nonlinear mapping of intensities based on provided quantized intensity mapping. Additionally,
                      there is one special cases: An inverted 1:1 decoder map (map elements == scaling factor) will be
                      used as an encoder map*/
    NONLINEAR_ENCODING_ONLY = 2,
    NONLINEAR_DECODING_ONLY = 3
};

/**
 * Rotation Type
 */
enum LidarRotationDirection
{
    CW = 0, /**< clock wise*/
    CCW = 1 /**< counter clock wise*/
};


/**
 * Specifies ray type of lidar simulation
 */
enum LidarRayType
{
    IDEALIZED = 0, /**< emitter is modeled as an idealized ray */
    GAUSSIAN_BEAM = 1, /**< emitter is simulated as an gaussian beam */
    UNIFORM_BEAM = 2 /**< emitter is simulated as a uniform beam */
};


/**
 * Specifies the scanning principle of the simulated lidar
 */
enum class LidarScanType : uint8_t
{
    kUnknown, /**< unknown principle, result of incorrect reading of profile */
    kRotary, /**< rotating sensors */
    kLinear, /**< linear principle */
    kSolidState, /**< solid state sensors including flash lidar */
    kNum /**< indicator for number of elements in the enum */
};

/**
 * Specifies the intensity correction method
 */
enum class LidarIntensityProcessing : uint8_t
{
    kCorrection, /**< simple correction method which removes the distance factor */
    kRaw, /**< no correction, raw intensity output scaled to fit */
    kNormalization, /**< normalized intensity output (not supported, yet) */
    kCalibrated, /**< close to true reflectance output, rigorous radimetric correction and calibration applied. (not
                    supported, yet) */
    kPointType, /**< inferred hit point type (not supported, yet) */
    kNum /**< indicator for number of elements in the enum */
};

struct EmitterProfileSoA
{
    // Arrays are of size emitterStatesCount*numberOfEmitters
    float* azimuthDeg{ nullptr }; /**< azimuth deviation in degrees */
    float* elevationDeg{ nullptr }; /**< elevation deviation in degrees */
    float* vertOffsetM{ nullptr }; /**< vertical offset of the emitter origin in m */
    float* horOffsetM{ nullptr }; /**< horizontal offset of the emitter origin in m */

    float* distanceCorrectionM{ nullptr }; /**< distance offset to sensor origin in m */
    float* focalDistM{ nullptr }; /**< focal distance in m */
    float* focalSlope{ nullptr }; /**< focal slope in m */

    uint32_t* fireTimeNs{ nullptr }; /**< firing time of emitter (delta to tick start time) in ns */
    uint32_t* reportRateDiv{ nullptr }; /**< report rate divisor */
    uint32_t* bank{ nullptr }; /**< beam bank */
    uint32_t* channelId{ nullptr }; /**< channel of beam */
    uint32_t* rangeId{ nullptr }; /**< emitter range id */

    // Emitter State Count Size
    bool* isROIState{ nullptr }; /** is State a ROI state? */
    // Maybe not filled
    // rangeCount size
    float* minRange{ nullptr };
    float* maxRange{ nullptr };
    // Size: numLines size
    uint16_t* numRaysPerLine{ nullptr };
    bool* isROI{ nullptr }; /**< not all emiters are valid in roi */
};

struct IntensityMappingParam
{
    LidarIntensityMapping type; /**< specifies intensity mapping type */
    float intensityScalePercent; /**< max intensity value in % */
    uint32_t elCountEnc; /**< number of elements in encoding */
    uint32_t elCountDec; /**< number of elements in decoding */
    float* encoding; /**< intensity encoding */
    float* decoding; /**< intensity decoding */
};

/**
 * Error profile for the sensor azimuth position
 */
struct ErrorProfile
{
    float std;
    float mean;
};

struct EmitterError
{
    ErrorProfile azimuth; /**< jitter for azimuth */
    ErrorProfile elevation; /**< jitter for elevation */
    ErrorProfile origin[3]; /**< jitter for origin (x,y,z) -- simulate small vibrations */
};

struct AtmosProfileParam
{
    float rainRate{ 0.f }; // in mm/h  -- base parameter for atmospherics
    float rainDropHitThresh{ 0.f }; // min thresh for backscatter based random drop hit
    float alpha{ 0.f }; // alpha parameter of beta distribution
    float beta{ 0.f }; // beta parameter of beta distribution
};

struct AerosolAtmosProfileParam
{
    float aerosolModel{ -1.f }; // specifies the atmospheric model ranging from continental, rural, marine, and urban
};

struct RayFiringsParam
{
    float rangeOffset{ 0.f }; // Specifies an offset for each primary ray firing
    bool cullBackFace{ false }; // cull back facing primitives parameter
};

/**
 * BeamProfile, used for beam divergence
 */
struct BeamProfile
{
    float wavelengthNm; /**< wavelength of laser */
    float beamWaistHorM; /**< beam radius at waist */
    float beamWaistVertM; /**< beam radius at waist */
    float Msquared; /**< beam quality */
    float focusDistM; /**< Focusing distance in m, distance to beam waist */

    float divHorRad{ 0.f }; /**< beam divergence in rad, optional, if not provided, will be calculated for Gaussian
                                   beam from M2 and w0 */
    float divVertRad{ 0.f }; /**< beam divergence in rad, optional, if not provided, will be calculated for Gaussian
                                   beam from M2 and w0 */
    float aspectRatio{ 1.f }; /**< beam footprint aspect ratio, optional */
};

// DOXYGEN needs a namespace in order to handle the LidarProfile structs // still needed?
#ifdef DOXYGEN_BUILD
namespace
{
#endif
/**
 * LidarBaseProfile, common for all types of lidar
 */
struct LidarProfile
{
    LidarScanType scanType; /**< specifies the scanning principle of the simulated lidar */
    LidarRotationDirection rotationDirection; /**< specifies the rotation direction of the sensor */
    LidarIntensityProcessing intensityProcessing; /**< specifies the intensity correction method */
    LidarRayType rayType; /**< specifies the modeled ray type */

    uint32_t dwId; /**< DriveWorks id  */

    float nearRangeM; /**< minimum distance of sensor in m */
    float farRangeM; /**< maximum distance of sensor in m */
    float validStartAzimuthDeg; /**< start azimuth in deg for capped sensor fov */
    float validEndAzimuthDeg; /**< end azimuth in deg for capped sensor fov */
    bool validAzimuthTickBased;
    uint8_t padding[7];
    float startAzimuthOffsetDeg; /**< offset of sensor internal start azimuth to kit coordinates*/

    // foveal ROI
    float minAzimuthROI;
    float maxAzimuthROI;

    float effectiveApertureSize; /**< effective aperture size of collector in meters */
    float quantumEfficiency; /**< quantum efficiency of the detector */
    float calibrationGain; /**< gain factor that accounts for intensity calibration */
    float pixelPitch; /**< size of single detector element in microns */
    float bitDepthResolution; /**< bit depth quantization from detector */
    float reflectionPowerFraction; /**< reflection power fraction for secondary returns */
    float transmissionPowerFraction; /**< transmission power fraction for secondary returns */

    float rangeResolutionM; /**< range resolution in m */
    float rangeAccuracyM; /**< range accuracy in m */

    uint32_t rangeCount; /**< number of different emitter ranges */
    float avgPowerW; /**< average power of laser in W */
    float minReflectance; /**< minimum reflectance at a specified range */
    float minReflectanceRange; /**< specified range with min reflectance */
    float minDistBetweenEchos; /**< min distance between succeeding echos */
    uint32_t pulseTimeNs; /**< laser pulse time in ns */

    BeamProfile beamProfile; /**< beam profile */

    uint32_t maxReturns; /**< maximum number of returns/echos per laser emitter */

    uint32_t scanRateBaseHz; /**< base scan rate which is the default */
    uint32_t reportRateBaseHz; /**< base frequency of one shooting of all lasers */

    // Multiple emitter can map to same channel.
    uint32_t numberOfChannels; /**< number of channels = detectors per tick/sensor position */
    uint32_t numberOfEmitters; /**< number of emitters per tick/sensor position */

    uint32_t stateResolutionStep; /**< step size between different emitter states */
    uint32_t emitterStateCount; /**< number of different emitter states */

    EmitterError emitterError; /**< error parameter for emitter */
    AtmosProfileParam weatherAtmosParam; /**< weather parameter */
    AerosolAtmosProfileParam aerosolAtmosParam; /**< aerosol parameter */
    RayFiringsParam rayFiringsParam; /**< specifies the ray firing control params */
    uint16_t numLines; /**< number of azimuth lines per full scan */
    omni::sensors::AuxType auxOutputType;
    bool enableSorting;
    uint8_t padding2[3];
    omni::sensors::FrameOfReference outFrameOfReference;
    omni::sensors::MotionCompensationState outMotionCompensationState;
    omni::sensors::CoordsType elementsCoordsType;
    float customOutPos[3];
    float customOutOrientation[4];
    // EmitterProfiles in SoA
    IntensityMappingParam intensityMapping;
    EmitterProfileSoA emitterProfileSoA;
};


#ifdef DOXYGEN_BUILD
}
#endif
