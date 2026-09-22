// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#if defined(_MSC_VER)
#    define DISABLE_WARNING_PUSH __pragma(warning(push))
#    define DISABLE_WARNING_POP __pragma(warning(pop))
#    define DISABLE_WARNING(warningNumber) __pragma(warning(disable : warningNumber))

#    define DISABLE_WARNING_UNREFERENCED_VARIABLE DISABLE_WARNING(4101)
#    define DISABLE_WARNING_UNREFERENCED_SET_VARIABLE DISABLE_WARNING(4101)
#    define DISABLE_WARNING_UNREFERENCED_FORMAL_PARAMETER DISABLE_WARNING(4100)
#    define DISABLE_WARNING_UNREFERENCED_FUNCTION DISABLE_WARNING(4505)
#    define DISABLE_WARNING_DANGLING_ELSE
#    define DISABLE_WARNING_WRONG_MACRO_PARAMS DISABLE_WARNING(4003)
#    define DISABLE_WARNING_SIGNED_UNSIGNED_MISMATCH DISABLE_WARNING(4018)

#    define DISABLE_WARNING_TO_FLOAT DISABLE_WARNING(4244)
#    define DISABLE_WARNING_TO_INT DISABLE_WARNING(4267)
#    define DISABLE_WARNING_ARG_TO_FLOAT DISABLE_WARNING(4305)
#    define DISABLE_WARNING_INT_TO_BOOL DISABLE_WARNING(4800)
#    define DISABLE_WARNING_UNSAFE_STD_COPY DISABLE_WARNING(4996)

#    define DISABLE_WARNING_PXR                                                                                        \
        DISABLE_WARNING_TO_FLOAT                                                                                       \
        DISABLE_WARNING_TO_INT                                                                                         \
        DISABLE_WARNING_ARG_TO_FLOAT                                                                                   \
        DISABLE_WARNING_INT_TO_BOOL                                                                                    \
        DISABLE_WARNING_UNSAFE_STD_COPY

// other warnings you want to deactivate...

#elif defined(__GNUC__) || defined(__clang__)
#    define DO_PRAGMA(X) _Pragma(#X)
#    define DISABLE_WARNING_PUSH DO_PRAGMA(GCC diagnostic push)
#    define DISABLE_WARNING_POP DO_PRAGMA(GCC diagnostic pop)
#    define DISABLE_WARNING(warningName) DO_PRAGMA(GCC diagnostic ignored warningName)

#    define DISABLE_WARNING_UNREFERENCED_VARIABLE DISABLE_WARNING("-Wunused-variable")
#    define DISABLE_WARNING_UNREFERENCED_SET_VARIABLE DISABLE_WARNING("-Wunused-but-set-variable")
#    define DISABLE_WARNING_UNREFERENCED_FORMAL_PARAMETER DISABLE_WARNING("-Wunused-parameter")
#    define DISABLE_WARNING_UNREFERENCED_FUNCTION DISABLE_WARNING("-Wunused-function")
#    define DISABLE_WARNING_DANGLING_ELSE DISABLE_WARNING("-Wdangling-else")
#    define DISABLE_WARNING_WRONG_MACRO_PARAMS
#    define DISABLE_WARNING_SIGNED_UNSIGNED_MISMATCH DISABLE_WARNING("-Wsign-compare")

#    define DISABLE_WARNING_DEPECATED_DECLARATIONS DISABLE_WARNING("-Wdeprecated-declarations")
#    define DISABLE_WARNING_UNUSED_LOCAL_TYPEDEFS DISABLE_WARNING("-Wunused-local-typedefs")
#    define DISABLE_WARNING_UNUSED_FUNCTION DISABLE_WARNING("-Wunused-function")

#    define DISABLE_WARNING_PXR                                                                                        \
        DISABLE_WARNING_DEPECATED_DECLARATIONS                                                                         \
        DISABLE_WARNING_UNUSED_LOCAL_TYPEDEFS                                                                          \
        DISABLE_WARNING_UNUSED_FUNCTION

// other warnings you want to deactivate...

#else
#    define DISABLE_WARNING_PUSH
#    define DISABLE_WARNING_POP
#    define DISABLE_WARNING_UNREFERENCED_VARIABLE
#    define DISABLE_WARNING_UNREFERENCED_SET_VARIABLE
#    define DISABLE_WARNING_UNREFERENCED_FORMAL_PARAMETER
#    define DISABLE_WARNING_UNREFERENCED_FUNCTION
#    define DISABLE_WARNING_DANGLING_ELSE
#    define DISABLE_WARNING_WRONG_MACRO_PARAMS
#    define DISABLE_WARNING_SIGNED_UNSIGNED_MISMATCH

#    define DISABLE_WARNING_PXR

// other warnings you want to deactivate...

#endif
