// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <type_traits>

namespace usdrt
{

/// A metafunction with a static const bool member 'value' that is true for
/// GfVec types, like GfVec2i, GfVec4d, etc and false for all other types.
template <class T>
struct GfIsGfVec
{
    static const bool value = false;
};

/// A metafunction with a static const bool member 'value' that is true for
/// GfMatrix types, like GfMatrix3d, GfMatrix4f, etc and false for all other
/// types.
template <class T>
struct GfIsGfMatrix
{
    static const bool value = false;
};

/// A metafunction with a static const bool member 'value' that is true for
/// GfQuat types and false for all other types.
template <class T>
struct GfIsGfQuat
{
    static const bool value = false;
};

/// A metafunction with a static const bool member 'value' that is true for
/// GfDualQuat types and false for all other types.
template <class T>
struct GfIsGfDualQuat
{
    static const bool value = false;
};

/// A metafunction with a static const bool member 'value' that is true for
/// GfRange types and false for all other types.
template <class T>
struct GfIsGfRange
{
    static const bool value = false;
};

/// A metafunction which is equivalent to std::is_floating_point but
/// allows for additional specialization for types like GfHalf
template <class T>
struct GfIsFloatingPoint : public std::is_floating_point<T>
{
};

/// A metafunction which is equivalent to std::arithmetic but
/// also includes any specializations from GfIsFloatingPoint (like GfHalf)
template <class T>
struct GfIsArithmetic : public std::integral_constant<bool, GfIsFloatingPoint<T>::value || std::is_arithmetic<T>::value>
{
};

}
