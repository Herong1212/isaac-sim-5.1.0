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
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>

#include <vector>

namespace usdrt
{


// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtObject);
OMNI_DECLARE_INTERFACE(IRtPrim);
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

class IRtObject_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtObject")>
{
protected: // all ABI functions must always be 'protected'.
    // ---- validity
    virtual bool isValid_abi() noexcept = 0;

    // ---- context
    virtual OMNI_ATTR("not_prop, no_api") IRtPrim* getPrim_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop, no_api") IRtStage* getStage_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") omni::fabric::TokenC getName_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::PathC getPrimPath_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::PathC getPath_abi() noexcept = 0;
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

#include "IRtObject.gen.h"

// FIXME omni.bind doesn't generate ObjectPtr correctly with forward declarations,
// as far as I can tell, or I'm missing something important

// clang-format off
OMNI_DEFINE_INTERFACE_API(usdrt::IRtObject) {
public:

    omni::core::ObjectPtr<usdrt::IRtPrim> getPrim() noexcept {
        return omni::core::steal(getPrim_abi());
    }

    omni::core::ObjectPtr<usdrt::IRtStage> getStage() noexcept
    {
        return omni::core::steal(getStage_abi());
    }
};
// clang-format on
