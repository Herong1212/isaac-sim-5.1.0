// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnToStringDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/UsdTypes.h>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include "PrimCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{
namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnToStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        std::string converted = tryConvertToString<T>(db, db.inputs.value(idx));

        if (!converted.empty())
            db.outputs.converted(idx) = converted.c_str();
    }
    return count;
}

// Token may return empty, so we don't check for the fault condition from tryConvertToString
template <>
size_t tryComputeAssumingType<ogn::Token>(OgnToStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        std::string converted = tryConvertToString<ogn::Token>(db, db.inputs.value(idx));
        db.outputs.converted(idx) = converted.c_str();
    }
    return count;
}

template <>
size_t tryComputeAssumingType<string>(OgnToStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto val = db.inputs.value(idx).template get<const uchar[]>();

        if (val)
        {
            auto charData = val->data();
            std::string converted(charData, charData + val->size());
            db.outputs.converted(idx) = converted.c_str();
        }
    }
    return count;
}

template <typename T, size_t tupleSize>
size_t tryComputeAssumingType(OgnToStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        std::string converted = tryConvertToString<T, tupleSize>(db, db.inputs.value(idx));

        if (!converted.empty())
            db.outputs.converted(idx) = converted.c_str();
    }
    return count;
}

} // namespace

class OgnToString
{
public:
    // Node to convert any input to a string
    static size_t computeVectorized(OgnToStringDatabase& db, size_t count)
    {
        const auto& inputType = db.inputs.value().type();
        try
        {
            switch (inputType.baseType)
            {
            case BaseDataType::eToken:
                return tryComputeAssumingType<ogn::Token>(db, count);
            case BaseDataType::eBool:
                return tryComputeAssumingType<bool>(db, count);
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count);
                case 9:
                    return tryComputeAssumingType<double, 9>(db, count);
                case 16:
                    return tryComputeAssumingType<double, 16>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int32_t>(db, count);
                case 2:
                    return tryComputeAssumingType<int32_t, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<int32_t, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<int32_t, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
                // This handles char and string case (get<ogn::string>() will return invalid result)
                if ((inputType.arrayDepth == 1) &&
                    ((inputType.role == AttributeRole::eText) || (inputType.role == AttributeRole::ePath)))
                {
                    return tryComputeAssumingType<string>(db, count);
                }
                return tryComputeAssumingType<uchar>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
            // LCOV_EXCL_START
            default:
                throw ogn::compute::InputError("Failed to resolve input types");
                // LCOV_EXCL_STOP
            }
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }
};

REGISTER_OGN_NODE();

}
}
}
