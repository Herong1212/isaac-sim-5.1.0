// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IClearCallback.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::IClearCallback.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace kit
{
namespace exec
{
namespace core
{
namespace unstable
{

class IClearCallback_abi;
class IClearCallback;

//! Interface wrapping a callback (possibly with storage) called when @ref
//! omni::kit::exec::core::unstable::IExecutionControllerFactory::clear is executed.
//!
//! To register a clear callback (and instantiate this interface) call @ref OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED in
//! either a plugin's @ref carbOnPluginStartup or @c onStarted.
class IClearCallback_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                       OMNI_TYPE_ID("omni.kit.exec.core.unstable.IClearCallback")>
{
protected:
    //! Invokes the wrapped function.
    //!
    //! Called by @ref omni::kit::exec::core::unstable::IExecutionControllerFactory::clear.
    //!
    //! @thread_safety omni::kit::exec::core::unstable::IExecutionControllerFactory::clear will never call this method
    //! concurrently.
    virtual void onClear_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref IClearCallback.
using ClearCallbackPtr = omni::core::ObjectPtr<IClearCallback>;

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/kit/exec/core/unstable/IClearCallback.gen.h>

//! @copydoc omni::kit::exec::core::unstable::IClearCallback_abi
class omni::kit::exec::core::unstable::IClearCallback
    : public omni::core::Generated<omni::kit::exec::core::unstable::IClearCallback_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/kit/exec/core/unstable/IClearCallback.gen.h>
