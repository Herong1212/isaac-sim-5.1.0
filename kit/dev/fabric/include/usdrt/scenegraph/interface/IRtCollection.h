// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/core/IObject.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/IPath.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtCollection);

class IRtCollection_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IRtCollection")>
{
protected:
    virtual bool isCollectionAPIPath_abi(omni::fabric::PathC primPath,
                                         omni::fabric::TokenC property,
                                         OMNI_ATTR("in, out") omni::fabric::TokenC* instanceName) noexcept = 0;
};

} // namespace usdrt

#include "IRtCollection.gen.h"
