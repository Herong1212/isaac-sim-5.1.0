// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnEachZeroDatabase.h>
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
bool checkScalarForZero(OgnEachZeroAttributes::inputs::value_t& value, const double& tolerance, bool& isZero)
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


//  Determine which components of a decimal tuple attribute are within a given tolerance of zero.
//  (i.e. they lie within 'tolerance' of 0).
//
//  T - type of the components of the tuple.
//  N - number of components in the tuple
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each component of the tuple. On return the elements
//  will be set true where the corresponding components lie within 'tolerance' of zero, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
template <typename T, uint8_t N>
bool getTupleZeroes(const OgnEachZeroAttributes::inputs::value_t& value, const double& tolerance, ogn::array<bool>& isZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const tuple = value.get<T[N]>())
    {
        for (uint8_t i = 0; i < N; ++i)
        {
            isZero[i] = (std::abs(tuple[i]) <= tolerance);
        }

        return true;
    }

    return false;
}

//  Determine which components of a tuple attribute are zero
//  (i.e. they lie within 'tolerance' of 0).
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each component of the tuple. On return the elements
//  will be set true where the corresponding components are zero, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
bool getTupleZeroes(const OgnEachZeroAttributes::inputs::value_t& value, const double& tolerance, ogn::array<bool>& isZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    switch (value.type().baseType)
    {
    case BaseDataType::eDouble:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleZeroes<double, 2>(value, tolerance, isZero);
        case 3:
            return getTupleZeroes<double, 3>(value, tolerance, isZero);
        case 4:
            return getTupleZeroes<double, 4>(value, tolerance, isZero);
        case 9:
            return getTupleZeroes<double, 9>(value, tolerance, isZero);
        case 16:
            return getTupleZeroes<double, 16>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    case BaseDataType::eFloat:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleZeroes<float, 2>(value, tolerance, isZero);
        case 3:
            return getTupleZeroes<float, 3>(value, tolerance, isZero);
        case 4:
            return getTupleZeroes<float, 4>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    case BaseDataType::eHalf:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleZeroes<pxr::GfHalf, 2>(value, tolerance, isZero);
        case 3:
            return getTupleZeroes<pxr::GfHalf, 3>(value, tolerance, isZero);
        case 4:
            return getTupleZeroes<pxr::GfHalf, 4>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    case BaseDataType::eInt:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleZeroes<int32_t, 2>(value, tolerance, isZero);
        case 3:
            return getTupleZeroes<int32_t, 3>(value, tolerance, isZero);
        case 4:
            return getTupleZeroes<int32_t, 4>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    default:
        break;
    }

    return false;
}

//  Determine which elements of an unsigned array attribute are zero (i.e. they lie
//  within 'tolerance' of 0).
//
//  T - type of the elements of the array. Must be an unsigned type, other than bool.
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each element of the unsigned array. On return the elements
//  of 'isZero' will be set true where the corresponding elements in the unsigned array are zero, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
template <typename T>
bool getUnsignedArrayZeroes(const OgnEachZeroAttributes::inputs::value_t& value,
                            const double& tolerance,
                            ogn::array<bool>& isZero)
{
    static_assert(std::is_unsigned<T>::value && !std::is_same<T, bool>::value, "Unsigned integer type required.");
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const array = value.get<T[]>())
    {
        for (size_t i = 0; i < array.size(); ++i)
            isZero[i] = (array->at(i) <= (T)tolerance);

        return true;
    }

    return false;
}

//  Determine which elements of a bool array attribute are zero/false. No tolerance
//  value is applied since tolerance is meaningless for bool.
//
//  'isZero' is an array of bool with one element for each element of the 'value' array. On return the elements
//  of 'isZero' will be set true where the corresponding elements in the 'value' array are zero, false otherwise.
//
//  The return value is true if 'value' is a bool array type, false otherwise.
//
bool getBoolArrayZeroes(const OgnEachZeroAttributes::inputs::value_t& value, ogn::array<bool>& isZero)
{
    if (auto const array = value.get<bool[]>())
    {
        for (size_t i = 0; i < array.size(); ++i)
            isZero[i] = !array->at(i);

        return true;
    }

    return false;
}

//  Determine which elements of a signed array attribute are within a given tolerance of zero.
//  (i.e. they lie within 'tolerance' of 0).
//
//  T - type of the elements of the array. Must be a signed type.
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each element of the signed array. On return the elements
//  of 'isZero' will be set true where the corresponding elements in the unsigned array are within 'tolerance'
//  of 0.0, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
template <typename T>
bool getSignedArrayZeroes(const OgnEachZeroAttributes::inputs::value_t& value,
                          const double& tolerance,
                          ogn::array<bool>& isZero)
{
    static_assert(
        std::is_signed<T>::value || pxr::GfIsFloatingPoint<T>::value, "Signed integer or decimal type required.");
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const array = value.get<T[]>())
    {
        for (size_t i = 0; i < array.size(); ++i)
            isZero[i] = (std::abs(array->at(i)) <= tolerance);

        return true;
    }

    return false;
}

//  Determine which elements of a scalar array attribute are zero (i.e. they lie within 'tolerance' of 0).
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each element of the scalar array. On return the elements
//  of 'isZero' will be set true where the corresponding elements in the scalar array are zero, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
bool getScalarArrayZeroes(const OgnEachZeroAttributes::inputs::value_t& value,
                          const double& tolerance,
                          ogn::array<bool>& isZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    switch (value.type().baseType)
    {
    case BaseDataType::eBool:
        return getBoolArrayZeroes(value, isZero);
    case BaseDataType::eDouble:
        return getSignedArrayZeroes<double>(value, tolerance, isZero);
    case BaseDataType::eFloat:
        return getSignedArrayZeroes<float>(value, tolerance, isZero);
    case BaseDataType::eHalf:
        return getSignedArrayZeroes<pxr::GfHalf>(value, tolerance, isZero);
    case BaseDataType::eInt:
        return getSignedArrayZeroes<int32_t>(value, tolerance, isZero);
    case BaseDataType::eInt64:
        return getSignedArrayZeroes<int64_t>(value, tolerance, isZero);
    case BaseDataType::eUChar:
        return getUnsignedArrayZeroes<unsigned char>(value, tolerance, isZero);
    case BaseDataType::eUInt:
        return getUnsignedArrayZeroes<uint32_t>(value, tolerance, isZero);
    case BaseDataType::eUInt64:
        return getUnsignedArrayZeroes<uint64_t>(value, tolerance, isZero);
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
template <typename T, uint8_t N>
bool isTupleZero(const T tuple[N], double tolerance)
{
    CARB_ASSERT(tolerance >= 0.0);

    for (uint8_t i = 0; i < N; ++i)
    {
        if (std::abs(tuple[i]) > tolerance)
            return false;
    }

    return true;
}

//  Determine which elements of a tuple array attribute are zero (i.e. all of the tuple's
//  components lie within a 'tolerance' of 0).
//
//  T - type of the components of the tuple.
//  N - number of components in the tuple
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each tuple in the tuple array. On return the elements
//  of 'isZero' will be set true where the corresponding tuples are zero, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
template <typename T, uint8_t N>
bool getTupleArrayZeroes(const OgnEachZeroAttributes::inputs::value_t& value, double tolerance, ogn::array<bool>& isZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    if (auto const array = value.get<T[][N]>())
    {
        for (size_t i = 0; i < array.size(); ++i)
            isZero[i] = isTupleZero<T, N>(array->at(i), tolerance);

        return true;
    }

    return false;
}

//  Determine which elements of a tuple array attribute are zero (i.e. all of the tuple's components
//  lie within 'tolerance' of 0).
//
//  'tolerance' must be non-negative
//  'isZero' is an array of bool with one element for each tuple in the tuple array. On return the elements
//  of 'isZero' will be set true where the corresponding tuples are zero, false otherwise.
//
//  The return value is true if 'value' is a supported tuple type, false otherwise.
//
bool getTupleArrayZeroes(const OgnEachZeroAttributes::inputs::value_t& value,
                         const double& tolerance,
                         ogn::array<bool>& isZero)
{
    CARB_ASSERT(tolerance >= 0.0);

    switch (value.type().baseType)
    {
    case BaseDataType::eDouble:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleArrayZeroes<double, 2>(value, tolerance, isZero);
        case 3:
            return getTupleArrayZeroes<double, 3>(value, tolerance, isZero);
        case 4:
            return getTupleArrayZeroes<double, 4>(value, tolerance, isZero);
        case 9:
            return getTupleArrayZeroes<double, 9>(value, tolerance, isZero);
        case 16:
            return getTupleArrayZeroes<double, 16>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    case BaseDataType::eFloat:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleArrayZeroes<float, 2>(value, tolerance, isZero);
        case 3:
            return getTupleArrayZeroes<float, 3>(value, tolerance, isZero);
        case 4:
            return getTupleArrayZeroes<float, 4>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    case BaseDataType::eHalf:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleArrayZeroes<pxr::GfHalf, 2>(value, tolerance, isZero);
        case 3:
            return getTupleArrayZeroes<pxr::GfHalf, 3>(value, tolerance, isZero);
        case 4:
            return getTupleArrayZeroes<pxr::GfHalf, 4>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    case BaseDataType::eInt:
        switch (value.type().componentCount)
        {
        case 2:
            return getTupleArrayZeroes<int32_t, 2>(value, tolerance, isZero);
        case 3:
            return getTupleArrayZeroes<int32_t, 3>(value, tolerance, isZero);
        case 4:
            return getTupleArrayZeroes<int32_t, 4>(value, tolerance, isZero);
        default:
            break;
        }
        break;
    default:
        break;
    }

    return false;
}

} // namespace

class OgnEachZero
{
public:
    static bool compute(OgnEachZeroDatabase& db)
    {
        const auto& value = db.inputs.value();

        if (!value.resolved())
            return true;

        const auto& tolerance = db.inputs.tolerance();
        auto& result = db.outputs.result();

        try
        {
            bool foundType{ false };
            // Arrays
            if (value.type().arrayDepth > 0)
            {
                if (auto resultArray = result.get<bool[]>())
                {
                    resultArray.resize(value.size());

                    // Arrays of tuples.
                    if (value.type().componentCount > 1)
                    {
                        foundType = getTupleArrayZeroes(value, tolerance, *resultArray);
                    }
                    // Arrays of scalars.
                    else
                    {
                        foundType = getScalarArrayZeroes(value, tolerance, *resultArray);
                    }
                }
                else
                {
                    throw ogn::compute::InputError("input value is an array but result is not bool[]");
                }
            }
            // Tuples
            else if (value.type().componentCount > 1)
            {
                if (auto resultArray = result.get<bool[]>())
                {
                    resultArray.resize(value.type().componentCount);

                    foundType = getTupleZeroes(value, tolerance, *resultArray);
                }
                else
                {
                    throw ogn::compute::InputError("input value is a tuple but result is not bool[]");
                }
            }
            // Scalars
            else
            {
                if (auto resultScalar = result.get<bool>())
                {
                    *resultScalar = false;

                    foundType = checkScalarForZero(value, tolerance, *resultScalar);
                }
                else
                {
                    throw ogn::compute::InputError("input value is a scalar but result is not bool");
                }
            }
            if (!foundType)
            {
                throw ogn::compute::InputError(kValueTypeUnresolved);
            }
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("%s", error.what());
            return false;
        }
        return true;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto value = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto valueType = value.iAttribute->getResolvedType(value);

        // Require value to be resolved before determining result's type
        if (valueType.baseType != BaseDataType::eUnknown)
        {
            // The result is bool for scalar values, and bool array for arrays and tuples.
            bool resultIsArray = ((valueType.arrayDepth > 0) || (valueType.componentCount > 1));
            Type resultType(BaseDataType::eBool, 1, (resultIsArray ? 1 : 0));

            result.iAttribute->setResolvedType(result, resultType);
        }
        else
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
