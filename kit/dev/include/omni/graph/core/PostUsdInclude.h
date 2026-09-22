// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// This file should be included in conjunction with PreUsdInclude.h when including any of the individual USD
// definition files. This file restores the warnings that were disabled for the inclusion of USD files.
//
// It includes a special ifdef detection to prevent inclusion of this file without PreUsdInclude.h as that
// would have unpredictable effects on the compiler. The usual "#pragma once" is omitted, so that the mechanism works
// correctly even with multiple uses. It is not legal to include anything other than USD headers between these two.
//
// Here is an example of how you use this mechanism to include the definition of the USD type pxr::GfHalf:
//
//  #include <omni/graph/core/PreUsdInclude.h>
//  #include <pxr/base/gf/half.h>
//  #include <omni/graph/core/PostUsdInclude.h>
//
#ifdef _MSC_VER
#    pragma warning(pop)
#elif defined(__GNUC__)
#    pragma GCC diagnostic pop
#    ifdef OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#        define __DEPRECATED
#        undef OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#    endif
#endif

#ifdef __USD_INCLUDE_PROTECTION__
#   undef __USD_INCLUDE_PROTECTION__
#else
#   error "You must include PreUsdInclude.h before including PostUsdInclude.h"
#endif
