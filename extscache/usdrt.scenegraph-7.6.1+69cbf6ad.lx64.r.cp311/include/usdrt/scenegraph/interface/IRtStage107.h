// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRtStage106_4.h"
#include <usdrt/scenegraph/usd/usd/timeCode.h>

#include <omni/Vector.h>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtStage107);

class IRtStage107_abi : public omni::core::Inherits<IRtStage106_4, OMNI_TYPE_ID("usdrt.IRtStage107")>
{
protected: // all ABI functions must always be 'protected'.
    virtual OMNI_ATTR("not_prop") IRtPrim* getDefaultPrim107_abi(bool prefetchFromUsd) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtPrim* getPrimAtPath107_abi(omni::fabric::PathC path, bool prefetchFromUsd) noexcept = 0;

    virtual OMNI_ATTR("not_prop") IRtAttribute* getAttributeAtPath107_abi(omni::fabric::PathC path,
                                                                          omni::fabric::TokenC prop,
                                                                          bool prefetchFromUsd) noexcept = 0;
    virtual OMNI_ATTR("not_prop") IRtRelationship* getRelationshipAtPath107_abi(omni::fabric::PathC path,
                                                                                omni::fabric::TokenC prop,
                                                                                bool prefetchFromUsd) noexcept = 0;
    virtual IRtStage* createOnlyInFabric_abi() noexcept = 0;
    virtual IRtStage* attachByFabricId_abi(const omni::fabric::FabricId fabricId) noexcept = 0;
    virtual bool isFabricOnlyStage_abi() noexcept = 0;

    // `find` without needing to call `findCount` first
    virtual bool find107_abi(omni::fabric::TokenC typeName,
                             OMNI_ATTR("in, count=apiNamesSize") const omni::fabric::TokenC* apiNames,
                             uint32_t apiNamesSize,
                             omni::vector<omni::fabric::PathC>& outPaths) noexcept = 0;
};

} // namespace usdrt

#include "IRtStage107.gen.h"
