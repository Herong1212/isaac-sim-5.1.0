// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#if !OMNI_MOF && !defined __INTELLISENSE__
#    error Should only be included from MoveOnlyFunction.h
#endif

#include <type_traits>
#include <variant>
#include <utility>
#include <stdexcept>
#include <cstdlib>
#include <array>
#include <new>
#include <cstddef>
#include "../../carb/Memory.h"
#include "../../carb/cpp/TypeTraits.h"

//! \cond DEV
namespace omni::detail
{

/**
 * @brief Throws a `std::bad_alloc` exception or terminates the program if exceptions are disabled.
 *
 * @throws std::bad_alloc if exceptions are enabled and memory allocation fails.
 */

[[noreturn]] inline void bad_alloc()
{
#if CARB_EXCEPTIONS_ENABLED
    throw std::bad_alloc();
#else
    CARB_FATAL_UNLESS(false, "Failed to allocate memory");
    std::terminate(); // Enforce [[noreturn]]
#endif
}

/**
 * @brief A helper struct to obtain the address of various data types inside an std::variant.
 */
struct addr
{
    /**
     * @brief Returns the address of the first element in a mutable std::array.
     *
     * @tparam Size The size of the array.
     * @param arg The array to obtain the address from.
     * @return void* The address of the first element in the array.
     */
    template <size_t Size>
    void* operator()(std::array<std::byte, Size>& arg) const
    {
        return static_cast<void*>(&arg[0]);
    }

    /**
     * @brief Returns the address of a mutable void pointer.
     *
     * @param arg The pointer to obtain the address from.
     * @return void* The address of the pointer.
     */
    void* operator()(void* arg) const
    {
        return arg;
    }
};

struct addr_const
{
    /**
     * @brief Returns the address of the first element in a const std::array.
     *
     * @tparam Size The size of the array.
     * @param arg The array to obtain the address from.
     * @return const void* The address of the first element in the array.
     */
    template <size_t Size>
    const void* operator()(const std::array<std::byte, Size>& arg) const
    {
        return static_cast<const void*>(&arg[0]);
    }

    /**
     * @brief Returns the address of a const void pointer.
     *
     * @param arg The pointer to obtain the address from.
     * @return const void* The address of the pointer.
     */
    const void* operator()(const void* arg) const
    {
        return arg;
    }
};


/**
 * @brief A class to manage move-only storage for a callable. Allocates if exceeds @p Size
 *
 * @tparam Size The maximum size of the object to be stored locally
 */
template <size_t Size>
class storage
{
public:
    /**
     * @brief Default constructor.
     */
    storage() = default;

    CARB_PREVENT_COPY(storage);

    /**
     * @brief Move constructor.
     *
     * @param other The storage object to move from.
     */
    storage(storage&& other) noexcept
    {
        *this = std::move(other);
    }


    /**
     * @brief Move assignment operator.
     *
     * @param other The storage object to move from.
     * @return storage& A reference to this storage object.
     */
    storage& operator=(storage&& other) noexcept
    {
        if (this == &other)
        {
            return *this;
        }
        clear();
        std::swap(m_data, other.m_data);
        m_destroyer = std::exchange(other.m_destroyer, nullptr);
        return *this;
    }

    /**
     * @brief Assignment operator for nullptr_t.
     *
     * @tparam std::nullptr_t.
     * @return storage& A reference to this storage object.
     */
    storage& operator=(std::nullptr_t) noexcept
    {
        clear();
        return *this;
    }

    /**
     * @brief Stores an object of type `T` locally or dynamically, depending on the type and alignment of T and whether
     * T is trivially move-constructible
     *
     * @tparam T The type of the object to store.
     * @tparam Args Types of the arguments to initialise the callable
     * @param args arguments to initialise the callable
     */

    template <typename T, typename... Args>
    void store(Args&&... args)
    {
        using U = std::decay_t<T>;
        static_assert(!std::is_array_v<T>, "T[] is not supported");
        clear();
        if constexpr (_stored_locally<T>())
        {
            m_data = std::array<std::byte, Size>{};
            new (std::visit(addr{}, m_data)) U(std::forward<Args>(args)...);
        }
        else
        {
            m_data = _allocate_and_construct<U>(std::forward<Args>(args)...);
        }
        m_destroyer = [](void* ptr) { _destroy<T>(ptr); };
    }

    /**
     * @brief Clears the stored object, if any.
     */
    void clear() noexcept
    {
        if (m_destroyer)
        {
            m_destroyer(std::visit(addr{}, m_data));
            m_destroyer = nullptr;
        }
        m_data = nullptr;
    }


    /**
     * @brief Retrieves a pointer to the stored object of type `T`.
     *
     * @tparam T The type of the object stored.
     * @return std::decay_t<T>* A pointer to the stored object.
     */
    template <typename T>
    std::decay_t<T>* get() noexcept
    {
        return static_cast<std::decay_t<T>*>(std::visit(addr{}, m_data));
    }

    /**
     * @brief Retrieves a pointer to the stored object of type `T`.
     *
     * @tparam T The type of the object stored.
     * @return const std::decay_t<T>* A const pointer to the stored object.
     */
    template <typename T>
    const std::decay_t<T>* get() const noexcept
    {
        return static_cast<const std::decay_t<T>*>(std::visit(addr_const{}, m_data));
    }

    /**
     * @brief Destructor that clears the stored object.
     */
    ~storage() noexcept
    {
        clear();
    }

private:
    void (*m_destroyer)(void*) = nullptr;
    std::variant<void*, std::array<std::byte, Size>> m_data;


    /**
     * @brief Allocates memory and constructs an object of type `T`.
     *
     * @tparam T The type of the object to construct.
     * @param args Arguments for the constructor
     * @return U* A pointer to the newly constructed object.
     */
    template <typename T, typename... Args>
    static auto* _allocate_and_construct(Args&&... args)
    {
        using U = std::decay_t<T>;
        auto* ptr = carb::allocate(sizeof(U), alignof(U));
        if (!ptr)
        {
            bad_alloc();
        }
        return new (ptr) U(std::forward<Args>(args)...);
    }

    /**
     * @brief Destroys the object of type `T`.
     *
     * @tparam T The type of the object to destroy.
     * @param ptr A pointer to the object to destroy.
     */
    template <typename T>
    static void _destroy(void* ptr) noexcept
    {
        using U = std::decay_t<T>;
        if constexpr (!std::is_trivially_destructible_v<U>)
        {
            static_cast<U*>(ptr)->~U();
        }
        if constexpr (!_stored_locally<U>())
        {
            carb::deallocate(ptr);
        }
    }

    /**
     * @brief Determines if an object of type `T` can be stored locally.
     *
     * @tparam T The type of the object.
     * @return true If the object can be stored locally.
     * @return false Otherwise.
     */
    template <typename T>
    static constexpr bool _stored_locally() noexcept
    {
        using U = std::decay_t<T>;
        return sizeof(U) <= Size && std::is_trivially_move_constructible_v<U> && alignof(U) <= alignof(decltype(m_data));
    }
};


} // namespace omni::detail
//! \endcond
