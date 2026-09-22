// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IXformCache.h"

namespace usdrt
{
namespace xformcache
{

OMNI_DECLARE_INTERFACE(ISharedXformCache);

class ISharedXformCache_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.xformcache.ISharedXformCache")>
{
protected:
    virtual bool hasCache_abi(const omni::fabric::UsdStageId stageId) noexcept = 0;

    virtual OMNI_ATTR("no_api") IXformCache* getCache_abi(const omni::fabric::UsdStageId stageId) noexcept = 0;

    virtual OMNI_ATTR("no_api") IXformCache* getOrCreateCache_abi(const omni::fabric::UsdStageId stageId) noexcept = 0;

    virtual bool clear_abi() noexcept = 0;
};

} // namespace xformcache
} // namespace usdrt

#include "ISharedXformCache.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::xformcache::ISharedXformCache)
{
public:
    omni::core::ObjectPtr<usdrt::xformcache::IXformCache> getCache(omni::fabric::UsdStageId stageId) noexcept
    {
        return omni::core::borrow(getCache_abi(stageId));
    }

    omni::core::ObjectPtr<usdrt::xformcache::IXformCache> getOrCreateCache(omni::fabric::UsdStageId stageId) noexcept
    {
        return omni::core::borrow(getOrCreateCache_abi(stageId));
    }

};
// clang-format on
