// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtStage105.h"

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtStage106);

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

class IRtStage106_abi : public omni::core::Inherits<IRtStage105, OMNI_TYPE_ID("usdrt.IRtStage106")>
{
protected: // all ABI functions must always be 'protected'.
    virtual void writeWithOptions_abi(OMNI_ATTR("c_str, in") const char* filepath, bool includePrivate, bool convertXforms) noexcept = 0;
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

#include "IRtStage106.gen.h"
