// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/Interface.h>

#include <omni/fabric/core/API.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/core/Ordered_Set.h>

#include <stdint.h>

namespace omni
{
namespace fabric
{

/**
 * @brief Legacy support for Fabric metadata
 *
 * Fabric doesn't need all metadata in UsdAttribute, just the attribute's
 * type, size in bytes, whether it is an array, and if it is an array, the
 * size of each elements in bytes
 *
 * @todo This only exists for legacy support.  Once getTypeInfo is officially removed
 * this can be removed as well. See OM-86447
 */
struct Typeinfo
{
    size_t size; //!< Size of the object being stored
    bool isArray; //!< True if the object is an array type
    size_t arrayElemSize; //!< If an array type, holds the size of a single array element, else 0
};

struct IFabric
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IFabric", 0, 9);

    FabricId(CARB_ABI* createFabricCache)(FabricOptions options);

    // TODO: Enable this is a follow on MR
    // CARB_DEPRECATED("This call has been replaced by release")
    void(CARB_ABI* destroyFabricCache)(FabricId fabricId);

    uint64_t(CARB_ABI* serializeFabricCache)(FabricId fabricId, uint8_t* dest, size_t destSize);
    bool(CARB_ABI* deserializeFabricCache)(FabricId fabricId,
                                           const uint8_t* input,
                                           const size_t inputSize,
                                           bool skipConfirmation);

    bool(CARB_ABI* writeFabricCacheToDisk)(
        FabricId fabricId, const char* file, uint8_t* workingBuffer, size_t workingBufferSize, uint64_t* bytesWritten);
    bool(CARB_ABI* readFabricCacheFromDisk)(
        FabricId fabricId, const char* fileName, uint8_t* workingBuffer, size_t workingBufferSize, uint64_t* bytesRead);

    // TODO: Delete this for OM-86447
    CARB_DEPRECATED("Typeinfo is deprecated. Type now carries all relevant data")
    Typeinfo(CARB_ABI* getTypeInfo)(FabricId fabricId, TypeC type);

    // TODO: Delete this for OM-86447
    CARB_DEPRECATED("Typeinfo is deprecated. Type now carries all relevant data")
    void(CARB_ABI* addType)(FabricId fabricId, TypeC type, Typeinfo info);

    // TODO: Enable this is a follow on MR
    // CARB_DEPRECATED("This call has been replaced by cloneFabricCache")
    void(CARB_ABI* copyFabricCache)(FabricId srcFabricId, FabricId dstFabricId);

    void(CARB_ABI* enableGpuCompute)(GpuComputeType type);

    void(CARB_ABI* clearFabricCacheData)(FabricId fabricId);

    // TODO: Delete this for OM-86447
    CARB_DEPRECATED("Typeinfo is deprecated. Type now carries all relevant data")
    void(CARB_ABI* clearFabricCacheTypeInfo)(FabricId fabricId);

    /** @brief check if a fabric ID is valid
     *
     * @fabricId[in] the fabric id to check
     *
     * returns true if valid, false otherwise
     */
    bool(CARB_ABI* isFabricIdValid)(FabricId fabricId);

    // TODO: Delete this for OM-86447
    CARB_DEPRECATED("Typeinfo is deprecated. Type now carries all relevant data")
    bool(CARB_ABI* setTypeinfo)(FabricId fabricId, TypeC type, Typeinfo info);
    
    /** Removes all data from the Fabric string directory
     *
     */
    void(CARB_ABI* clearObjectDirectory)(FabricId fabricId);

    FABRIC_ABI_DUMMY(1)
    FABRIC_ABI_DUMMY(2)
    FABRIC_ABI_DUMMY(3)
    FABRIC_ABI_DUMMY(4)
    FABRIC_ABI_DUMMY(5)
    FABRIC_ABI_DUMMY(6)

    void(CARB_ABI* configureSerialization)(FabricId fabricId, SerializationOption option);

    void(CARB_ABI* setFabricDebugName)(FabricId fabricId, const char* name);
    const char*(CARB_ABI* getFabricDebugName)(FabricId fabricId);

    bool(CARB_ABI* cloneFabricCache)(FabricId srcFabricId, FabricId dstFabricId);

    bool(CARB_ABI* appendFabricCache)(FabricId srcFabricId, FabricId dstFabricId, Span<FabricCopyFilter> filters);
    bool(CARB_ABI* appendFabricCaches)(Span<FabricId> srcFabricsIds,
                                       FabricId dstFabricId,
                                       Span<FabricCopyFilter> filters);

    bool(CARB_ABI* copyOrMergeFabricCache)(FabricId srcFabricId,
                                           FabricId dstFabricId,
                                           Span<FabricCopyFilter> filters,
                                           bool overwritePrims,
                                           bool createNewPrims);
    bool(CARB_ABI* copyOrMergeFabricCaches)(Span<FabricId> srcFabricIds,
                                            FabricId dstFabricId,
                                            Span<FabricCopyFilter> filters,
                                            bool overwritePrims,
                                            bool createNewPrims);

    bool(CARB_ABI* moveFabricCache)(FabricId srcFabricId,
                                    FabricId dstFabricId,
                                    Span<FabricCopyFilter> filters,
                                    bool overwritePrims,
                                    bool createNewPrims);

    /**
     * @brief Create a listener
     * This just creates a listener ID, you have to attach it to a stage to use it.
     * Note that there is no destroyListener method. To stop using an ID, detach it from all stages it is attached to.
     * @return The listenerId
     *
     * // TODO: This shouldn't be on IFabric... This should be on something like the IChangeTracking api
     */
    CARB_DEPRECATED("Use the create listener call on IChangeTracker instead.")
    ListenerId(CARB_ABI* createListener)();

    void(CARB_ABI* addRef)(FabricId id);
    void(CARB_ABI* release)(FabricId id);

    uint64_t(CARB_ABI* serializeFabricCacheFromRevision)(FabricId fabricId, uint8_t* dest, size_t destSize, uint64_t fromRevision);
    uint64_t(CARB_ABI* getObjectDirectoryCurrentRevision)(FabricId fabricId);
    /**
     * @brief Retrieves the current revision of the fabric cache serialization code. A cache serialized with a different revision
     * cannot be deserialized successfully.
     */
    uint64_t(CARB_ABI* getFabricCacheSerializationCurrentRevision)();

    /**
     * * @brief Copy data between fabric caches via bucket copying. Note, buckets with mismatched or duplicated paths in
     * the dest fabric cache are skipped. Connectivity of all the copied buckets in the dest are reset. It expects the
     * API caller to re-establish.
     *
     * @param[in] srcFabricId The id of the source fabric cache.
     * @param[in] dstFabricId The id of the destination fabric cache.
     * @param[in] filter The filter to select the buckets and attributes to be copied.
     * @returns true If all the buckets designated by the filter are copied, false if no buckets copied or there is any
     * bucket skipped due to duplicated paths.
     */
    bool(CARB_ABI* copyFabricCacheBuckets)(FabricId srcFabricId,
                                           FabricId dstFabricId,
                                           FabricCopyFilter filter);

    uint64_t (CARB_ABI* getTopologyVersion)(FabricId fabricId);
};

} // namespace fabric
} // namespace omni
