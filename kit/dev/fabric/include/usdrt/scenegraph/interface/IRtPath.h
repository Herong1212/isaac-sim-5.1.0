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
#include <omni/extras/OutArrayUtils.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
// #include <omni/str/IReadOnlyCString.h>

#include <vector>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPath);

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

class IRtPath_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtPath")>
{
protected: // all ABI functions must always be 'protected'.
    virtual OMNI_ATTR("not_prop") IRtPath* create_abi(omni::fabric::PathC primPart,
                                                      omni::fabric::TokenC propPart) noexcept = 0;

    virtual void setPath_abi(omni::fabric::PathC primPart, omni::fabric::TokenC propPart) noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::PathC getPrimPart_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getPropPart_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getNameToken_abi() noexcept = 0;

    virtual bool isAbsolutePath_abi() noexcept = 0;

    virtual OMNI_ATTR("no_api") omni::core::Result
        getPrefixes_abi(OMNI_ATTR("out, count=*numPrefixes, *not_null") IRtPath** prefixes,
                        OMNI_ATTR("out, not_null") uint32_t* numPrefixes) noexcept = 0; // disable omni.bind until
                                                                                        // OM-21202
    virtual bool hasPrefix_abi(omni::fabric::PathC primPart, omni::fabric::TokenC propPart) noexcept = 0;

    virtual OMNI_ATTR("not_prop") IRtPath* ancestorsRangeIteratorIncrement_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") IRtPath* replacePrefix_abi(omni::fabric::PathC oldPrefixPrimPart,
                                                             omni::fabric::TokenC oldPrefixPropPart,
                                                             omni::fabric::PathC newPrefixPrimPart,
                                                             omni::fabric::TokenC newPrefixPropPart) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPath* getCommonPrefix_abi(omni::fabric::PathC primPart,
                                                               omni::fabric::TokenC propPart) noexcept = 0;
    virtual void removeCommonSuffix_abi(omni::fabric::PathC primPart,
                                        omni::fabric::TokenC propPart,
                                        IRtPath* result1,
                                        IRtPath* result2,
                                        bool stopAtRootPrim) noexcept = 0;

    virtual bool isValidIdentifier_abi(OMNI_ATTR("not_null, c_str") const char* name) noexcept = 0;
    virtual bool isValidNamespacedIdentifier_abi(OMNI_ATTR("not_null, c_str") const char* name) noexcept = 0;
    virtual bool isValidPathString_abi(OMNI_ATTR("not_null, in, c_str") const char* pathString,
                                       OMNI_ATTR("out") char* errMsg) noexcept = 0;
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


#include "IRtPath.gen.h"


// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtPath)
{
public:

    std::vector<omni::core::ObjectPtr<usdrt::IRtPath>> getPrefixes() noexcept
    {
        std::vector<omni::core::ObjectPtr<usdrt::IRtPath>> vec;
        auto result = omni::extras::getOutArray<usdrt::IRtPath*>(
            [this](usdrt::IRtPath** out, uint32_t* outCount) // get func
            {
                std::memset(out, 0, sizeof(usdrt::IRtPath*) * *outCount); // incoming ptrs must be nullptr
                return this->getPrefixes_abi(out, outCount);
            },
            [&vec](usdrt::IRtPath** in, uint32_t inCount) // fill func
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
            OMNI_LOG_ERROR("Unable to get prefixes: 0x%08X", result);
        }

        return vec;
    }

};
