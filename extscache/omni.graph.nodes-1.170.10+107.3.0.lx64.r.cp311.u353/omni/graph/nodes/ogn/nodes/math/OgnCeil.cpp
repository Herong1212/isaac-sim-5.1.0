// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnCeilDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <cmath>

namespace omni
{
namespace graph
{
namespace nodes
{

// unnamed namespace to avoid multiple declaration when linking
namespace
{
template <typename T>
bool tryComputeAssumingType(OgnCeilDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto& result) { result = static_cast<int>(std::ceil(a)); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, int>(db.inputs.a(), db.outputs.result(), functor, count);
}

template <typename T, size_t N>
bool tryComputeAssumingType(OgnCeilDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto& result) { result = static_cast<int>(std::ceil(a)); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, int>(db.inputs.a(), db.outputs.result(), functor, count);
}
} // namespace

class OgnCeil
{
public:
    static size_t computeVectorized(OgnCeilDatabase& db, size_t count)
    {
        try
        {
            auto& aType = db.inputs.a().type();
            switch (aType.baseType)
            {
            case BaseDataType::eDouble:
                switch (aType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count);
                }
                break;
            case BaseDataType::eFloat:
                switch (aType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count);
                }
                break;
            case BaseDataType::eHalf:
                switch (aType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
                }
                break;
            default:
                break;
            }
            throw ogn::compute::InputError("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("%s", error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto a = node.iNode->getAttributeByToken(node, inputs::a.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto valueType = a.iAttribute->getResolvedType(a);

        if (valueType.baseType != BaseDataType::eUnknown)
        {
            Type resultType(BaseDataType::eInt, valueType.componentCount, valueType.arrayDepth);
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
