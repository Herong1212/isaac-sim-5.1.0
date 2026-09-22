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
#include "IRtAttribute.h"

#include <omni/core/IObject.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IFabric.h>

#include <vector>

namespace usdrt
{

// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IRtAttribute105);

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

class IRtAttribute105_abi : public omni::core::Inherits<usdrt::IRtAttribute, OMNI_TYPE_ID("usdrt.IRtAttribute105")>
{
protected: // all ABI functions must always be 'protected'.
    // This should have returned ConstSpanC in the original implementation
    // but it's too late now, so fix it here
    virtual OMNI_ATTR("not_prop") omni::fabric::ConstSpanC getValueGpuRd_abi() noexcept = 0;

    virtual bool isCpuDataValid_abi() noexcept = 0;
    virtual bool isGpuDataValid_abi() noexcept = 0;

    virtual bool updateCpuDataFromGpu_abi() noexcept = 0;
    virtual bool updateGpuDataFromCpu_abi() noexcept = 0;

    // Querying and Editing Connections
    virtual bool addConnection_abi(const omni::fabric::Connection source, ListPosition position) noexcept = 0;
    virtual bool removeConnection_abi(const omni::fabric::Connection source) noexcept = 0;
    virtual bool setConnections_abi(OMNI_ATTR("in, count=size") const omni::fabric::Connection* sources,
                                    uint32_t size) noexcept = 0;
    virtual bool clearConnections_abi() noexcept = 0;
    virtual bool getConnections_abi(OMNI_ATTR("out, count=size") omni::fabric::Connection* sources,
                                    uint32_t size) noexcept = 0;
    virtual bool hasAuthoredConnections_abi() noexcept = 0;
    virtual uint32_t numConnections_abi() noexcept = 0;
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

#include "IRtAttribute105.gen.h"
