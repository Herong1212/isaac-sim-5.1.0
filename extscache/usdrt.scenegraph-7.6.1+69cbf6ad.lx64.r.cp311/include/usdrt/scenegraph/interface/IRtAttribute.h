// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtProperty.h"

#include <omni/core/IObject.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IFabric.h>

#include <vector>

namespace usdrt
{


// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtAttribute);

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

class IRtAttribute_abi : public omni::core::Inherits<usdrt::IRtProperty, OMNI_TYPE_ID("usdrt.IRtAttribute")>
{
protected: // all ABI functions must always be 'protected'.
    // ---- values
    virtual bool hasValue_abi() noexcept = 0;
    virtual bool hasAuthoredValue_abi() noexcept = 0;
    virtual bool hasAuthoredValueGpu_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") omni::fabric::ConstSpanC getValue_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::SpanC getValueGpu_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::SpanC setValue_abi() noexcept = 0;
    virtual OMNI_ATTR("not_prop") omni::fabric::SpanC setValueGpu_abi() noexcept = 0;

    virtual OMNI_ATTR("not_prop") size_t getValueArraySize_abi() noexcept = 0;
    // setValueNewArraySize() should be called before setValue() when
    // writing a new array value to fabric
    virtual OMNI_ATTR("not_prop") void setValueNewArraySize_abi(size_t size) noexcept = 0;

    // ---- metadata
    virtual OMNI_ATTR("not_prop") omni::fabric::TypeC getTypeName_abi() noexcept = 0;
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

#include "IRtAttribute.gen.h"
