// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
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
namespace xformcache
{

OMNI_DECLARE_INTERFACE(IXformCache);

class IXformCache_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.xformcache.IXformCache")>
{
protected:
    virtual bool attachToStage_abi(const omni::fabric::UsdStageId stageId) noexcept = 0;

    virtual omni::fabric::UsdStageId getStageId_abi() noexcept = 0;

    virtual void syncXforms_abi() noexcept = 0;

    virtual void syncTargetedXforms_abi(const omni::fabric::PathC targetPath) noexcept = 0;

    virtual OMNI_ATTR("not_prop") usdrt::GfMatrix4d getLatestWorldXform_abi(const omni::fabric::PathC path) noexcept = 0;

    virtual usdrt::GfMatrix4d computeWorldXform_abi(const omni::fabric::PathC path) noexcept = 0;
};

} // namespace xformcache
} // namespace usdrt

#include "IXformCache.gen.h"
