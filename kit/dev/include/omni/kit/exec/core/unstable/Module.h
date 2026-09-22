// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Module.h
//!
//! @brief Helpers for writing modules/plugins based on @ref omni::kit::exec::core.
#pragma once

#include <omni/graph/exec/unstable/Module.h>
#include <omni/kit/exec/core/unstable/IExecutionControllerFactory.h>

#include <type_traits>

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

#ifndef DOXYGEN_BUILD
namespace detail
{
// overloaded function to handle a clear callback not be given to OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED
void _addClearCallback()
{
}

template <typename Fn>
void _addClearCallback(Fn&& fn)
{
    addClearCallback(std::forward<Fn>(fn));
}

} // namespace detail
#endif

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni


//! Helper macro to ensure EF features are enabled in the current module/plugin.
//!
//! This macro should be called from either @ref carbOnPluginStartup or @c onStarted.
//!
//! If your module/plugin registers EF nodes or passes, you must call this macro.
//!
//! @p moduleName_ is the name of your plugin and is used for debugging purposes.
//!
//! The second argument is optional and points to a callback that will be called when *any other plugin* that also calls
//! @ref OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED is about to be unloaded. The purpose of the callback is to give *this*
//! module a chance to remove any references to objects that contain code that is about to be unloaded.  The signature
//! of the callback is `void(void)`.  See @ref
//! omni::kit::exec::core::unstable::IExecutionControllerFactory::addClearCallback for more details.
#define OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED(moduleName_, ...)                                                         \
    OMNI_GRAPH_EXEC_ON_MODULE_STARTED(moduleName_);                                                                    \
    omni::kit::exec::core::unstable::detail::_addClearCallback(__VA_ARGS__);

//! Helper macro to ensure EF features are safely disabled when the current module/plugin unloads.
//!
//! This macro should be called from either @ref carbOnPluginShutdown or @c onUnload.
//!
//! If your module/plugin registers EF nodes or passes, you must call this macro.
#define OMNI_KIT_EXEC_CORE_ON_MODULE_UNLOAD()                                                                          \
    OMNI_GRAPH_EXEC_ON_MODULE_UNLOAD();                                                                                \
    omni::kit::exec::core::unstable::getExecutionControllerFactory()->clear(                                           \
        omni::kit::exec::core::unstable::detail::getModuleHash());                                                     \
    omni::kit::exec::core::unstable::removeClearCallbacks();
