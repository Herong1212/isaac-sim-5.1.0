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
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/IToken.h>

namespace omni
{
namespace fabric
{
    
struct IChangeTrackerConfig
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IChangeTrackerConfig", 0, 5);

    void(CARB_ABI* pause)(StageReaderWriterId stageId, ListenerId listenerId);
    void(CARB_ABI* resume)(StageReaderWriterId stageId, ListenerId listenerId);
    bool(CARB_ABI* isChangeTrackingPaused)(StageReaderWriterId stageId, ListenerId listenerId);

    void(CARB_ABI* attributeEnable)(StageReaderWriterId stageId, TokenC attrName, ListenerId listenerId);
    void(CARB_ABI* attributeDisable)(StageReaderWriterId stageId, TokenC attrName, ListenerId listenerId);

    bool(CARB_ABI* isListenerAttached)(StageReaderWriterId stageId, ListenerId listenerId);
    void(CARB_ABI* detachListener)(StageReaderWriterId stageId, ListenerId listenerId);
    size_t(CARB_ABI* getListenerCount)(StageReaderWriterId stageId);

    void(CARB_ABI* enablePrimCreateTracking)(StageReaderWriterId stageId, ListenerId listenerId);

    ListenerId(CARB_ABI* createListener)();

};

}
}
