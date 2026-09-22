// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtObject.h"

#include <omni/core/IObject.h>
#include <omni/extras/OutArrayUtils.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/str/IReadOnlyCString.h>

#include <vector>

namespace usdrt
{


// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtProperty);

// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// The interfaces within these obnoxious comment blocks are now locked for long-term support.
// Any changes you wish to make should be added in a new interface.
//
// Please do not break our precious ABIs!
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************

class IRtProperty_abi : public omni::core::Inherits<usdrt::IRtObject, OMNI_TYPE_ID("usdrt.IRtPropety")>
{
protected: // all ABI functions must always be 'protected'.
    // ---- property name
    virtual OMNI_ATTR("not_prop") omni::str::IReadOnlyCString* getBaseName_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::str::IReadOnlyCString* getNamespace_abi() noexcept = 0;
    virtual OMNI_ATTR("no_api") omni::core::Result
        splitName_abi(OMNI_ATTR("out, count=*partsCount, *not_null") omni::str::IReadOnlyCString** parts,
                      OMNI_ATTR("out, not_null") uint32_t* partsCount) noexcept = 0;
};

// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// End of locked interfaces. Enjoy the rest of your day.
//
//     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION     ATTENTION
//
// *********************************************************************************************************************
// *********************************************************************************************************************
// *********************************************************************************************************************


} // namespace usdrt

#include "IRtProperty.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtProperty) {
public:
    std::vector<std::string> splitName() noexcept
    {
        std::vector<omni::core::ObjectPtr<omni::str::IReadOnlyCString>> vec;
        auto result = omni::extras::getOutArray<omni::str::IReadOnlyCString*>(
            [this](omni::str::IReadOnlyCString** out, uint32_t* outCount) // get func
            {
                std::memset(out, 0, sizeof(omni::str::IReadOnlyCString*) * *outCount);
                // incoming ptrs must be nullptr
                return this->splitName_abi(out, outCount);
            },
            [&vec](omni::str::IReadOnlyCString** in, uint32_t inCount) // fill func
            {
                vec.reserve(inCount);
                for (uint32_t i = 0; i < inCount; ++i)
                {
                    vec.emplace_back(in[i], omni::core::kSteal);
                }
            }
        );

        std::vector<std::string> out;
        out.reserve(vec.size());
        for (const auto& roc : vec)
        {
            out.push_back(std::string(roc->getBuffer()));
        }

        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("Unable to split name: 0x%08X", result);
        }

        return out;
    }

};
// clang-format on
