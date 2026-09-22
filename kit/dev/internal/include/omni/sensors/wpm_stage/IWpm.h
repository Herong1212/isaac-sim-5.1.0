// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

/**
 * @brief WPM (wave propagation model) interface.
 * @note all units follow standard metric system except when otherwise specified in a member name (ex: timeNs will
 * indicate time in nano seconds instead of standard seconds)
 *
 */

#pragma once

#define RTXSENSOR_MODEL_V20
#include <rtx/rtsensor/RtxSensorModel.h>

//! @file
//!
//! @brief WPM (wave propagation model) API

#include <carb/IObject.h>

#include <omni/sensors/materials/MaterialManager.h>

#include <cstdint>

// Forward declaration of external needed types
struct float3;
struct float4;

// Short hand for RtxSensor types namespace
namespace rts = rtx::rtxsensor;

namespace omni
{
namespace sensors
{
namespace wpm
{

/** @brief cuda stream type can be mapped directly to cudaStream_t */
using WpmCudaStream_t = void*;

/** @brief type for custom ray properties */
using CustomRayProps = void;


/*************************************************************************
 * Config that needs to be set once
 * **********************************************************************/

/**
 * @brief Global Wpm config that needs to be set only once at Init and can't change after
 *
 */
struct Config
{
    /** @brief max depth of the ray tracing tree (defines number of bounces) */
    uint8_t maxTraceTreeDepth;

    /** @brief max number of possible transmitters */
    uint32_t maxNumTransmitters;

    /** @brief max number of possible receivers */
    uint32_t maxNumReceivers;

    /** @brief max number of ray patterns */
    uint8_t maxNumRayPatterns;

    /** @brief max number of rays in any ray pattern */
    uint32_t maxNumRaysPerPattern;

    /** @brief max number of possible detector patterns */
    uint8_t maxNumDetPatterns;

    /** @brief max number of detectors in any detector pattern */
    uint32_t maxNumDetsPerPattern;

    /** @brief max number of target detector groups per receiver */
    uint32_t maxNumTarDetGroupsPerRx;

    /** @brief max numbers of detector indices per any target detector group */
    uint8_t maxNumIdxsPerTarDetGroup;

    /** @brief size of the CustomRayProps blob */
    size_t customRayPropsSize;

    /** @brief determines if transmitters definition should be on host */
    bool isTransmittersOnHost;

    /** @brief determines if receivers definition should be on host */
    bool isReceiversOnHost;

    /** @brief determines if detectors definition should be on host */
    bool isDetectorsOnHost;

    /** @brief enables generation of transmission rays (not yet supported) */
    bool enTransmission;

    /** @brief enables using backscatter from reflection ray in a bounce contribution (not yet supported) */
    bool enBackscatterFromR;

    /** @brief enables using backscatter from transmission ray in a bounce contribution (not yet supported) */
    bool enBackscatterFromT;

    /** @brief enables calculating round trip path velocity in contributions */
    bool enRtVelocity;

    /** @brief enables availability of hit point geometry information */
    bool enHitGeometry;

    /** @brief minimum distance to accept ray hit [m] */
    float minHitDistanceM = 0.005f;

    /** @brief minimum distance to accept ray hit for primary rays [m] */
    float minPrimaryHitDistanceM = 0.005f;

    /** @brief maximum distance after which ray hit search terminates [m] */
    float maxHitDistanceM = 1000.0f;

    /** @brief lobewidth of source beam */
    float sourceDivergence = 0.0f;
};


/*************************************************************************
 * Trace definition that can be modified with each new trace
 * **********************************************************************/

/** @brief a struct the defines a frame of reference */
struct Frame
{
    float3 p; /**< position vector */
    float4 q; /**< orientation quaternion */
};

/** @brief a struct the defines a frame of reference */
struct Frames
{
    float3* p; /**< position vector */
    float4* q; /**< orientation quaternion */
};

/** @brief a struct the defines motion of a frame of reference */
struct FrameMotion
{
    Frame start; /**< position and orientation at frame motion start */
    uint64_t startTimeNs; /**< time in nano secs at frame motion start */

    Frame end; /**< position and orientation at frame motion end */
    uint64_t endTimeNs; /**< time in nano secs at frame motion end */

    float3 velocity; /**< world linear velocity vector */
    float3 localAngVelocity; /**< local angular velocity vector */
};

/** @brief a struct that defines a Ray */
struct Rays
{
    uint64_t* deltaTimeNs; /**< delta time in nano secs from parent transmitter */
    float3* origin; /**< vector defining origin point of the ray relative to transmitter frame */
    float3* direction; /**< unit vector defining ray direction relative to transmitter frame */

    uint32_t* targetDetGroupIdxInRx; /**< idx of target detectors group in corresponding receiver */
};

/** @brief a struct that defines a transmitter */
struct Transmitters
{
    uint64_t* deltaTimeNs; /**< delta time in nano secs from frame start time */
    Frames frames; /**< a frame of reference defining the pose of the transmitter relative to the sensor frame */
    uint8_t* rayPatternIdx; /**< idx of ray pattern transmitted by transmitter */
    uint32_t* targetRxIdx; /**< target corresponding receiver to transmitter */
};

/** @brief a struct that defines a detector */
struct Detectors
{
    float3* origin; /**< vector defining origin point of the detector relative to receiver frame */
    float4* quat; /**< quaternion defining detector orientation relative to receiver frame */
};

/** @brief a struct that defines a receiver */
struct Receivers
{
    Frames frames; /**< a frame of reference defining the pose of the receiver relative to the sensor frame */
    uint8_t* detPatternIdx; /**< idx of detectors pattern in receiver */
};

/**
 * @brief a struct defining a trace, the trace definition struct can be obtained from the wpm object with the API
 * getTraceDefinition() and can be changed in runtime, changes will only take effect at the start of a new trace
 *
 * @note the wpm manages the memory allocation of trace definition members, and the user has some control on this with
 * allocation flags in the config struct (ex: isTransmittersOnHost ... etc), this is to ease usage depending on the size
 * of the entities being defined (transmitters, receivers, ... etc). if the setCudaDevice() API is not called the wpm
 * will assume pure CPU mode and all memory will be allocated on host, otherwise GPU mode and allocation flags will be
 * respected
 *
 */
struct TraceDefinition
{
    /** @brief cudaStream for the current run, not used in case of CPU mode */
    WpmCudaStream_t cudaStream{ 0 };

    /** @brief defines the depth of the trace tree, related to expected num bounces/returns per ray */
    int8_t traceTreeDepth{ 0 };

    /** @brief sensor frame motion throughout the whole trace */
    FrameMotion frameMotion;

    /** @brief 1 dimensional array of transmitter definitions, transmitters1D can be on host if flag
     * (isTransmittersOnHost) is true otherwise on device  */
    Transmitters transmitters1D;

    /** @brief number of transmitters */
    uint32_t numTransmitters{ 0 };

    /** @brief 1 dimensional array of receiver definitions, receivers1D can be on host if flag (isReceiversOnHost) is
     * true otherwise on device  */
    Receivers receivers1D;

    /** @brief number of receivers */
    uint32_t numReceivers{ 0 };

    /** @brief 2 dimensional array of ray definitions linearized in row major, rows represent patterns, columns
     * represent rays within a pattern [pattern1(ray1+ray2+...)+pattern2(...)+...], rays2D is always on device */
    Rays rays2D;

    /** @brief 2 dimensional array of custom ray properties linearized in row major, rows represent patterns, columns
     * represent rays within a pattern [pattern1(rayProps1+rayProps2+...)+pattern2(...)+...], rayProps2D is always on
     * device */
    CustomRayProps* rayProps2D{ nullptr };

    /** @brief 1 dimensional array same size as ray patterns, each element specifies the number of rays in the
     * corresponding pattern, numRaysPerPattern1D is always on device */
    uint32_t* numRaysPerPattern1D{ nullptr };

    /** @brief number of ray patterns */
    uint8_t numRayPatterns{ 0 };

    /** @brief 2 dimensional array of detector definitions linearized in row major, rows represent patterns, columns
     * represent detectors within a pattern [pattern1(det1+det2+...)+pattern2(...)+...], detectors2D can be on host if
     * flag (isDetectorsOnHost) is true otherwise on device */
    Detectors detectors2D;

    /** @brief 1 dimensional array same size as detector patterns, each element specifies the number of detectors in the
     * corresponding pattern, numDetsPerPattern1D can be on host if flag (isDetectorsOnHost) is true otherwise on device
     */
    uint32_t* numDetsPerPattern1D{ nullptr };

    /** @brief number of detector patterns */
    uint8_t numDetPatterns{ 0 };

    /** @brief 3 dimensional array of target detector indicies linearized major to minor as (z->y->x), z represents
     * receivers, y represents detector groups, x represents detector indices
     * [receiver1(group1(detIdx1+detIdx2+detIdx3+...)+group2(...)+...)+receiver2(...)+...], targetDetIdxs3D can be on
     * host if both flags (isReceiversOnHost & isDetectorsOnHost) are true otherwise on device */
    uint32_t* targetDetIdxs3D{ nullptr };

    /** @brief 2 dimensional array of numIndicies linearized in row major, rows represent receivers, columns
     * represent num indicies per group within a receiver
     * [receiver1(NumIdxsPergroup1+NumIdxsPergroup2+...)+receiver2(...)+...], numIdxsPerGroup2D can be on host if both
     * flags (isReceiversOnHost & isDetectorsOnHost) are true otherwise on device */
    uint8_t* numIdxsPerGroup2D{ nullptr };
};

/*************************************************************************
 * Output (trace results) data types
 * **********************************************************************/

/**
 * @brief a struct that contains a single contribution form a ray bounce in the scene to a detector, each bounce can
 * contribute up to 3 contributions to a detector:
 * I contribution = backscatter from the incidence ray
 * R contribution = backscatter from reflected ray backscatter
 * T contribution = backscatter from transmitted ray backscatter
 *
 * R and T contributions can be enabled/disabled using the flags (enBackscatterFromR, enBackscatterFromT) in config
 *
 * @note this struct only defines the standard WPM properties inside a contribution, in addition to that, each
 * contribution also has a custom ray properties associated with it this can be extracted from rayProps4D
 *
 */
struct Contributions
{
    bool* isValid; /**< if true, means this contribution is valid to be used otherwise, shouldn't be used */
    uint8_t* numBounces; /**< total num bounces throughout the contribution path */
    float* rtDistance; /**< total roundtrip distance (total contribution path length) */
    float* rtVelocity; /**< total roundtrip velocity (total contribution path length change) */
    float3* pos; /**< contribution position in detector frame */
    float3* vertices; /**< vertex positions for the hit triangle in detector frame (float3 array with stride of 3)*/
    uint64_t* deltaTimeNs; /**< contribution delta time in nsec from startframe */
    uint32_t* materialId; /**< contribution materialId */
    float* cosAngle; /**< incident normal dot prod for contribution */
    float* accumBeamRangeDivergence; /**< accumulated divergence with range of the beam for this contribution */
};

/**
 * @brief a struct that holds all results from a trace (all contributions from all bounces for all detectors inside all
 * receivers)
 * @note all arrays are on device, except if in pure CPU mode (i.e. setCudaDevice() API was never called)
 *
 */
struct TraceResult
{
    /** @brief 4 dimensional array of standard contributions linearized major to minor as (w->z->y->x), w represents
     * receivers, z represents detectors per receiver, y represents bounces per detector, x represents contributions per
     * bounce
     * [receiver1(detecor1(Bounce1(contribution_I+contribution_R+contribution_T)+Bounce2(...)+...)+detector2()+...)
     * + receiver2(...)+....] */
    Contributions contributions4D;

    /** @brief 4 dimensional array of custom rayProps linearized major to minor as (w->z->y->x), w represents
     * receivers, z represents detectors per receiver, y represents bounces per detector, x represents rayProps per
     * bounce [receiver1(detecor1(Bounce1(rayProps_I+rayProps_R+rayProps_T)+Bounce2(...)+...)+detector2()+...)
     * + receiver2(...)+....] */
    CustomRayProps* rayProps4D{ nullptr };

    /** @brief max number of detectors per receiver as convenience for acessing results in aforementioned 4D arrays (z
     * size) */
    uint32_t maxNumDetectorsPerRx;

    /** @brief max number of bounces per detector as convenience for acessing results in aforementioned 4D arrays (y
     * size) */
    uint32_t maxNumBouncesPerDetector;

    /** @brief max number of contributions per bounce as convenience for acessing results in aforementioned 4D arrays (x
     * size)
     * @note this can be 1, 2, or 3 based on the use of the flags (enBackscatterFromR, enBackscatterFromT)
     */
    uint8_t maxNumContributionsPerBounce;
};

/**
 * @brief Main wave propagation model interface, users can create objects that implement this interface by acquiring the
 * IWpmFactory carbonite interface and using the createInstance() method. eventhough it is not foreseen as need, it
 * is possible for each sensor model to own multiple wave propagation model objects that are configured differently and
 * to alternate using them. it is worth noting that a wpm object is heavy can have a heavy footprint on GPU resources,
 * thus it is adviced to use wpm objects sparingly
 *
 */
class IWpm : public carb::IObject
{
public:
    virtual ~IWpm(){};

    /*************************************************************************
     * Init interfaces
     * - normally used on init and maybe upon device migration
     * **********************************************************************/

    /**
     * @brief Sets the Cuda Device to be used, if no cuda device is set the wpm
     * will assume cpu mode and all memory will be allocated on host
     *
     * @param cudaDevice cuda device to use
     */
    virtual void setCudaDevice(int32_t cudaDevice) = 0;

    /**
     * @brief Gets the Trace Definition object, the user needs to pass a valid config
     * object to get a valid trace definition object otherwise a null pointer is returned.
     * users can modify the trace definition in runtime, changes will only take effect on
     * a new trace cycle
     *
     * @param cfg configuration object for the wpm
     * @param randState configuration to include random states for material interactions
     * @return TraceDefinition* pointer to trace definition object when successfull, otherwise a nullptr
     */
    virtual TraceDefinition* getTraceDefinition(const Config& cfg, const bool randState = true) = 0;

    /**
     * @brief sets up a material map, with this interface the user can map specific RtxSensor MaterialIds, to
     * specific material names. all exisiting enabled material plugins will be searched and the material with same
     * name will be used. in case users are providing own material plugins they are encouraged to use unique names
     * because name collisions can occur (first material with matching name will be used)
     *
     * @param materialMap material map, maps RtxSensor Material Ids, material descriptors
     * @param reset reset material map to reprocess materials
     * @param update update material map for existing materials
     * @return true if setting up materials succeeds
     * @return false if setting up materials fails
     */
    virtual bool setupMaterials(const omni::sensors::materials::MaterialMap& materialMap, bool reset = false, bool update = false) = 0;

    /*************************************************************************
     * Runnable interfaces
     * - used cyclically within a trace to cover batches of work
     * fillFirings()->setReturns()->fillFirings()->setReturns()-> ... etc
     * - Note: the user can find out how many batches are needed using
     * utilGetNumBatches(), if the APIs are called more than needed they will
     * boil down to a no-op in the extra calls.
     * **********************************************************************/

    /**
     * @brief fills the RtxSensor firings for the user. the wpm has an internal state and will fill the firings
     * based on the current batch of work. the trace definition specifies the full trace tree depth, and thus the
     * number of batches and the amount of work. this API will normally be called within the batchBegin(...) from
     * RtxSensor API
     *
     * @param firings an array of RtxSensor firings to be filled by the wpm
     */
    virtual void fillFirings(rts::RtxSensorFiring* firings) = 0;

    /**
     * @brief sets in the wpm the results of tracing the previous firings. wpm uses the results to
     * calculate the next needed amount of work
     *
     * @param returns and array of RtxSensor returns containing the results of tracing the previous firings
     */
    virtual void setReturns(rts::RtxSensorReturn* returns) = 0;

    /*************************************************************************
     * Result interfaces
     * - used to get the result from a trace
     * **********************************************************************/

    /**
     * @brief Get the Trace Result object
     * @note using this API at the end of a trace is mandatory to indicate to the wpm the start of a new trace
     *
     * @return TraceResult* pointer to and object that has trace results.
     */
    virtual TraceResult* getTraceResult() = 0;
};

/**
 * @brief a carb object pointer for an object that implements the IWpm interface
 *
 */
using IWpmPtr = carb::ObjectPtr<IWpm>;

} // namespace wpm
} // namespace sensors
} // namespace omni
