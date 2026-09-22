// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <omni/core/IObject.h>
#include <omni/ext/IExtensionData.h>

namespace omni
{
namespace ext
{

//! Declaration of IExtensionHooks
OMNI_DECLARE_INTERFACE(IExtensionHooks);

//! Hooks that can be defined by plugins to better understand how the plugin is being used by the extension system.
class IExtensionHooks_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.ext.IExtensionHooks")>
{
protected:
    //! Called when an extension loads the plugin.
    //!
    //! If multiple extensions load the plugin, this method will be called multiple times.
    //! @param ext The \ref IExtensionData_abi of the starting extension
    virtual void onStartup_abi(OMNI_ATTR("not_null") IExtensionData* ext) noexcept = 0;

    //! Called when an extension that uses this plugin is unloaded.
    //!
    //! If multiple extension load the plugin, this method will be called multiple times.
    //! @param ext The \ref IExtensionData_abi of the extension that is shutting down
    virtual void onShutdown_abi(IExtensionData* ext) noexcept = 0;
};

} // namespace ext
} // namespace omni

#include "IExtensionHooks.gen.h"
