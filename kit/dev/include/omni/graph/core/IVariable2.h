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
#include <omni/core/TypeId.h>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/IVariable.h>

namespace omni
{
namespace graph
{
namespace core
{

OMNI_DECLARE_INTERFACE(IVariable2);

/**
 * @brief Interface extension for IVariable that adds the ability to set a variable type
 */
class IVariable2_abi :
    public omni::core::Inherits<omni::graph::core::IVariable, OMNI_TYPE_ID("omni.graph.core.IVariable2")>
{
protected:
    /**
     * Sets the type of the variable.
     *
     * @param[in] type New type for the variable
     *
     * @return True if the type is able to be set, false otherwise
     */
    virtual bool setType_abi(Type type) noexcept = 0;
};


} // namespace core
} // namespace graph
} // namespace omni

#include "IVariable2.gen.h"

/**
 * Implementation of IVariable setType method
 */
#ifndef DOXYGEN_BUILD
inline bool omni::graph::core::IVariable::setType(omni::graph::core::Type type) noexcept
{
    auto v2 = omni::core::cast<omni::graph::core::IVariable2>(this);
    if (v2)
    {
        return v2->setType(type);
    }
    else
    {
        return false;
    }
}
#endif
