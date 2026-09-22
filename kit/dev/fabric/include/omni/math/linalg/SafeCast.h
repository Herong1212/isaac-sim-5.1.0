// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <pxr/pxr.h>

#include <type_traits>
#include <stdint.h>

// Forward declarations, to avoid needing to include the world.

PXR_NAMESPACE_OPEN_SCOPE

namespace pxr_half
{
class half;
}

using GfHalf = pxr_half::half;

class GfVec2h;
class GfVec2f;
class GfVec2d;
class GfVec2i;

class GfVec3h;
class GfVec3f;
class GfVec3d;
class GfVec3i;

class GfVec4h;
class GfVec4f;
class GfVec4d;
class GfVec4i;

class GfQuath;
class GfQuatf;
class GfQuatd;

class GfMatrix2f;
class GfMatrix2d;

class GfMatrix3f;
class GfMatrix3d;

class GfMatrix4f;
class GfMatrix4d;

PXR_NAMESPACE_CLOSE_SCOPE

namespace omni
{
namespace math
{
namespace linalg
{

class half;

template <typename T, std::size_t N>
class base_vec;

template <typename T>
class vec2;

template <typename T>
class vec3;

template <typename T>
class vec4;

template <typename T>
class quat;

template <typename T, std::size_t N>
class base_matrix;

template <typename T>
class matrix2;

template <typename T>
class matrix3;

template <typename T>
class matrix4;

using vec2h = vec2<half>;
using vec2f = vec2<float>;
using vec2d = vec2<double>;
using vec2i = vec2<int>;

using vec3h = vec3<half>;
using vec3f = vec3<float>;
using vec3d = vec3<double>;
using vec3i = vec3<int>;

using vec4h = vec4<half>;
using vec4f = vec4<float>;
using vec4d = vec4<double>;
using vec4i = vec4<int>;

using quath = quat<half>;
using quatf = quat<float>;
using quatd = quat<double>;

using matrix2f = matrix2<float>;
using matrix2d = matrix2<double>;

using matrix3f = matrix3<float>;
using matrix3d = matrix3<double>;

using matrix4f = matrix4<float>;
using matrix4d = matrix4<double>;

template<typename T>
struct TypeStruct
{
    using type = T;
};

template<typename USD_TYPE>
struct OmniType : TypeStruct<void> {};

template<typename OMNI_TYPE>
struct USDType : TypeStruct<void> {};

template <> struct OmniType<pxr::GfHalf> : TypeStruct<half> {};
template <> struct OmniType<float> : TypeStruct<float> {};
template <> struct OmniType<double> : TypeStruct<double> {};
template <> struct OmniType<int> : TypeStruct<int> {};
template <> struct OmniType<unsigned char> : TypeStruct<unsigned char> {};
template <> struct OmniType<unsigned int> : TypeStruct<unsigned int> {};
template <> struct OmniType<int64_t> : TypeStruct<int64_t> {};
template <> struct OmniType<uint64_t> : TypeStruct<uint64_t> {};
template <> struct OmniType<bool> : TypeStruct<bool> {};

template <> struct OmniType<pxr::GfVec2h> : TypeStruct<vec2h> {};
template <> struct OmniType<pxr::GfVec2f> : TypeStruct<vec2f> {};
template <> struct OmniType<pxr::GfVec2d> : TypeStruct<vec2d> {};
template <> struct OmniType<pxr::GfVec2i> : TypeStruct<vec2i> {};

template <> struct OmniType<pxr::GfVec3h> : TypeStruct<vec3h> {};
template <> struct OmniType<pxr::GfVec3f> : TypeStruct<vec3f> {};
template <> struct OmniType<pxr::GfVec3d> : TypeStruct<vec3d> {};
template <> struct OmniType<pxr::GfVec3i> : TypeStruct<vec3i> {};

template <> struct OmniType<pxr::GfVec4h> : TypeStruct<vec4h> {};
template <> struct OmniType<pxr::GfVec4f> : TypeStruct<vec4f> {};
template <> struct OmniType<pxr::GfVec4d> : TypeStruct<vec4d> {};
template <> struct OmniType<pxr::GfVec4i> : TypeStruct<vec4i> {};

template <> struct OmniType<pxr::GfQuath> : TypeStruct<quath> {};
template <> struct OmniType<pxr::GfQuatf> : TypeStruct<quatf> {};
template <> struct OmniType<pxr::GfQuatd> : TypeStruct<quatd> {};

template <> struct OmniType<pxr::GfMatrix2f> : TypeStruct<matrix2f> {};
template <> struct OmniType<pxr::GfMatrix2d> : TypeStruct<matrix2d> {};

template <> struct OmniType<pxr::GfMatrix3f> : TypeStruct<matrix3f> {};
template <> struct OmniType<pxr::GfMatrix3d> : TypeStruct<matrix3d> {};

template <> struct OmniType<pxr::GfMatrix4f> : TypeStruct<matrix4f> {};
template <> struct OmniType<pxr::GfMatrix4d> : TypeStruct<matrix4d> {};


template <> struct USDType<half> : TypeStruct<pxr::GfHalf> {};
template <> struct USDType<float> : TypeStruct<float> {};
template <> struct USDType<double> : TypeStruct<double> {};
template <> struct USDType<int> : TypeStruct<int> {};
template <> struct USDType<unsigned char> : TypeStruct<unsigned char> {};
template <> struct USDType<unsigned int> : TypeStruct<unsigned int> {};
template <> struct USDType<int64_t> : TypeStruct<int64_t> {};
template <> struct USDType<uint64_t> : TypeStruct<uint64_t> {};
template <> struct USDType<bool> : TypeStruct<bool> {};

template <> struct USDType<vec2h> : TypeStruct<pxr::GfVec2h> {};
template <> struct USDType<vec2f> : TypeStruct<pxr::GfVec2f> {};
template <> struct USDType<vec2d> : TypeStruct<pxr::GfVec2d> {};
template <> struct USDType<vec2i> : TypeStruct<pxr::GfVec2i> {};

template <> struct USDType<vec3h> : TypeStruct<pxr::GfVec3h> {};
template <> struct USDType<vec3f> : TypeStruct<pxr::GfVec3f> {};
template <> struct USDType<vec3d> : TypeStruct<pxr::GfVec3d> {};
template <> struct USDType<vec3i> : TypeStruct<pxr::GfVec3i> {};

template <> struct USDType<vec4h> : TypeStruct<pxr::GfVec4h> {};
template <> struct USDType<vec4f> : TypeStruct<pxr::GfVec4f> {};
template <> struct USDType<vec4d> : TypeStruct<pxr::GfVec4d> {};
template <> struct USDType<vec4i> : TypeStruct<pxr::GfVec4i> {};

template <> struct USDType<quath> : TypeStruct<pxr::GfQuath> {};
template <> struct USDType<quatf> : TypeStruct<pxr::GfQuatf> {};
template <> struct USDType<quatd> : TypeStruct<pxr::GfQuatd> {};

template <> struct USDType<matrix2f> : TypeStruct<pxr::GfMatrix2f> {};
template <> struct USDType<matrix2d> : TypeStruct<pxr::GfMatrix2d> {};

template <> struct USDType<matrix3f> : TypeStruct<pxr::GfMatrix3f> {};
template <> struct USDType<matrix3d> : TypeStruct<pxr::GfMatrix3d> {};

template <> struct USDType<matrix4f> : TypeStruct<pxr::GfMatrix4f> {};
template <> struct USDType<matrix4d> : TypeStruct<pxr::GfMatrix4d> {};


template <typename USD_TYPE>
const typename OmniType<USD_TYPE>::type* safeCastToOmni(const USD_TYPE* p)
{
    return reinterpret_cast<const typename OmniType<USD_TYPE>::type*>(p);
}

template <typename USD_TYPE>
typename OmniType<USD_TYPE>::type* safeCastToOmni(USD_TYPE* p)
{
    return reinterpret_cast<typename OmniType<USD_TYPE>::type*>(p);
}

template <typename USD_TYPE>
const typename OmniType<USD_TYPE>::type& safeCastToOmni(const USD_TYPE& p)
{
    return reinterpret_cast<const typename OmniType<USD_TYPE>::type&>(p);
}

template <typename USD_TYPE>
typename OmniType<USD_TYPE>::type& safeCastToOmni(USD_TYPE& p)
{
    return reinterpret_cast<typename OmniType<USD_TYPE>::type&>(p);
}

template <typename OMNI_TYPE>
const typename USDType<OMNI_TYPE>::type* safeCastToUSD(const OMNI_TYPE* p)
{
    return reinterpret_cast<const typename USDType<OMNI_TYPE>::type*>(p);
}

template <typename OMNI_TYPE>
typename USDType<OMNI_TYPE>::type* safeCastToUSD(OMNI_TYPE* p)
{
    return reinterpret_cast<typename USDType<OMNI_TYPE>::type*>(p);
}

template <typename OMNI_TYPE>
const typename USDType<OMNI_TYPE>::type& safeCastToUSD(const OMNI_TYPE& p)
{
    return reinterpret_cast<const typename USDType<OMNI_TYPE>::type&>(p);
}

template <typename OMNI_TYPE>
typename USDType<OMNI_TYPE>::type& safeCastToUSD(OMNI_TYPE& p)
{
    return reinterpret_cast<typename USDType<OMNI_TYPE>::type&>(p);
}

}
}
}
