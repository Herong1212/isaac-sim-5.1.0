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
#include <omni/fabric/SimStageWithHistory.h>

namespace usdrt
{
namespace benchmarks
{

OMNI_DECLARE_INTERFACE(IBenchmarks);

class IBenchmarks_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.benchmarks.IBenchmarks")>
{
protected:
    virtual uint64_t getCount_abi() noexcept = 0;
    virtual OMNI_ATTR("c_str, not_null") const char* getName_abi(uint64_t index) noexcept = 0;
    virtual void activate_abi(OMNI_ATTR("c_str, not_null") const char* name,
                              omni::fabric::UsdStageId usdStageId) noexcept = 0;
    virtual void update_abi(float currentTime, float elapsedSecs) noexcept = 0;
    virtual void close_abi() noexcept = 0;
};

} // namespace benchmarks
} // namespace usdrt

#include "IBenchmarks.gen.h"
