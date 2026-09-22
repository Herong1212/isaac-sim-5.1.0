// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Common.h"

#include <omni/fabric/IToken.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtSchemaRegistry);

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

class IRtSchemaRegistry_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtSchemaRegistry")>
{
protected: // all ABI functions must always be 'protected'.
    virtual IRtSchemaRegistry* initRegistry_abi() noexcept = 0;

    virtual bool isConcrete_abi(omni::fabric::TokenC primTypeC) noexcept = 0;
    virtual bool isAppliedAPISchema_abi(omni::fabric::TokenC apiSchemaTypeC) noexcept = 0;
    virtual bool isMultipleApplyAPISchema_abi(omni::fabric::TokenC apiSchemaTypeC) noexcept = 0;
    virtual bool isA_abi(omni::fabric::TokenC sourceTypeNameC, omni::fabric::TokenC queryTypeNameC) noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getAliasFromName_abi(omni::fabric::TokenC nameC) noexcept = 0;
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

#include "IRtSchemaRegistry.gen.h"
