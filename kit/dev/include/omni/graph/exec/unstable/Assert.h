// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Assert.h
//!
//! @brief Defines macros for assertions.
#pragma once

#include <carb/Defines.h>
#include <carb/extras/Debugging.h>

#include <omni/Expected.h>
#include <omni/core/Assert.h>
#include <omni/core/ResultError.h>
#include <omni/graph/exec/unstable/IBase.h>

//! @defgroup groupOmniGraphExecAssert Error Checking
//!
//! @brief Macros/Functions related to error checking.
//!
//! See @rstref{Error Handling<ef_error_handling>} to understand Execution Framework's error handling/reporting
//! approach.

//! Debug build assertion.
//!
//! This assertion is only active in debug builds.
//!
//! See @rstref{Error Handling<ef_error_handling>} to understand when it is appropriate to use this macro.
//!
//! @ingroup  groupOmniGraphExecAssert
#define OMNI_GRAPH_EXEC_ASSERT(cond, ...) OMNI_ASSERT(cond, ##__VA_ARGS__)

//! Check if the given argument is @c nullptr, and if so terminates the application.
//!
//! See @rstref{Error Handling<ef_error_handling>} to understand when it is appropriate to use this macro.
//!
//! @ingroup  groupOmniGraphExecAssert
#define OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(arg_)                                                                         \
    OMNI_FATAL_UNLESS((arg_), "argument '" CARB_STRINGIFY(arg_) "' must not be null")

//! Check if the given expression evaluates to `true`, and if not, terminates the application.
//!
//! See @rstref{Error Handling<ef_error_handling>} to understand when it is appropriate to use this macro.
//!
//! @ingroup  groupOmniGraphExecAssert
#define OMNI_GRAPH_EXEC_FATAL_UNLESS(arg_, ...) OMNI_FATAL_UNLESS((arg_), "'" CARB_STRINGIFY(arg_) "' must be true")

//! Terminates the application due to an unexpected condition.
//!
//! The given message will be printed to the terminal.
//!
//! @ingroup  groupOmniGraphExecAssert
#define OMNI_GRAPH_EXEC_FATAL(msg_) OMNI_FATAL_UNLESS(false, msg_)

//! Casts an object to the specified interface, terminating the application if the cast fails.
//!
//! Calls @ref omni::graph::exec::unstable::cast() on @p obj_, in an attempt to cast @p obj_ to an interface pointer of
//! type @p type_.
//!
//! The result of the operation is stored in @p var_, which is a variable allocated by this macro and useable any code
//! called after the macro in the same scope.
//!
//! If the cast fails, the application is terminated.
//!
//! @ingroup  groupOmniGraphExecAssert
#define OMNI_GRAPH_EXEC_CAST_OR_FATAL(var_, type_, obj_)                                                               \
    auto var_ = omni::graph::exec::unstable::cast<type_>(obj_);                                                        \
    OMNI_FATAL_UNLESS((var_), "'" CARB_STRINGIFY(obj_) "' must implement the '" CARB_STRINGIFY(type_) "' interface")

//! At compile-time, check if the given type can safely be copied by value across the ABI.
//!
//! For a type to safely passed across the ABI, the type must be:
//!
//! - <a href="https://en.cppreference.com/w/cpp/named_req/StandardLayoutType">Standard Layout</a> so that the
//!   layout of members in the type fall into predictable locations.
//!
//! - <a href="https://en.cppreference.com/w/cpp/named_req/TriviallyCopyable">Trivially Copyable</a> so that the
//!   type can be copied outside of non-C++ environments.
//!
//! - <a href="https://en.cppreference.com/w/cpp/language/destructor#Trivial_destructor">Trivially
//!   Destructible</a> so that temporary copies can be safely created (and destructed) when interoperating between
//!   language runtimes.
#define OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI(type_)                                                        \
    static_assert(std::is_standard_layout<type_>::value,                                                               \
                  CARB_STRINGIFY(type_) " is expected to be passable by value in the abi (standard layout)");          \
    static_assert(std::is_trivially_copyable<type_>::value,                                                            \
                  CARB_STRINGIFY(type_) " is expected to be passable by value in the abi (trivially copyable)");       \
    static_assert(std::is_trivially_destructible<type_>::value,                                                        \
                  CARB_STRINGIFY(type_) " is expected to be passable by value in the abi (trivially destructible)")

//! At compile-time, check if the given type must be passed by pointer in the ABI.
//!
//! For a type to safely passed across the ABI, the type must be:
//!
//! - <a href="https://en.cppreference.com/w/cpp/named_req/StandardLayoutType">Standard Layout</a> so that the
//!   layout of members in the type fall into predictable locations.
#define OMNI_STATIC_ASSERT_MUST_BE_PASSED_BY_POINTER_IN_ABI(type_)                                                     \
    static_assert(std::is_standard_layout<type_>::value,                                                               \
                  CARB_STRINGIFY(type_) " is expected to be passable by pointer in the abi (standard layout)");        \
    static_assert(!(std::is_trivially_copyable<type_>::value && std::is_trivially_destructible<type_>::value),         \
                  CARB_STRINGIFY(type_) " can be passed by value in the ABI but is not marked as so")

//! Returns an @ref omni::expected with the proper expected or unexpected value.
//!
//! This is a helper macro that cuts down of the amount of boiler-plate code needed when returning @ref omni::expected.
//!
//! @p expected_ can be any type.
//!
//! @p unexpected_ must be a @ref omni::core::Result.
//!
//! If @p unexpected_ passes @ref OMNI_SUCCEEDED(), @p exepected_ is returned as the expected value.  Otherwise, @p
//! unexpected_ is returned as the unexpected value.
#define OMNI_GRAPH_EXEC_RETURN_EXPECTED(expected_, unexpected_)                                                        \
    do                                                                                                                 \
    {                                                                                                                  \
        auto result_ = (unexpected_);                                                                                  \
        if (OMNI_SUCCEEDED(result_))                                                                                   \
        {                                                                                                              \
            return omni::expected<decltype(expected_), omni::core::Result>(expected_);                                 \
        }                                                                                                              \
        else                                                                                                           \
        {                                                                                                              \
            return omni::unexpected<omni::core::Result>(result_);                                                      \
        }                                                                                                              \
    } while (0)
