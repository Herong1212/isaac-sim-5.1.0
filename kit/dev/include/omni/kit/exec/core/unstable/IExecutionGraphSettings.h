// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionGraphSettings.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::IExecutionGraphSettings.
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

// forward declarations needed by interface declaration
class IExecutionGraphSettings;
class IExecutionGraphSettings_abi;

//! Interface for accessing global execution graph settings.
//!
//! This interface is a singleton. The settings are applied to all graphs.
//!
//! Access the singleton with @ref omni::kit::exec::core::unstable::getExecutionGraphSettings().
class IExecutionGraphSettings_abi
    : public omni::core::Inherits<graph::exec::unstable::IBase,
                                  OMNI_TYPE_ID("omni.kit.exec.core.unstable.IExecutionGraphSettings")>
{
protected:
    //! If @c true all tasks will skip the scheduler and be executed immediately.
    virtual bool shouldForceSerial_abi() noexcept = 0;

    //! If @c true all tasks will be given to the scheduler and marked as being able to execute in parallel.
    virtual bool shouldForceParallel_abi() noexcept = 0;
};

//! Returns the @ref omni::kit::exec::core::unstable::IExecutionGraphSettings singleton.
//!
//! May return @c nullptr if the *omni.kit.exec.core* extension has not been loaded.
//!
//! The returned pointer does not have @ref omni::core::IObject::acquire() called on it.
inline IExecutionGraphSettings* getExecutionGraphSettings() noexcept;

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/kit/exec/core/unstable/IExecutionGraphSettings.gen.h>

//! @copydoc omni::kit::exec::core::unstable::IExecutionGraphSettings_abi
//!
//! @ingroup groupOmniKitExecCoreInterfaces
class omni::kit::exec::core::unstable::IExecutionGraphSettings
    : public omni::core::Generated<omni::kit::exec::core::unstable::IExecutionGraphSettings_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IDef.h>

inline omni::kit::exec::core::unstable::IExecutionGraphSettings* omni::kit::exec::core::unstable::getExecutionGraphSettings() noexcept
{
    // createType() always calls acquire() and returns an ObjectPtr to make sure release() is called. we don't want
    // to hold a ref here to avoid static destruction issues. here we allow the returned ObjectPtr to destruct
    // (after calling get()) to release our ref. we know the DLL in which the singleton was created is maintaining a
    // ref and will keep the singleton alive for the lifetime of the DLL.
    static auto* sSingleton = omni::core::createType<IExecutionGraphSettings>().get();
    return sSingleton;
}

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/kit/exec/core/unstable/IExecutionGraphSettings.gen.h>
