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
#include <omni/graph/core/IVariable2.h>

namespace omni
{
namespace graph
{
namespace core
{

OMNI_DECLARE_INTERFACE(IVariable3);

/**
 * @brief Interface extension for IVariable that adds the ability to check if the variable is backed by Usd.
 */
class IVariable3_abi :
    public omni::core::Inherits<omni::graph::core::IVariable2, OMNI_TYPE_ID("omni.graph.core.IVariable3")>
{
protected:
    /**
     * Returns whether the variable has an USD representation on the stage.
     *
     * @return True if the variable is backed by USD, false otherwise.
     */
    virtual bool isBackedByUsd_abi() noexcept = 0;
};


} // namespace core
} // namespace graph
} // namespace omni

#include "IVariable3.gen.h"

/**
 * Implementation of IVariable isBackedByUsd method
 */
#ifndef DOXYGEN_BUILD
inline bool omni::graph::core::IVariable::isBackedByUsd() noexcept
{
    auto v3 = omni::core::cast<omni::graph::core::IVariable3>(this);
    if (v3)
    {
        return v3->isBackedByUsd();
    }
    else
    {
        return true;
    }
}
#endif
