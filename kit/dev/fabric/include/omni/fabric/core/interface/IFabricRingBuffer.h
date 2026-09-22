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

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/Ordered_Set.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/TimeWindow.h>

#include <stdint.h>

namespace omni
{
namespace fabric
{

struct IFabricRingBuffer
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IFabricRingBuffer", 1, 2);

    RingBufferId(CARB_ABI* create)(size_t slots, FabricTime rate, FabricOptions options);
    void(CARB_ABI* release)(RingBufferId id);
    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - Due to changing concerns this is no longer useful")
    void(CARB_ABI* markForRelease)(RingBufferId id);

    size_t(CARB_ABI* growBuffer)(RingBufferId id, size_t growthAmount);
    void(CARB_ABI* setFilter)(RingBufferId id, Span<FabricCopyFilter> filters);
    FabricTime(CARB_ABI* getRate)(RingBufferId id);

    void(CARB_ABI* attachToFabric)(RingBufferId id, FabricId fabricId);
    void(CARB_ABI* attachToFabrics)(RingBufferId id, Span<FabricId> fabricIds);
    void(CARB_ABI* detachFromFabric)(RingBufferId id, FabricId fabricId);
    void(CARB_ABI* detachFromFabrics)(RingBufferId id, Span<FabricId> fabricIds);
    void(CARB_ABI* detachAllSources)(RingBufferId id);

    bool(CARB_ABI* pushNextSlot)(RingBufferId id);
    bool(CARB_ABI* tryPushNextSlot)(RingBufferId id);
    bool(CARB_ABI* pushNextSlotWithTimeStamp)(RingBufferId id, FabricTime timestamp);
    bool(CARB_ABI* tryPushNextSlotWithTimeStamp)(RingBufferId id, FabricTime timestamp);

    LockedRingBufferWindowId(CARB_ABI* lockTimeWindowForRead)(RingBufferId id, FabricTimeWindow window);
    void(CARB_ABI* unlockTimeWindowForRead)(RingBufferId id, LockedRingBufferWindowId window);
    size_t(CARB_ABI* getSampleCountForTimeWindow)(RingBufferId id, LockedRingBufferWindowId window);
    size_t(CARB_ABI* getFabricIdsForTimeWindow)(RingBufferId id,
                                                LockedRingBufferWindowId window,
                                                Span<FabricId>* ids,
                                                Span<FabricTime>* timestamps);
    void(CARB_ABI* addRef)(RingBufferId id);
    
    // NOTE: These ane only implemnted for some DS MAGIC.. Will ASSERT IF CALLED OUTSIDE OF THAT
    bool(CARB_ABI* pushNextSlotChangeTracked)(RingBufferId id, ListenerId listenerId);
    bool(CARB_ABI* tryPushNextSlotChangeTracked)(RingBufferId id, ListenerId listenerId);
    bool(CARB_ABI* pushNextSlotWithTimeStampChangeTracked)(RingBufferId id, FabricTime timestamp, ListenerId listenerId);
    bool(CARB_ABI* tryPushNextSlotWithTimeStampChangeTracked)(RingBufferId id, FabricTime timestamp, ListenerId listenerId);

    LockedRingBufferWindowId(CARB_ABI* lockImplicitWindowForRead)(RingBufferId id, FabricTime targetTime);
};

} // namespace fabric
} // namespace omni
