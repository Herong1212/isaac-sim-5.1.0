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
#include "IRtProperty.h"

#include <omni/core/IObject.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IFabric.h>

#include <vector>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtRelationship);

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

class IRtRelationship_abi : public omni::core::Inherits<usdrt::IRtProperty, OMNI_TYPE_ID("usdrt.IRtRelationship")>
{
protected: // all ABI functions must always be 'protected'.
    // ---- targets
    virtual bool hasAuthoredTargets_abi() noexcept = 0;

    // Note: As of this implementation, Fabric does not support
    // lists of targets for relationships, so the behavior of some
    // of these may diverge from USD until that support is added
    virtual bool addTarget_abi(omni::fabric::PathC path, ListPosition position) noexcept = 0;
    virtual bool removeTarget_abi(omni::fabric::PathC path) noexcept = 0;
    virtual bool OMNI_ATTR("not_prop")
        setTargets_abi(OMNI_ATTR("in, count=size") const omni::fabric::PathC* paths, uint32_t size) noexcept = 0;
    virtual bool clearTargets_abi() noexcept = 0;
    virtual uint32_t numTargets_abi() noexcept = 0;
    virtual bool OMNI_ATTR("not_prop")
        getTargets_abi(OMNI_ATTR("out, count=size") omni::fabric::PathC* paths, uint32_t size) noexcept = 0;
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

#include "IRtRelationship.gen.h"
