// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
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
#include "IRtRelationship.h"

#include <omni/core/IObject.h>
#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>


namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtStage);

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

class IRtStage_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtStage")>
{
protected: // all ABI functions must always be 'protected'.
    // ---- static methods
    virtual IRtStage* open_abi(OMNI_ATTR("c_str, in, not_null") const char* identifier) noexcept = 0;
    virtual IRtStage* createNew_abi(OMNI_ATTR("c_str, in, not_null") const char* identifier) noexcept = 0;
    virtual IRtStage* createInMemory_abi(OMNI_ATTR("c_str, in, not_null") const char* identifier) noexcept = 0;
    virtual IRtStage* attach_abi(omni::fabric::UsdStageId stageId,
                                 omni::fabric::StageReaderWriterId stageReaderWriterId) noexcept = 0;
    virtual IRtStage* attachUnknown_abi(omni::fabric::UsdStageId stageId) noexcept = 0;

    // ---- prim methods
    virtual OMNI_ATTR("not_prop") IRtPrim* getDefaultPrim_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPrim* getPrimAtPath_abi(omni::fabric::PathC path) noexcept = 0;
    virtual IRtPrim* definePrim_abi(omni::fabric::PathC path, omni::fabric::TokenC typeName) noexcept = 0;
    virtual bool removePrim_abi(omni::fabric::PathC path) noexcept = 0;

    // ---- attr methods
    virtual OMNI_ATTR("not_prop") IRtAttribute* getAttributeAtPath_abi(omni::fabric::PathC path) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtRelationship* getRelationshipAtPath_abi(omni::fabric::PathC path) noexcept = 0;

    // ---- rt methods
    virtual void done_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::UsdStageId getStageId_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop, no_api") omni::fabric::StageReaderWriterId getStageInProgressId_abi() noexcept = 0;
    virtual void write_abi(OMNI_ATTR("c_str, in") const char* filepath) noexcept = 0;
    virtual bool hasPrimAtPath_abi(omni::fabric::PathC path) noexcept = 0;
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

#include "IRtStage.gen.h"

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtStage)
{
public:

    omni::fabric::StageReaderWriterId getStageReaderWriterId()
    {
        return getStageInProgressId_abi();
    }
};
// clang-format on
