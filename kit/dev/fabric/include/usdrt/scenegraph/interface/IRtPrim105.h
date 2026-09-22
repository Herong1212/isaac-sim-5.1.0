// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtAttribute.h"
#include "IRtPrim.h"

#include <omni/core/IObject.h>
#include <omni/fabric/Type.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPrim105);

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

class IRtPrim105_abi : public omni::core::Inherits<IRtPrim, OMNI_TYPE_ID("usdrt.IRtPrim105")>
{
protected: // all ABI functions must always be 'protected'.
    virtual OMNI_ATTR("not_prop") uint32_t getAttributesWithTypeCount_abi(omni::fabric::TypeC attrType) noexcept = 0;
    virtual OMNI_ATTR("not_prop, no_api") bool getAttributesWithType_abi(omni::fabric::TypeC attrType,
                                                                         OMNI_ATTR("out, count=attrsSize, *not_null")
                                                                             IRtAttribute** attrs,
                                                                         uint32_t attrsSize) noexcept = 0;
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

#include "IRtPrim105.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtPrim105)
{
public:

    bool getAttributesWithType(omni::fabric::TypeC attrType, usdrt::IRtAttribute** attrs, uint32_t attrsSize) noexcept
    {
        if (attrsSize == 0)
        {
            return false;
        }

        return getAttributesWithType_abi(attrType, attrs, attrsSize);
    }

};
// clang-format on
