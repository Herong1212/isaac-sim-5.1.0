// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtPrimSelection.h"

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtPrimSelection106_4);

class IRtPrimSelection106_4_abi : public omni::core::Inherits<IRtPrimSelection, OMNI_TYPE_ID("usdrt.IRtPrimSelection106_4")>
{
protected: // all ABI functions must always be 'protected'.
    virtual bool prepareForReuse_abi() noexcept = 0;

    virtual bool getPaths_abi(
        OMNI_ATTR("out, count=outPathCount") omni::fabric::PathC* outPaths,
        uint32_t outPathCount
    ) noexcept = 0;
};

} // namespace usdrt

#include "IRtPrimSelection106_4.gen.h"
