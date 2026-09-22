// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnAndDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "OperatorComputeWrapper.h"
#include "ResolveBooleanOpAttributes.h"

namespace omni
{
namespace graph
{
namespace nodes
{

// unnamed namespace to avoid multiple declaration when linking
namespace
{

/**
 * Boolean AND on two inputs.
 * If a and b are arrays, AND operations will be performed pair-wise. Sizes of a and b must match.
 * If only one input is an array, the other input will be broadcast to the size of the array.
 * Returns an array of booleans if either input is an array, otherwise returning a boolean.
 *
 * @param db: database object
 * @return True if we can get a result properly, false if not
 */

size_t tryCompute(OgnAndDatabase& db, size_t count)
{
    auto const& dynamicInputs = db.getDynamicInputs();
    if (dynamicInputs.empty())
    {
        auto functor = [](bool const& a, bool const& b, bool& result) { result = static_cast<bool>(a && b); };
        return ogn::compute::tryComputeWithArrayBroadcasting<bool, bool, bool>(
                   db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
                   count :
                   0;
    }
    else
    {
        std::vector<ogn::InputAttribute> inputs{ db.inputs.a(), db.inputs.b() };
        inputs.reserve(dynamicInputs.size() + 2);
        for (auto const& input : dynamicInputs)
            inputs.emplace_back(input());

        auto functor = [](bool const& a, bool& result) { result = static_cast<bool>(result && a); };
        return ogn::compute::tryComputeInputsWithArrayBroadcasting<bool>(inputs, db.outputs.result(), functor, count) ?
                   count :
                   0;
    }
}
} // namespace

class OgnAnd
{
public:
    static size_t computeVectorized(OgnAndDatabase& db, size_t count)
    {
        return tryComputeOperator<OgnAndDatabase>(tryCompute, db, count);
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        resolveBooleanOpDynamicAttributes(node, outputs::result.token());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
