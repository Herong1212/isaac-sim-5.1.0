// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtPath.h"

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPath107);

class IRtPath107_abi : public omni::core::Inherits<IRtPath, OMNI_TYPE_ID("usdrt.IRtPath107")>
{
protected: // all ABI functions must always be 'protected'.
    virtual bool lessThanOperator_abi(omni::fabric::PathC rhs, omni::fabric::TokenC rhsPropPart) noexcept = 0;
};

} // namespace usdrt

#include "IRtPath107.gen.h"
