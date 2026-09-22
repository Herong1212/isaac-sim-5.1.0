// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// Purposely missing #pragma once so it can be included multiple times
#if defined DOXYGEN_BUILD
#    include "../../carb/Defines.h"
#endif

#if !OMNI_MOF && !defined __INTELLISENSE__
#    error Should only be included from MoveOnlyFunction.h
#endif

#include "MoveOnlyFunctionStorage.h"

#ifndef OMNI_MOF_CV
#    define OMNI_MOF_CV
#endif
#ifndef OMNI_MOF_REF
#    define OMNI_MOF_REF
#endif
#ifndef OMNI_MOF_MOVE
#    define OMNI_MOF_MOVE
#endif
#ifndef OMNI_MOF_NOEX
#    define OMNI_MOF_NOEX
#endif

namespace omni
{

template <typename T>
class move_only_function;

/**
 * @brief A move-only function wrapper that can store and invoke callable objects.
 *        Doesn't require the callable to be copyable. Respects cv qualifications and noexcept.
 *        Specialization for noexcept(false).
 *
 * @tparam Ret The return type of the callable object.
 * @tparam Args The argument types of the callable object.
 */

template <typename Ret, typename... Args>
class move_only_function<Ret(Args...) OMNI_MOF_CV OMNI_MOF_REF OMNI_MOF_NOEX>
{
public:
    /**
     * @brief Default constructor.
     *
     * Constructs an empty `move_only_function` object.
     */
    move_only_function() = default;

    /**
     * @brief Constructor for nullptr
     *
     * Constructs an empty `move_only_function` object.
     */
    move_only_function(std::nullptr_t) noexcept {};

    CARB_PREVENT_COPY(move_only_function);


    /**
     * @brief Constructs a `move_only_function` from a callable object.
     *
     * @tparam F The type of the callable object (must not be `move_only_function`)
     * @param f The callable object to store.
     *
     * @note The callable object must not be of the same type as `move_only_function`.
     */
    template <typename F CARB_NO_DOC(, typename = std::enable_if_t<!std::is_same_v<std::decay_t<F>, move_only_function>>)>
    move_only_function(F&& f)
    {
        using Ft = std::decay_t<F>;
        if constexpr (std::is_function_v<std::remove_pointer_t<Ft>> || std::is_member_pointer_v<Ft>)
        {
            if (f == nullptr)
            {
                return;
            }
        }
        m_buf.store<Ft>(std::forward<F>(f));
        m_invoker = &_invoke<OMNI_MOF_CV Ft>;
    }


    /**
     * @brief Move constructor.
     *
     * Moves the contents of another `move_only_function` into this one.
     *
     * @param other The `move_only_function` object to move from.
     */
    move_only_function(move_only_function&& other) noexcept
    {
        *this = std::move(other);
    }


    /**
     * @brief Move assignment operator for `F` that is not identical to move_only_function.
     *
     * @tparam F The type of the callable object.
     * @param f The callable object to store.
     * @return move_only_function& A reference to this `move_only_function` object.
     *
     * @note The callable object must not be of the same type as `move_only_function`.
     */
    template <typename F CARB_NO_DOC(, typename = std::enable_if_t<!std::is_same_v<std::decay_t<F>, move_only_function>>)>
    move_only_function& operator=(F&& f)
    {
        using Ft = std::decay_t<F>;
        if constexpr (std::is_function_v<std::remove_pointer_t<Ft>> || std::is_member_pointer_v<Ft>)
        {
            if (f == nullptr)
            {
                *this = nullptr;
                return *this;
            }
        }
        m_buf.store<Ft>(std::forward<F>(f));
        m_invoker = &_invoke<OMNI_MOF_CV Ft>;
        return *this;
    }

    /**
     * @brief Constructs a std::move_only_function whose target is of type std::decay_t<F> and
     * direct-non-list-initialized with std::forward<CArgs>(args)...
     *
     * @param args Arguments for the constructor of `F`.
     */
    template <typename F, typename... Args_>
    explicit move_only_function(std::in_place_type_t<F>, Args_... args)
    {
        static_assert(std::is_same_v<std::decay_t<F>, F>);
        m_buf.store<F>(std::forward<Args_>(args)...);
        m_invoker = &_invoke<OMNI_MOF_CV F>;
    }

    /**
     * @brief Move assignment operator.
     *
     * Moves the contents of another `move_only_function` into this one.
     *
     * @param other The `move_only_function` object to move from.
     * @return move_only_function& A reference to this `move_only_function` object.
     */

    move_only_function& operator=(move_only_function&& other) noexcept
    {
        if (this != &other)
        {
            m_buf = std::move(other.m_buf);
            m_invoker = std::exchange(other.m_invoker, nullptr);
        }
        return *this;
    }

    /**
    * @brief Destroys the callable if any

    * @tparam std::nullptr_t
    * @return move_only_function& A reference to this `move_only_function` object.
    */
    move_only_function& operator=(std::nullptr_t) noexcept
    {
        m_buf = nullptr;
        m_invoker = nullptr;
        return *this;
    }


    /**
     * @brief Destructor.
     *
     * Destroys the `move_only_function` object, releasing any stored resources.
     */
    ~move_only_function() = default;

    /**
     * @brief Invokes the stored callable object with the provided arguments.
     *        Respects cv and noexcept qualifications
     * @param args The arguments to pass to the callable object.
     * @return Ret The result of the callable object's invocation.
     *
     */
    Ret operator()(Args... args) OMNI_MOF_CV OMNI_MOF_REF OMNI_MOF_NOEX
    {
        return m_invoker(this, std::forward<Args>(args)...);
    }


    /**
     * @brief Equality comparison with `nullptr`.
     *
     * Checks if the `move_only_function` is empty (i.e., does not contain a callable object).
     *
     * @param other The `move_only_function` to compare.
     * @return true If the `move_only_function` is empty.
     * @return false If the `move_only_function` contains a callable object.
     */
    friend bool operator==(const move_only_function& other, std::nullptr_t) noexcept
    {
        return other.m_invoker == nullptr;
    }

    /**
     * @brief Inequality comparison with `nullptr`.
     *
     * Checks if the `move_only_function` is bound.
     *
     * @param other The `move_only_function` to compare.
     * @return true If the `move_only_function` is bound.
     * @return false If the `move_only_function` is unbound.
     */
    friend bool operator!=(const move_only_function& other, std::nullptr_t) noexcept
    {
        return other.m_invoker != nullptr;
    }

    /**
     * @brief Checks if the `move_only_function` contains a callable object.
     *
     * @return true If the `move_only_function` contains a callable object.
     * @return false If the `move_only_function` is empty.
     */
    explicit operator bool() const noexcept
    {
        return m_invoker != nullptr;
    }

private:
    /**
     * @brief Invokes the stored callable object.
     *
     * @tparam Ft The type of the stored callable object.
     * @param self A pointer to the `move_only_function` object.
     * @param args The arguments to pass to the callable object.
     * @return Ret The result of the callable object's invocation.
     */
    template <typename Ft>
    static Ret _invoke(move_only_function OMNI_MOF_CV* self, Args... args) OMNI_MOF_NOEX
    {
        return std::invoke(OMNI_MOF_MOVE(*self->m_buf.template get<Ft>()), std::forward<Args>(args)...);
    }

    //! Buffer for storing the callable object.
    detail::storage<16> m_buf;

    //! Pointer to the function that invokes the callable object.
    Ret (*m_invoker)(move_only_function OMNI_MOF_CV*, Args...) OMNI_MOF_NOEX = nullptr;
};


#undef OMNI_MOF_CV
#undef OMNI_MOF_REF
#undef OMNI_MOF_MOVE
#undef OMNI_MOF_NOEX

} // namespace omni
