// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtPrimSelection.h"
#include "IRtStage.h"

#include <omni/core/IObject.h>
#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <usdrt/gf/range.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtStage105);

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

class IRtStage105_abi : public omni::core::Inherits<IRtStage, OMNI_TYPE_ID("usdrt.IRtStage105")>
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

    // ---- new attr methods to include token
    virtual OMNI_ATTR("not_prop") IRtAttribute* getAttributeAtPath105_abi(omni::fabric::PathC path,
                                                                          omni::fabric::TokenC prop) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtRelationship* getRelationshipAtPath105_abi(omni::fabric::PathC path,
                                                                                omni::fabric::TokenC prop) noexcept = 0;

    // ---- additional flag on hasPrimAtPath to ignore tags from stage query api
    virtual bool hasPrimAtPath105_abi(omni::fabric::PathC path, bool excludeTags) noexcept = 0;

    virtual OMNI_ATTR("not_prop") IRtPrimSelection* selectPrims_abi(
        OMNI_ATTR("in, count=requireAppliedSchemaCount") const omni::fabric::TokenC* requireAppliedSchemaPtr,
        size_t requireAppliedSchemaCount,
        OMNI_ATTR("in, count=requireAttrsCount") const AttrSpecC* requireAttrsPtr,
        size_t requireAttrsCount,
        OMNI_ATTR("in") const omni::fabric::TokenC* requirePrimType,
        uint32_t device) noexcept = 0;

    virtual OMNI_ATTR("not_prop") omni::fabric::FabricId getFabricId_abi() noexcept = 0;
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

#include "IRtStage105.gen.h"
