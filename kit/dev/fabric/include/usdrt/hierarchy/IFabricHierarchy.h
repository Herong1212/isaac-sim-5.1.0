// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
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
#include <omni/fabric/IPath.h>
#include <omni/fabric/IdTypes.h>
#include <usdrt/gf/matrix.h>

namespace usdrt
{
namespace hierarchy
{

OMNI_DECLARE_INTERFACE(IFabricHierarchy);

class IFabricHierarchy_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.hierarchy.IFabricHierarchy")>
{
protected:
    virtual OMNI_ATTR("not_prop, no_api") IFabricHierarchy* getFabricHierarchy_abi(
        const omni::fabric::FabricId fabricId, const omni::fabric::UsdStageId stageId) noexcept = 0;

    virtual OMNI_ATTR("not_prop") omni::fabric::FabricId getFabricId_abi() noexcept = 0;

    virtual void updateWorldXforms_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") usdrt::GfMatrix4d getLocalXform_abi(const omni::fabric::PathC path) noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool setLocalXform_abi(const omni::fabric::PathC path,
                                                         const usdrt::GfMatrix4d xform) noexcept = 0;

    virtual OMNI_ATTR("not_prop") usdrt::GfMatrix4d getWorldXform_abi(const omni::fabric::PathC path) noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool setWorldXform_abi(const omni::fabric::PathC path,
                                                         const usdrt::GfMatrix4d xform) noexcept = 0;

    virtual void trackWorldXformChanges_abi(bool enabled) noexcept = 0;

    virtual OMNI_ATTR("not_prop") void setTimeSampledXformHint_abi(double newTime, bool resyncOccurred) noexcept = 0;

    virtual void markTimeSampledXformDirty_abi(const omni::fabric::PathC path) noexcept = 0;

    virtual void trackLocalXformChanges_abi(bool enabled) noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool getResetXformStack_abi(const omni::fabric::PathC path) noexcept = 0;

    virtual OMNI_ATTR("not_prop") bool setResetXformStack_abi(const omni::fabric::PathC path, bool reset) noexcept = 0;

    virtual void trackResetXformStackChanges_abi(bool enabled) noexcept = 0;

    /** Update world transforms and extents from local transforms on the GPU.
     *
     * This function is meant to be used after only GPU local transform updates happened in Fabric.
     *
     * noStructuralChangesHint - Hint to indicate that there were no structural changes since the last call
     *                           When set to true but there were structural changes the behavior is undefined
     * 
     * Returns: true if the update was successful, false otherwise
     */
    virtual bool updateWorldXformsGpu_abi(OMNI_ATTR("default=false") bool noStructuralChangesHint) noexcept = 0;
};

} // namespace hierarchy
} // namespace usdrt

#include "IFabricHierarchy.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::hierarchy::IFabricHierarchy)
{
public:

    omni::core::ObjectPtr<usdrt::hierarchy::IFabricHierarchy> getFabricHierarchy(const omni::fabric::FabricId fabricId, const omni::fabric::UsdStageId stageId) noexcept
    {
        return omni::core::borrow(getFabricHierarchy_abi(fabricId, stageId));
    }
};
// clang-format on
