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
#include <omni/fabric/IFabric.h>
#include <usdrt/gf/vec.h>

namespace usdrt
{


// we must always forward declare each interface that will be referenced here.
OMNI_DECLARE_INTERFACE(IGeoPriority);


class IGeoPriority_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.IGeoPriority")>
{
protected: // all ABI functions must always be 'protected'.
    virtual IGeoPriority* create_abi(omni::fabric::StageReaderWriterId stageReaderWriterId) noexcept = 0;

    virtual const GfVec3f* getCenter_abi() const noexcept = 0;
    virtual void setCenter_abi(OMNI_ATTR("in, not_null") const GfVec3f*) noexcept = 0;

    virtual float getSolidAngleLimit_abi() const noexcept = 0;
    virtual void setSolidAngleLimit_abi(float) noexcept = 0;

    virtual bool readFromFabric_abi() noexcept = 0;
    virtual bool compute_abi() noexcept = 0;

    virtual size_t getNumberOfPathsAboveLimit_abi() const noexcept = 0;

    virtual OMNI_ATTR("no_py") omni::fabric::ConstSpanC getSortedPaths_abi() const noexcept = 0;

    virtual OMNI_ATTR("no_py") omni::fabric::ConstSpanC getSortedPriorities_abi() const noexcept = 0;
};


} // namespace usdrt

#include "IGeoPriority.gen.h"
