// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Implementation detail

// Note! Intentionally without include guards
// This file is counterpart to PopBadMacros.h

// TL;DR: for header files, include this before, and include PopBadMacros.h after, any of the following:
// * including <cstdio>
// * Use of any of the functions listed below: vsprintf, snprintf, vsnprintf, vfscanf, vscanf, vsscanf
// For source files, you only need to include this in a compilation unit if you have issues. And then it should be
// included before any uses in the list above. There is no need to include PopBadMacros.

// Some naughty files (looking at you pyerrors.h, among others) can define macros of functions that are legitimately
// valid C/C++ functions. Now imagine you have:
// #define vsnprintf my_super_vsnprintf
//
// And then someone include <cstdio> which does
// #pragma once
// namespace std
// {
// using vsnprintf = ::vsnprintf;
// }
//
// Now, you have a symbol called `std::my_super_vsnprintf` instead of `std::vsnprintf` and because of include guards
// cannot fix it for this compilation unit.
// So before we do things like #include <cstdio> we pop the macros here.

#pragma push_macro("vsprintf")
#undef vsprintf

#pragma push_macro("snprintf")
#undef snprintf

#pragma push_macro("vsnprintf")
#undef vsnprintf

#pragma push_macro("vfscanf")
#undef vfscanf

#pragma push_macro("vscanf")
#undef vscanf

#pragma push_macro("vsscanf")
#undef vsscanf
// If something is pushed here, it should be popped in PopBadMacros.h
