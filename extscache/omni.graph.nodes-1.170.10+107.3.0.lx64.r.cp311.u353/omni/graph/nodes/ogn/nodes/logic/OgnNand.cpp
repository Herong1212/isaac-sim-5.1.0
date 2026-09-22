// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnNandDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include "ResolveBooleanOpAttributes.h"
#include "OperatorComputeWrapper.h"

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
 * Boolean NAND on two inputs.
 * If a and b are arrays, NAND operations will be performed pair-wise. Sizes of a and b must match.
 * If only one input is an array, the other input will be broadcast to the size of the array.
 * Returns an array of booleans if either input is an array, otherwise returning a boolean.
 *
 * @param db: database object
 * @return True if we can get a result properly, false if not
 */

size_t tryCompute(OgnNandDatabase& db, size_t count)
{
    auto const& dynamicInputs = db.getDynamicInputs();
    if (dynamicInputs.empty())
    {
        // if there are no dynamic inputs, compute the result in one call
        auto functor = [](bool const& a, bool const& b, bool& result) { result = static_cast<bool>(!(a && b)); };
        return ogn::compute::tryComputeWithArrayBroadcasting<bool, bool, bool>(
                   db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
                   count :
                   0;
    }

    // The NAND operator is not associative.
    // If we have dynamic inputs, we must compute the result in two steps

    std::vector<ogn::InputAttribute> inputs{ db.inputs.a(), db.inputs.b() };
    inputs.reserve(dynamicInputs.size() + 2);
    for (auto const& input : dynamicInputs)
        inputs.emplace_back(input());

    // 1. apply the OR operator for all inputs
    auto andFunctor = [](bool const& a, bool& result) { result = static_cast<bool>(a && result); };
    bool result =
        ogn::compute::tryComputeInputsWithArrayBroadcasting<bool>(inputs, db.outputs.result(), andFunctor, count);

    // the output attribute has to be cast to an input so that we can write the final value on it
    auto resultInput = omni::graph::core::ogn::constructInputFromOutput(db, db.outputs.result(), outputs::result.token());

    // 2. negate the result
    auto negateFunctor = [](bool const& a, bool& result) { result = static_cast<bool>(!a); };
    result = result && ogn::compute::tryComputeWithArrayBroadcasting<bool, bool>(
                           resultInput, db.outputs.result(), negateFunctor, count);
    return result ? count : 0;
}
} // namespace

class OgnNand
{
public:
    static size_t computeVectorized(OgnNandDatabase& db, size_t count)
    {
        return tryComputeOperator<OgnNandDatabase>(tryCompute, db, count);
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
