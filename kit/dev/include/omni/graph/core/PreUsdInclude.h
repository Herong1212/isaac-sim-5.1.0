// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// This file should be included in conjunction with PostUsdInclude.h when including any of the individual USD
// definition files. They have a number of warnings that are triggered by our default build configuration that these
// files silence as being third party includes we can't fix them ourselves.
//
// It includes a special ifdef detection to prevent inclusion of this file without PostUsdInclude.h as that
// would have unpredictable effects on the compiler. The usual "#pragma once" is omitted, so that the mechanism works
// correctly even with multiple uses. It is not legal to include anything other than USD headers between these two.
//
// Here is an example of how you use this mechanism to include the definition of the USD type pxr::GfHalf:
//
//  #include <omni/graph/core/PreUsdInclude.h>
//  #include <pxr/base/gf/half.h>
//  #include <omni/graph/core/PostUsdInclude.h>
//
// NOTE: At some point when USD is upgraded these might no longer be required; at that time they can be deprecated
//
#ifdef _MSC_VER
#    pragma warning(push)
#    pragma warning(disable : 4244) // = Conversion from double to float / int to float
#    pragma warning(disable : 4267) // conversion from size_t to int
#    pragma warning(disable : 4305) // argument truncation from double to float
#    pragma warning(disable : 4800) // int to bool
#    pragma warning(disable : 4996) // call to std::copy with parameters that may be unsafe
#    pragma warning(disable : 4003) // not enough arguments for function-like macro invocation
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif
#elif defined(__GNUC__)
#    pragma GCC diagnostic push
#    pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#    pragma GCC diagnostic ignored "-Wunused-local-typedefs"
#    pragma GCC diagnostic ignored "-Wunused-function"
#    pragma GCC diagnostic ignored "-Wunused-variable"
// This suppresses deprecated header warnings, which is impossible with pragmas.
// Alternative is to specify -Wno-deprecated build option, but that disables other useful warnings too.
#    ifdef __DEPRECATED
#        define OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#        undef __DEPRECATED
#    endif
#endif

#ifdef __USD_INCLUDE_PROTECTION__
#   error "You must include PostUsdInclude.h after including PreUsdInclude.h"
#else
#   define __USD_INCLUDE_PROTECTION__
#endif
