// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include <omni/core/Types.h>

#include <cstdint>
#include <type_traits>

namespace omni::sensors::net
{

OMNI_DECLARE_INTERFACE(IBufferCapsule);

/**
 * A polymorphic owner of buffers
 * @note expected to dispose/free/release it's underlying implementation
 * when destroyed. Best passed around as a @ref IBufferCapsulePtr
 */
class OMNI_ATTR("no_py") IBufferCapsule_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IBufferCapsule")>
{
protected:
    /**
     * Get a mutable view of the underlying buffer
     * @return a pointer to the underlying buffer
     */
    virtual void* data_abi() noexcept = 0;

    /**
     * Get the size of the actual data, regardless of the implementation
     * @return size of data in bytes
     */
    virtual size_t size_abi() noexcept = 0;

    /**
     * Set the size of the actual data, regardless of the implementation
     * @param size size of the actual data in bytes
     */
    virtual void setSize_abi(size_t size) noexcept = 0;
};

using IBufferCapsulePtr = omni::core::ObjectPtr<IBufferCapsule>;

} // namespace omni::sensors::net

#include "IBufferCapsule.gen.h"

OMNI_DEFINE_INTERFACE_API(omni::sensors::net::IBufferCapsule)
#ifdef CLANG_FORMAT /* Fix clang format bug. */
class omni::sensors::net::IBufferCapsule
#endif
{
public:
    /**
     *  Cast buffer to T&
     *
     * @tparam T the type to cast to
     * @returns the underlying buffer casted to T&
     *
     *
     * Usage:
     *
     * @code{.cpp}
     *
     * S& s = capsule->as<S>();
     *
     * @endcode
     *
     * @note this is equivalent to:
     *
     * @code{.cpp}
     *
     * S& s = *static_cast<S*>(capsule->data());
     *
     * @endcode
     *
     */
    template <typename T, typename = std::enable_if_t<!std::is_pointer<T>::value>>
    T& as()
    {
        const size_t actual = size_abi();
        constexpr const size_t expected = sizeof(T);

        CARB_CHECK(actual >= expected, "capsule size is: %lu, but sizeof(T) is: %lu", actual, expected);

        return *static_cast<std::add_pointer_t<T>>(data_abi());
    }

    /**
     *  Cast buffer to pointer (when T is a pointer)
     *
     * @tparam T the pointer to cast to
     * @returns the underlying buffer casted to T
     *
     * Usage:
     *
     * @code{.cpp}
     *
     * S* s = capsule->as<S*>();
     *
     * @endcode
     *
     * @note this is equivalent to:
     *
     * @code{.cpp}
     *
     * S* s = static_cast<S*>(capsule->data());
     *
     * @endcode
     *
     */
    template <typename T, typename = std::enable_if_t<std::is_pointer<T>::value>>
    T as()
    {
        const size_t actual = size_abi();
        constexpr const size_t expected = sizeof(std::remove_pointer_t<T>);

        CARB_CHECK(actual >= expected, "capsule size is: %lu, but sizeof(T) is: %lu", actual, expected);

        return static_cast<T>(data_abi());
    }
};
