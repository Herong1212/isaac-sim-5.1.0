// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/interface/IFabric.h>

#include <memory>
#include <carb/cpp/StringView.h>

namespace omni
{
namespace fabric
{

class Fabric
{
    FabricId m_id;
    IFabric* m_interface;

public:

    /** Construct a new fabric cache. When last referencing object is freed cache will be freed.
     *
     * @param[in] opt The fabric options to use for construction
     *
     */
    Fabric(FabricOptions opt = FabricOptions::eDefault);

    Fabric(const Fabric& other);
    Fabric& operator=(const Fabric& other);

    Fabric(Fabric&& other);
    Fabric& operator=(Fabric&& other);

    ~Fabric();

    /** Write a Fabric file to disk at a specified location

     * @param[in] file The location the file is desired to be written to
     *
     * @param[in] workingBuffer An optional buffer of working memory to avoid allocation. Must be large enough to hold
     * the entire operation or else memory will be allocated internally
     *
     * @param[out] bytesWritten The number of bytes written if successful or the number of bytes required otherwise.
     * @return success
     *
     */
    bool writeToDisk(carb::cpp::string_view file, std::vector<uint8_t>& workingBuffer, uint64_t& bytesWritten);

    /** Read a Fabric file from the specified location
     *
     * @param[in] file The location the file is desired to be read from
     *
     * @param[in] workingBuffer An optional buffer of working memory to avoid allocation. Must be large enough to hold
     * the entire operation or else memory will be allocated internally
     *
     * @param[out] bytesRead The number of bytes read if successful or the number of bytes required otherwise.
     *
     * @return success
     *
     */
    bool readFromDisk(carb::cpp::string_view file, std::vector<uint8_t>& workingBuffer, uint64_t& bytesRead);

    /** Enable a gpu compute engine on fabric.  Can only be enabled as all fabrics share an underlying platform
     *
     * @param[in] type The type of compute engine
     *
     */
    void enableGpuCompute(GpuComputeType type);

    /** Removes all data from the Fabric
     *
     */
    void clearData();

    /** Configures the serialization process of a Fabric cache on a few options
     *
     * @param[in] option The option to consider
     *
     */
    void configureSerialization(SerializationOption option);

    /** Attempt to serialize the fabric into the specified buffer.
     *
     * @param[inout] dest A span pointing to the target memory location for write. Will write up to dest.size() bytes.
     *
     * @return Number of bytes written success is determined by (return <= @destize)
     *
     * @invariant It is safe to write to any memory within[dest, dest+size] for the
     *            duration of the function call.
     *
     * @note If the Fabric will not fit into the size of memory allocated in
     *       @dest then it will stop writing, but continue to run the serialize
     *       algorithm to calculate the actual amount of data that needs to be
     *       written
     *
     */
    uint64_t serialize(Span<uint8_t> dest);

    /** Given a buffer that has the serialized version of a Fabric written
     *         using the serialize function, this function will override all the data
     *         in the Fabric with the data from the buffer
     *
     * @param[in] input A span pointing to the input to deserialize.
     * @param[in] skipConfirmation Whether we should skip making sure the destination fabric exists
     * @return True if buffer was successfully de-serialized
     *
     * @note This currently has to clear the Fabric before it is populated which is a possibly
     *         expensive operation
     *
     */
    bool deserialize(const Span<uint8_t> input, bool skipConfirmation);

    /** Sets the name of a fabric cache
     *
     * @param[in] name The name to use - note that for safety, non-displayable characters including % will be replaced
     * with underscores
     *
     */
    void setDebugName(carb::cpp::string_view name);

    /** Get the name of a fabric cache at this current moment in time.
     *
     * @return The debug name if set. Empty string if not.
     *
     */
    std::string getDebugName();

    /** Copy all of one fabric to another. Dst will look like Src afterwards
     * @param[in] src The source fabric to be cloned
     *
     * @return success
     *
     */
    bool cloneData(const Fabric& src);

    /** Append any data not in the dst cache with data from the src cache.
     *
     * Equivalent to copyOrMergeFabric(src, false, true);
     *
     * @param[in] src The source fabric to be copied.
     *
     * @param[in] filters A set of filters to apply to srcData before appending
     *
     * @return success
     *
     */
    bool appendData(const Fabric& src, Span<FabricCopyFilter> filters);

    /** Append multipe fabric caches to one destination.
     *
     * Equivalent to for(size_t i = 0; i< srcFabricIds.size(); ++i)
     * {
     *    appendFabric(srcFabrics[i], filters)
     * }
     *
     * @param[in] srcFabric The source fabrics to be read from.
     *
     * @param[in] filters A set of filters to apply to srcData before appending
     *
     * @return success
     *
     */
    bool appendData(Span<Fabric> srcFabrics, Span<FabricCopyFilter> filters);

    /** Copy elements from the source to the destination.
     *
     * @param[in] src The source fabric to be copied.
     *
     * @param[in] filters A set of filters to apply to srcData before copying/appending
     *
     * @param[in] overwritePrims If a prim is in the source and the destination, then overwrite the prim in the
     * destination to look like the filtered version of the source prim.
     *
     * @param[in] createNewPrims If a prim is in the source and not in the destination, then add a new prim that looks
     * like the filter version of the source prim. cache.
     *
     * @return success
     *
     */
    bool copyOrMergeData(const Fabric& src, Span<FabricCopyFilter> filters, bool overwritePrims, bool createNewPrims);

    /** copyOrMerge multipe fabric caches to one destination.
     *
     * equivalent to for(size_t i = 0; i< srcFabrics.size(); ++i)
     * {
     *    copyOrMergeFabric(srcFabrics[i], filters, overwritePrims, createNewPrims)
     * }
     *
     * @param[in] srcFabrics The source fabrics to be copied.
     *
     * @param[in] filters A set of filters to apply to srcData before copying/appending
     *
     * @param[in] overwritePrims If a prim is in the source and the destination, then overwrite the prim in the
     * destination to look like the filtered version of the source prim.
     *
     * @param[in] createNewPrims If a prim is in the source and not in the destination, then add a new prim that looks
     * like the filter version of the source prim. cache.
     *
     * @return success
     *
     */
    bool copyOrMergeData(Span<Fabric> srcFabrics,
                         Span<FabricCopyFilter> filters,
                         bool overwritePrims,
                         bool createNewPrims);

    /** copyOrMerge multipe fabric caches to one destination.
     *
     *    equvialent to
     *    copyOrMergeFabricData(src, filters, overwritePrims, createNewPrims);
     *    src.clearData()
     *
     * @param[in] src The source fabric to be copied.
     *
     * @param[in] filters A set of filters to apply to srcData before copying/appending
     *
     * @param[in] overwritePrims If a prim is in the source and the destination, then overwrite the prim in the
     * destination to look like the filtered version of the source prim.
     *
     * @param[in] createNewPrims If a prim is in the source and not in the destination, then add a new prim that looks
     * like the filter version of the source prim. cache.
     *
     * @return success
     *
     */
    bool moveData(Fabric& src, Span<FabricCopyFilter> filters, bool overwritePrims, bool createNewPrims);

    /** Copy buckets from the source to the destination.
     *
     * @param[in] src The source fabric to be copied.
     *
     * @param[in] filter The filter to select the buckets and attributes to be copied.
     *
     * @returns true If all the buckets designated by the filter are copied, false if no buckets copied or there is any
     * bucket skipped due to mismatch paths or duplicated paths in other buckets.
     *
     */
    bool copyBucketData(const Fabric& src, FabricCopyFilter filter);

    // TODO: These should ideally be made private and accessed via friend classes...
    /** Construct from an id. Will not release cache on destruction
     *
     * This should mostly be only for internal use with the interfaces.
     *
     * @param[in] id the fabric cache to wrap
     *
     */
    Fabric(FabricId id);

    /** Get the fabric id of the underlying cache.
     *
     * This is mainly for internal use and should not be needed outside of that.
     *
     * @return The id of the underlying fabric cache
     *
     */
    FabricId getId() const;

    /** Get the prim and attribute topology version for this fabric.
     *
     * Fabric keeps an an internal counter which is incremented:
     *  * when prims are added or removed
     *  * when attributes are added or removed
     *  * array attributes are resized (when the size changes, which invalidates the existing array)
     *
     * @return The current version of the topology
     *
     */
    uint64_t getTopologyVersion();
};

} // namespace fabric
} // namespace omni

#include <omni/fabric/core/impl/Fabric.inl>
