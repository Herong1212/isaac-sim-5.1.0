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
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/Fabric.h>
#include <omni/fabric/core/interface/IFabricRingBuffer.h>

#include <memory>

namespace omni
{
namespace fabric
{
// The Ringbuffers are temporally tagged collections of read only data
// that are drawn from multiple data sources and potentially filtered for interest.
// The Ringbuffer provides protections for reading data so that data being read
// is not overwritten. This will stall the writes if a conflict arises, but
// the api provides methods to resize the ringbuffer on the fly if a stall occurs.
// Think of the protection model as a ReaderWriterLock(aka shared_mutex)
class FabricRingBuffer
{
    RingBufferId m_id;
    IFabricRingBuffer* m_interface;

public:

    /** Create a RingBuffer that can be attached to a data source(e.g., Fabric)
     * When last referencing object is freed, ringbuffer wil be released
     * Note: If there are outstanding locked windows this will be blocking and could lead to a hang
     * 
     * @param[in] slots The number of slots in the ringbuffer at creation.
     *
     * @param[in] rate The {duration/quantum} which each slot in the ring buffer covers. Each call to pushNextSlot
     * increments the time point associated with the slot and assumes this rate. If kInvalidFabricTime is set as the rate then
     * the RingBuffer will be treated as having a variable rate and the timeStamped versions of pushNext must be used
     * with an explicit timestamp.
     *
     * The timestamps are used for interpolation by various apis used to read from the ringbuffer.
     *
     * @param[in] options The default storage options for the ring buffer. Attaching to a source with more advanced
     * options will cause all slots options to be increased in scope.  (e.g., a ring buffer without cuda enabled
     * attaching to a fabric cache with cuda will enable cuda for the ringbuffer.)
     *
     * @return A RingBufferId that can be used to reference the system.
     */
    FabricRingBuffer(size_t slots, FabricTime rate, FabricOptions options);

    FabricRingBuffer(const FabricRingBuffer& other);
    FabricRingBuffer& operator=(const FabricRingBuffer& other);

    FabricRingBuffer(FabricRingBuffer&& other);
    FabricRingBuffer& operator=(FabricRingBuffer&& other);
    ~FabricRingBuffer();



    /**
     * Pushes data to the next available slot in the ringbuffer for write.
     * This call will block if the next write slot is still being read.
     * Calling this on a variable rate ringbuffer will fail immediately
     *
     * Will advance the timestamp of the write slot based upon the specified rate.
     *
     * @return The success of the operation.
     */
    bool pushNextSlot();

    /** Tries to push to the next available slot.
     *
     * If the slot is still being read it will return
     * immediately.
     * Calling this on a variable rate ringbuffer will fail immediately
     *
     * Will advance the timestamp of the write slot based upon the specified rate.
     * @return The success of the operation.
     * 
     */
    bool tryPushNextSlot();

    /**
     * Pushes data to the next available slot in the ringbuffer for write.
     *
     * This call will block if the next write slot is still being read.
     * Calling this on a fixed rate ringbuffer will fail immediately
     * Marks the write slot with the specified timestamp.
     * 
     * @param[in] timestamp A rational time used as the timestamp for the write slot.
     *
     * @return the success of the operation.
     * 
     */
    bool pushNextSlot(FabricTime timestamp);

    /**
     * Tries to push to the next available slot
     * 
     * If the slot is still being read it will return
     * immediately.
     * Calling this on a fixed rate ringbuffer will fail immediately
     * Marks the write slot with the specified timestamp.
     * 
     * @param[in] timestamp A rational time used as the timestamp for the write slot.
     *
     * @return the success of the operation.
     * 
     */
    bool tryPushNextSlot(FabricTime timestamp);

    /**
     * Mark slots within the specified time window as locked for reading to prevent overwrite.
     * 
     * @param[in] window A time window to lock
     *
     * @return The id of the locked window to be used in later calls. These ids are only unique for
     * the ringbuffer they were created on. Using an id across ringbuffers will have unexpected results
     *
     */
    LockedRingBufferWindowId lockWindow(FabricTimeWindow window);

    /**
     * Mark slots at the specified time or bounding slots as locked for reading. 
     * 
     * If there is a slot that matches the target time exactly only that slot will be locked
     * Otherwis it will find the nearest upper and lower bounding times in the ringbuffer.
     * this may result in zero, one, or two slots being retured depending on the occupancy of the ringbuffer.
     * 
     * @param[in] time A time to search for
     *
     * @return The id of the locked window to be used in later calls. These ids are only unique for
     * the ringbuffer they were created on. Using an id across ringbuffers will have unexpected results
     *
     */
    LockedRingBufferWindowId lockSamples(FabricTime time);

    /** unlock slots within the specified time window that are marked locked for read.
     *
     * @param[in] window The id of the window to unlock. If the window is not found this is a noop
     *
     */
    void unlockWindow(LockedRingBufferWindowId window);

    /**
     * Get the number of samples in a given window
     * 
     * @param[in] window The id of the window
     *
     * @return the number of samples within the window. 0 for invalid or unfound windows
     *
     */
    size_t getSampleCount(LockedRingBufferWindowId window);

    /** Get timestamps and fabricids for each sample in the given window
     * 
     * @param[in] window The window to check
     *
     * @return A vector of Fabrics and the associated time stamp in temporal order
     * 
     */
    std::vector<std::pair<Fabric, FabricTime>> getFabrics(LockedRingBufferWindowId window);


    /**
     * Add a fabric to the list of fabrics copied from by the ring buffer when writing a slot.
     *
     * Attaching to a previously attached fabricId will not change the attachment order. This is effectively a no-op
     *
     * This is equivalent to iFabric->appendFabrics(attachedFabrics, numAttachedFabrics, writeSlot, filter,
     * filterCount); where the append order is the order in which fabrics were attached.
     * 
     * @param[in] fabricId The fabric to attach the ringbuffer to.
     * 
     */
    void attach(const Fabric& cache);

    /** attach multiple fabric caches to the ringbuffer at once
    * 
     * @param[in] caches the Fabrics to attach the ringbuffer to
     *
     */
    void attach(Span<Fabric> caches);

    /**
     * Remove a fabric from the list of fabrics the ringbuffer copies on push
     * 
     * @param[in] cache The fabric to detach from
     * 
     */
    void detach(const Fabric& cache);

    /** remove multiple fabrics from the list of fabrics the ringbuffer copies on push
     * 
     * @param[in] caches The fabrics to detach from
     *
     */
    void detach(Span<Fabric> caches);

    /** Remove all fabrics from the list of fabrics the ringbuffer copies on push
     * 
     */
    void detachAllSources();

    /**
     * Increase the number of slots in the ringbuffer.
     *
     * @param[in] growthAmount The number of slots to add.
     *
     * @return the new total size of the ringbuffer.
     */
    size_t growBuffer(size_t growthAmount);

    /**
     * Set a read filter for the ringbuffer to filter what data is fetched from the sources.
     * 
     * If no filter is set the ringbuffer will attempt to fetch all data from all of its sources.
     * 
     * @param[in] filters A pointer to some number of FabricCopyFilters. These will be deep copied.
     *
     */
    void setFilter(Span<FabricCopyFilter> filters);

    /**
     * Get the rate of the ringbuffer
     * 
     * @return The rate of the ringbuffer, kInvalidFabricTime for variable rate ringbuffers
     */
    FabricTime getRate() const;

    // TODO: These should ideally be made private and accessed via friend classes...

    /** Get the id of the underlying RingBuffer.
     * This is mainly for internal use and should not be needed outside of that.
     *
     * @return The id of the underlying id of the RingBuffer
     *
     */
    RingBufferId getId() const;

    /** Construct from an id. Will not release ringbuffer on destruction
     *
     * This should mostly be only for internal use with the interfaces.
     *
     * @param[in] id The fabric ringbuffer to wrap
     *
     */
    FabricRingBuffer(RingBufferId id);
};
} // namespace fabric
} // namespace omni

#include <omni/fabric/core/impl/FabricRingBuffer.inl>
