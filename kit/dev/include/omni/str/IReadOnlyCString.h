// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Interface to manage access to a read-only string.
#pragma once

#include "../core/IObject.h"
#include "../../carb/Defines.h"

namespace omni
{
//! Namespace for various string helper classes, interfaces, and functions.
namespace str
{

//! Forward declaration of the IReadOnlyCString.
OMNI_DECLARE_INTERFACE(IReadOnlyCString);

//! Reference counted read-only C-style (i.e. null-terminated) string.
class IReadOnlyCString_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.str.IReadOnlyCString")>
{
protected:
    //! Returns a pointer to the null-terminated string.
    //!
    //! The returned pointer is valid for the lifetime of this object.
    //!
    //! This method is thread safe.
    virtual OMNI_ATTR("c_str, not_null") const char* getBuffer_abi() noexcept = 0;
};

} // namespace str
} // namespace omni

#include "IReadOnlyCString.gen.h"

namespace omni
{
namespace str
{

//! Concrete implementation of the IReadOnlyCString interface.
class ReadOnlyCString : public omni::core::Implements<omni::str::IReadOnlyCString>
{
public:
    //! Creates a read-only string.  The given string is copied and must not be nullptr.
    static omni::core::ObjectPtr<IReadOnlyCString> create(const char* str)
    {
        OMNI_ASSERT(str, "ReadOnlyCString: the given string must not be nullptr");
        return { new ReadOnlyCString{ str }, omni::core::kSteal };
    }

private:
    ReadOnlyCString(const char* str) : m_buffer{ str }
    {
    }

    const char* getBuffer_abi() noexcept override
    {
        return m_buffer.c_str();
    }

    CARB_PREVENT_COPY_AND_MOVE(ReadOnlyCString);

    std::string m_buffer;
};

} // namespace str
} // namespace omni
