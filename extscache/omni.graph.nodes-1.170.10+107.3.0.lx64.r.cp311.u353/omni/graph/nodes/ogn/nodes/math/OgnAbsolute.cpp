// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <carb/logging/Log.h>

#include <omni/graph/core/ogn/ComputeHelpers.h>

#include <OgnAbsoluteDatabase.h>
#include <NumericUtils.h>
#include <cmath>
#include <type_traits>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

template <typename T>
T ogAbs(T const& input) noexcept
{
    if constexpr (std::is_unsigned_v<T>)
    {
        return input;
    }
    else
    {
        return std::abs(input);
    }
}

template <typename T, size_t N>
struct ComputeAbsoluteValueAssumingType
{
    bool operator()(OgnAbsoluteDatabase& db, size_t count) const
    {
        if constexpr (N == 1)
        {
            auto functor = [](T const& input, T& absolute) { absolute = ogAbs(input); };
            return ogn::compute::tryComputeWithArrayBroadcasting<T, T>(
                       db.inputs.input(), db.outputs.absolute(), functor, count) ?
                       count :
                       0;
        }
        else
        {
            auto functor = [](auto const& input, auto& absolute)
            {
                for (size_t i = 0; i < N; ++i)
                {
                    absolute[i] = ogAbs(input[i]);
                }
            };
            return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N]>(
                       db.inputs.input(), db.outputs.absolute(), functor, count) ?
                       count :
                       0;
        }
    }
};

}

class OgnAbsolute
{
public:
    static size_t computeVectorized(OgnAbsoluteDatabase& db, size_t count)
    {
        try
        {
            auto const& type = db.inputs.input().type();
            if (!callForNumericAttribute<ComputeAbsoluteValueAssumingType>(db, type, count))
            {
                throw ogn::compute::InputError("Failed to resolve input type");
            }
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("OgnAbsolute: %s", error.what());
        }
        return 0;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto input = node.iNode->getAttributeByToken(node, inputs::input.token());
        auto absolute = node.iNode->getAttributeByToken(node, outputs::absolute.token());

        auto inputType = input.iAttribute->getResolvedType(input);

        // Require inputs to be resolved before determining output's type
        if (inputType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ input, absolute };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

}
}
}
