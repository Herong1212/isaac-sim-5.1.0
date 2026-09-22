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
#include <omni/fabric/FabricTypes.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/batch/View.h>
#include <usdrt/scenegraph/interface/Common.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPrimSelection);

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

class IRtPrimSelection_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtPrimSelection")>
{
protected: // all ABI functions must always be 'protected'.
    virtual OMNI_ATTR("not_prop") size_t getAttributeCount_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") void getAttributeSpecs_abi(OMNI_ATTR("out, count=outSpecCount") AttrSpecC* outSpecs,
                                                             size_t outSpecCount) noexcept = 0;
    virtual OMNI_ATTR("not_prop") uint32_t getDevice_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::batch::View getBatchView_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::batch::AttributeRef
        getRef_abi(omni::fabric::TokenC name, omni::fabric::TypeC type) noexcept = 0;
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


#include "IRtPrimSelection.gen.h"
