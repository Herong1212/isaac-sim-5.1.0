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
#include <omni/fabric/IToken.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtAssetPath);

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

class IRtAssetPath_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtAssetPath")>
{
protected: // all ABI functions must always be 'protected'.
    virtual IRtAssetPath* create_abi(OMNI_ATTR("not_null, c_str") const char* assetPath) noexcept = 0;
    virtual IRtAssetPath* createWithResolved_abi(OMNI_ATTR("not_null, c_str") const char* assetPath,
                                                 OMNI_ATTR("not_null, c_str") const char* resolvedPath) noexcept = 0;
    virtual OMNI_ATTR("not_prop") const char* getAssetPath_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") const char* getResolvedPath_abi() noexcept = 0;

    // RT-only
    virtual IRtAssetPath* createFromFabric_abi(OMNI_ATTR("not_null, in") const void* fabricAssetPath) noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getAssetPathC_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getResolvedPathC_abi() noexcept = 0;
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


#include "IRtAssetPath.gen.h"
