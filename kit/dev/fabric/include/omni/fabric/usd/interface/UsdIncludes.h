// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

// The following is needed to include USD headers
#ifdef _MSC_VER
#    pragma warning(push)
#    pragma warning(disable : 4003) // not enough arguments for function-like macro invocation
#    pragma warning(disable : 4244) // = Conversion from double to float / int to float
#    pragma warning(disable : 4267) // conversion from size_t to int
#    pragma warning(disable : 4305) // argument truncation from double to float
#    pragma warning(disable : 4800) // int to bool
#    pragma warning(disable : 4996) // call to std::copy with parameters that may be unsafe
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif
#    include <Windows.h> // Include this here so we can curate
#    undef small // defined in rpcndr.h
#elif defined(__GNUC__)
#    pragma GCC diagnostic push
#    pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#    pragma GCC diagnostic ignored "-Wunused-local-typedefs"
#    pragma GCC diagnostic ignored "-Wunused-function"
// This suppresses deprecated header warnings, which is impossible with pragmas.
// Alternative is to specify -Wno-deprecated build option, but that disables other useful warnings too.
#    ifdef __DEPRECATED
#        define OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#        undef __DEPRECATED
#    endif
#endif

#include <pxr/pxr.h>

#ifdef PXR_PYTHON_SUPPORT_ENABLED
// Python must be included first because it monkeys with macros that cause
// TBB to fail to compile in debug mode if TBB is included before Python
//
// NOTE: This "fix" is derived from UsdPCH.h
#    include <boost/python/object.hpp>
#endif

#include <pxr/usd/usd/prim.h>
#include <pxr/usd/sdf/valueTypeName.h>
#include <pxr/base/tf/type.h>
#include <pxr/base/tf/token.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/notice.h>
#ifdef _MSC_VER
#    pragma warning(pop)
#elif defined(__GNUC__)
#    pragma GCC diagnostic pop
#    ifdef OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#        define __DEPRECATED
#        undef OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#    endif
#endif
