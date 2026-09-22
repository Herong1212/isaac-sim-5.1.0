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

namespace omni
{
namespace ext
{

//! Declaration of IExtensionData.
OMNI_DECLARE_INTERFACE(IExtensionData);

//! Information about an extension.
class IExtensionData_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.ext.IExtensionData")>
{
protected:
    //! Access the extension id.  For example: "omni.example.greet".
    //!
    //! @returns The Extension ID. The memory returned is valid for the lifetime of `*this`.
    virtual OMNI_ATTR("c_str, not_null") const char* getId_abi() noexcept = 0;

    //! Access the directory which contains the extension.  For example:
    //! c:/users/ncournia/dev/kit/kit/_build/windows-x86_64/debug/exts/omni.example.greet.
    //!
    //! @returns The Extension Directory. The memory returned is valid for the lifetime of `*this`.
    virtual OMNI_ATTR("c_str, not_null") const char* getDirectory_abi() noexcept = 0;
};

} // namespace ext
} // namespace omni

#include "IExtensionData.gen.h"
