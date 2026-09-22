// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/core/IObject.h>
#include <omni/fabric/IFabric.h>
#include <omni/fabric/core/FabricRenderingView.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/TimeWindow.h>
#include <usdrt/gf/vec.h>

namespace usdrt
{
namespace hydra
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(ISceneDelegate);

struct SceneDelegateTimings
{
    size_t numPopulate = 0;
    double accumulatedPopulate = 0.f;
};

enum class GeoStreamingStatus
{
    kUnknown = -1,
    kDisabled = 0,
    kNotStarted = 1,
    kStarted = 2,
    kStoppedAllLoaded = 3,
    kStoppedAllAboveLimitLoaded = 4,
    kStoppedNotEnoughMemory = 5,
};

class SceneDelegateUpdateContext_CoreAPI
{
public:
    SceneDelegateUpdateContext_CoreAPI()
    {
    }
    const SceneDelegateUpdateContext_CoreAPI& operator=(const SceneDelegateUpdateContext_CoreAPI& rhs)
    {
        indexToRender = rhs.indexToRender;
        return *this;
    }
    omni::fabric::SampleIndex indexToRender;
};

class ISceneDelegate_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.hydra.ISceneDelegate")>
{
protected: // all ABI functions must always be 'protected'.
    virtual void create_abi(OMNI_ATTR("in") void const* renderIndex, omni::fabric::PathC delegateID) noexcept = 0;
    virtual void populate_abi(omni::fabric::UsdStageId stageId,
                              OMNI_ATTR("in, out") omni::fabric::FabricRenderingView* fabricRenderingView) noexcept = 0;
    virtual void setTime_abi(double time) noexcept = 0;
    virtual void applyPendingUpdates_abi(OMNI_ATTR("in") const SceneDelegateUpdateContext_CoreAPI& last,
                                         OMNI_ATTR("in") const SceneDelegateUpdateContext_CoreAPI& next) noexcept = 0;
    virtual void popFabricSceneDelegateChanges_abi(omni::fabric::FabricId fabricId) noexcept = 0;
    virtual void* getUsdSceneDelegate_abi() const noexcept = 0;
    virtual size_t getFabricPrimsAddedThisFrame_abi() const noexcept = 0;
    virtual void getTimings_abi(OMNI_ATTR("out") SceneDelegateTimings* timings) const noexcept = 0;
    virtual void setLightMultiplier_abi(float multiplier) noexcept = 0;

    virtual void setReadTransformsFromFabricInRenderDelegate_abi(bool value) noexcept = 0;

    virtual void setRefineLevelFallback_abi(int32_t level) noexcept = 0;
};

// Structures used to pass attribute content hashes between scene delegate and render delegate
struct ArrayContentHashDesc
{
    omni::fabric::ContentHashType contentHash;
    omni::fabric::Type type; // this type may be unknown
};

inline bool operator==(const ArrayContentHashDesc& a, const ArrayContentHashDesc& b)
{
    return (a.contentHash.d[0] == b.contentHash.d[0])
        && (a.contentHash.d[1] == b.contentHash.d[1])
        && (a.type == b.type);
}

struct PrimvarArrayContentHashDesc
{
    omni::fabric::ContentHashType primvarContentHash;
    omni::fabric::ContentHashType primvarIndexContentHash;
    omni::fabric::Type primvarType; // this type may be unknown
};

inline bool operator==(const PrimvarArrayContentHashDesc& a, const PrimvarArrayContentHashDesc& b)
{
    return (a.primvarContentHash.d[0] == b.primvarContentHash.d[0])
        && (a.primvarContentHash.d[1] == b.primvarContentHash.d[1])
        && (a.primvarIndexContentHash.d[0] == b.primvarIndexContentHash.d[0])
        && (a.primvarIndexContentHash.d[1] == b.primvarIndexContentHash.d[1])
        && (a.primvarType == b.primvarType);
}

} // namespace hydra
} // namespace usdrt

#include "ISceneDelegate.gen.h"
