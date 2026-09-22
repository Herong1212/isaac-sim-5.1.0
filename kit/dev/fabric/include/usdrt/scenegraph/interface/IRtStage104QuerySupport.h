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
#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <usdrt/gf/range.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtStage104QuerySupport);

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

class IRtStage104QuerySupport_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtStage104QuerySupport")>
{
protected: // all ABI functions must always be 'protected'.
    virtual uint32_t findCount_abi(omni::fabric::TokenC typeName,
                                   OMNI_ATTR("in, count=apiNamesSize") const omni::fabric::TokenC* apiNames,
                                   uint32_t apiNamesSize) noexcept = 0;
    virtual bool find_abi(omni::fabric::TokenC typeName,
                          OMNI_ATTR("in, count=apiNamesSize") const omni::fabric::TokenC* apiNames,
                          uint32_t apiNamesSize,
                          OMNI_ATTR("out, count=outPathCount") omni::fabric::PathC* outPaths,
                          uint32_t outPathCount) noexcept = 0;
    virtual bool computeWorldBound_abi(OMNI_ATTR("out") GfRange3d* result) noexcept = 0;
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

#include "IRtStage104QuerySupport.gen.h"
