// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtPrim105.h"

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPrim107);

class IRtPrim107_abi : public omni::core::Inherits<IRtPrim105, OMNI_TYPE_ID("usdrt.IRtPrim107")>
{
protected: // all ABI functions must always be 'protected'.
    virtual OMNI_ATTR("not_prop") IRtPrim* getChild107_abi(omni::fabric::TokenC name, bool prefetchFromUsd) noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result getChildren107_abi( // disable omni.bind until OM-21202
        OMNI_ATTR("out, count=*outCount, *not_null") IRtPrim** out,
        OMNI_ATTR("out, not_null") uint32_t* outCount, bool prefetchFromUsd) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPrim* getParent107_abi(bool prefetchFromUsd) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPrim* getNextSibling107_abi(bool prefetchFromUsd) noexcept = 0;
};

} // namespace usdrt

#include "IRtPrim107.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtPrim107)
{
public:

    std::vector<omni::core::ObjectPtr<usdrt::IRtPrim>> getChildren107(bool prefetchFromUsd) noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtPrim>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtPrim*>(
            [this, prefetchFromUsd](usdrt::IRtPrim** out, uint32_t* outCount) // get func
        {
            std::memset(out, 0, sizeof(usdrt::IRtPrim*) * *outCount); // incoming ptrs must be nullptr
            return this->getChildren107_abi(out, outCount, prefetchFromUsd);
        },
            [&vec](usdrt::IRtPrim** in, uint32_t inCount) // fill func
        {
            vec.reserve(inCount);
            for (uint32_t i = 0; i < inCount; ++i)
            {
                vec.emplace_back(in[i], omni::core::kSteal);
            }
        }
        );

        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to get children: 0x%08X", result);
        }

        return vec;
    }

};
// clang-format on