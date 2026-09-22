// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnAnyZeroDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

static constexpr char kValueTypeUnresolved[] = "Failed to resolve type of 'value' input";

//  Check whether a scalar attribute contains a value which lies within 'tolerance' of 0.
//
//  'tolerance' must be non-negative. It is ignored for bool values.
//  'isZero' will be set true if 'value' contains a zero value, false otherwise.
//
//  The return value is true if 'value' is a supported scalar type, false otherwise.
//
bool checkScalarForZero(OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& isZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    switch (value.type().baseType)
    {
    case BaseDataType::eBool:
        isZero = !*(value.get<bool>());
        break;
    case BaseDataType::eDouble:
        isZero = std::abs(*(value.get<double>())) <= tolerance;
        break;
    case BaseDataType::eFloat:
        isZero = std::abs(*(value.get<float>())) <= tolerance;
        break;
    case BaseDataType::eHalf:
        isZero = std::abs(*(value.get<pxr::GfHalf>())) <= tolerance;
        break;
    case BaseDataType::eInt:
        isZero = std::abs(*(value.get<int32_t>())) <= (int32_t)tolerance;
        break;
    case BaseDataType::eInt64:
        isZero = std::abs(*(value.get<int64_t>())) <= (int64_t)tolerance;
        break;
    case BaseDataType::eUChar:
        isZero = *(value.get<unsigned char>()) <= (unsigned char)tolerance;
        break;
    case BaseDataType::eUInt:
        isZero = *(value.get<uint32_t>()) <= (uint32_t)tolerance;
        break;
    case BaseDataType::eUInt64:
        isZero = *(value.get<uint64_t>()) <= (uint64_t)tolerance;
        break;
    default:
        return false;
    }

    return true;
}

//  Check whether a tuple attribute contains a value with at least one zero component
//  (i.e. its value lies within 'tolerance' of 0).
//
//  T - type of the components of the tuple.
//  N - number of components in the tuple
//
//  'tolerance' must be non-negative
//  'hasZero' is assumed to be false on entry and will be set true if any component of the tuple is zero.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
template <typename T, int N>
bool checkTupleForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& hasZero)
{
    CARB_ASSERT(tolerance >= 0.0);
    CARB_ASSERT(!hasZero);

    if (auto const tuple = value.get<T[N]>())
    {
        for (int i = 0; !hasZero && (i < N); ++i)
        {
            hasZero = (std::abs(tuple[i]) <= tolerance);
        }

        return true;
    }

    return false;
}

//  Check whether a tuple attribute contains a value with at least one zero component
//  (i.e. its value lies within 'tolerance' of 0).
//
//  'tolerance' must be non-negative
//  'hasZero' is assumed to be false on entry and will be set true if any component of the tuple is zero.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
bool checkTupleForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& hasZero)
{
    CARB_ASSERT(tolerance >= 0.0);
    CARB_ASSERT(!hasZero);

    switch (value.type().baseType)
    {
    case BaseDataType::eDouble:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleForZeroes<double, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleForZeroes<double, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleForZeroes<double, 4>(value, tolerance, hasZero);
        case 9:
            return checkTupleForZeroes<double, 9>(value, tolerance, hasZero);
        case 16:
            return checkTupleForZeroes<double, 16>(value, tolerance, hasZero);
        }
        break;
    case BaseDataType::eFloat:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleForZeroes<float, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleForZeroes<float, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleForZeroes<float, 4>(value, tolerance, hasZero);
        }
        break;
    case BaseDataType::eHalf:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleForZeroes<pxr::GfHalf, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleForZeroes<pxr::GfHalf, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleForZeroes<pxr::GfHalf, 4>(value, tolerance, hasZero);
        }
        break;
    case BaseDataType::eInt:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleForZeroes<int32_t, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleForZeroes<int32_t, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleForZeroes<int32_t, 4>(value, tolerance, hasZero);
        }
        break;
    default:
        break;
    }

    return false;
}

//  Check whether an unsigned array attribute contains at least one element with a value of zero
//  (i.e. it lies within 'tolerance' of 0).
//
//  T - type of the elements of the array.  Must be an unsigned type, other than bool.
//
//  'tolerance' must be non-negative
//  'hasZero' will be set true if any element of the array is zero, false otherwise.
//
//  The return value is true if 'value' is a supported integer array type, false otherwise.
//
template <typename T>
bool checkUnsignedArrayForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& hasZero)
{
    static_assert(std::is_unsigned<T>::value && !std::is_same<T, bool>::value, "Unsigned integer type required.");
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const array = value.get<T[]>())
    {
        hasZero =
            std::any_of(array->begin(), array->end(), [tolerance](auto element) { return element <= (T)tolerance; });
        return true;
    }

    return false;
}

//  Check whether a bool array attribute contains at least one element with a value of zero (i.e. false).
//  No tolerance value is applied since tolerance is meaningless for bool.
//
//  'hasZero' will be set true if any element of the array is zero, false otherwise.
//
//  The return value is true if 'value' is a bool array type, false otherwise.
//
bool checkBoolArrayForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, bool& hasZero)
{
    if (auto const array = value.get<bool[]>())
    {
        hasZero = std::any_of(array->begin(), array->end(), [](auto element) { return !element; });
        return true;
    }

    return false;
}

//  Check whether a signed array attribute contains at least one element with a value of zero
//  (i.e. its value lies within 'tolerance' of 0).
//
//  T - type of the elements of the array. Must be a decimal type.
//
//  'tolerance' must be non-negative
//  'hasZero' will be set true if any element of the array is zero, false otherwise.
//
//  The return value is true if 'value' is a supported decimal array type, false otherwise.
//
template <typename T>
bool checkSignedArrayForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& hasZero)
{
    static_assert(
        std::is_signed<T>::value || pxr::GfIsFloatingPoint<T>::value, "Signed integer or decimal type required.");
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const array = value.get<T[]>())
    {
        hasZero = std::any_of(
            array->begin(), array->end(), [tolerance](auto element) { return (std::abs(element) <= tolerance); });
        return true;
    }

    return false;
}

//  Check whether a scalar array attribute contains at least one element with a value of zero
//  (i.e. its value lies within 'tolerance' of 0).
//
//  'tolerance' must be non-negative
//  'hasZero' will be set true if any element of the array is zero, false otherwise.
//
//  The return value is true if 'value' is a supported scalar array type, false otherwise.
//
bool checkScalarArrayForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& hasZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    switch (value.type().baseType)
    {
    case BaseDataType::eBool:
        return checkBoolArrayForZeroes(value, hasZero);
    case BaseDataType::eDouble:
        return checkSignedArrayForZeroes<double>(value, tolerance, hasZero);
    case BaseDataType::eFloat:
        return checkSignedArrayForZeroes<float>(value, tolerance, hasZero);
    case BaseDataType::eHalf:
        return checkSignedArrayForZeroes<pxr::GfHalf>(value, tolerance, hasZero);
    case BaseDataType::eInt:
        return checkSignedArrayForZeroes<int32_t>(value, tolerance, hasZero);
    case BaseDataType::eInt64:
        return checkSignedArrayForZeroes<int64_t>(value, tolerance, hasZero);
    case BaseDataType::eUChar:
        return checkUnsignedArrayForZeroes<unsigned char>(value, tolerance, hasZero);
    case BaseDataType::eUInt:
        return checkUnsignedArrayForZeroes<uint32_t>(value, tolerance, hasZero);
    case BaseDataType::eUInt64:
        return checkUnsignedArrayForZeroes<uint64_t>(value, tolerance, hasZero);
    default:
        break;
    }

    return false;
}

//  Returns true if all components of the tuple are zero.
//  (i.e. they lie within 'tolerance' of 0).
//
//  T - base type of the tuple (e.g. float if tuple is float[2]).
//  N - number of components in the tuple (e.g. '2' in the example above).
//
//  'tolerance' must be non-negative
//
template <typename T, int N>
bool isTupleZero(const T tuple[N], double tolerance)
{
    CARB_ASSERT(tolerance >= 0.0);

    for (int i = 0; i < N; ++i)
    {
        if (std::abs(tuple[i]) > tolerance)
            return false;
    }

    return true;
}

//  Check whether a tuple array attribute contains at least one element which is zero
//  (i.e. all of their components are within 'tolerance' of 0).
//
//  T - type of the components of the tuple. Must be a decimal type.
//  N - number of components in the tuple
//
//  'tolerance' must be non-negative
//  'hasZero' will be set true if any tuple in the array is zero, false otherwise.
//
//  The return value is true if 'value' is a supported decimal tuple array type, false otherwise.
//
template <typename T, int N>
bool checkTupleArrayForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, double tolerance, bool& hasZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const array = value.get<T[][N]>())
    {
        hasZero = std::any_of(
            array->begin(), array->end(), [tolerance](auto element) { return isTupleZero<T, N>(element, tolerance); });
        return true;
    }

    return false;
}

//  Check whether a tuple array attribute contains at least one element which is zero
//  (i.e. all of their components are within 'tolerance' of 0).
//
//  'tolerance' must be non-negative
//  'hasZero' will be set true if any tuple in the array is zero, false otherwise.
//
//  The return value is true if 'value' is a supported decimal tuple array type, false otherwise.
//
bool checkTupleArrayForZeroes(const OgnAnyZeroAttributes::inputs::value_t& value, const double& tolerance, bool& hasZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    switch (value.type().baseType)
    {
    case BaseDataType::eDouble:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleArrayForZeroes<double, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleArrayForZeroes<double, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleArrayForZeroes<double, 4>(value, tolerance, hasZero);
        case 9:
            return checkTupleArrayForZeroes<double, 9>(value, tolerance, hasZero);
        case 16:
            return checkTupleArrayForZeroes<double, 16>(value, tolerance, hasZero);
        }
        break;
    case BaseDataType::eFloat:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleArrayForZeroes<float, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleArrayForZeroes<float, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleArrayForZeroes<float, 4>(value, tolerance, hasZero);
        }
        break;
    case BaseDataType::eHalf:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleArrayForZeroes<pxr::GfHalf, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleArrayForZeroes<pxr::GfHalf, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleArrayForZeroes<pxr::GfHalf, 4>(value, tolerance, hasZero);
        }
        break;
    case BaseDataType::eInt:
        switch (value.type().componentCount)
        {
        case 2:
            return checkTupleArrayForZeroes<int32_t, 2>(value, tolerance, hasZero);
        case 3:
            return checkTupleArrayForZeroes<int32_t, 3>(value, tolerance, hasZero);
        case 4:
            return checkTupleArrayForZeroes<int32_t, 4>(value, tolerance, hasZero);
        }
        break;
    default:
        break;
    }

    return false;
}

} // namespace

class OgnAnyZero
{
public:
    static bool compute(OgnAnyZeroDatabase& db)
    {
        const auto& value = db.inputs.value();

        if (!value.resolved())
            return true;

        const auto& tolerance = db.inputs.tolerance();
        auto& result = db.outputs.result();

        try
        {
            //  Some of the functions below return as soon as they find a zero value, so
            //  we start out assuming there are no zeroes and let them change that to true.
            //
            result = false;
            bool foundType{ false };

            // Arrays
            if (value.type().arrayDepth > 0)
            {
                // Arrays of tuples.
                if (value.type().componentCount > 1)
                {
                    foundType = checkTupleArrayForZeroes(value, tolerance, result);
                }
                else
                {
                    // Arrays of scalars.
                    foundType = checkScalarArrayForZeroes(value, tolerance, result);
                }
            }
            // Tuples
            else if (value.type().componentCount > 1)
            {
                foundType = checkTupleForZeroes(value, tolerance, result);
            }
            else
            {
                // Scalars
                foundType = checkScalarForZero(value, tolerance, result);
            }
            if (!foundType)
            {
                throw ogn::compute::InputError(kValueTypeUnresolved);
            }
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("OgnAnyZero: %s", error.what());
            return false;
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
