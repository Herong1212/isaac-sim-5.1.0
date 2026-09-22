// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnXorDatabase.h>
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
 * Boolean XOR on two inputs.
 * If a and b are arrays, XOR operations will be performed pair-wise. Sizes of a and b must match.
 * If only one input is an array, the other input will be broadcast to the size of the array.
 * Returns an array of booleans if either input is an array, otherwise returning a boolean.
 *
 * @param db: database object
 * @return True if we can get a result properly, false if not
 */

size_t tryCompute(OgnXorDatabase& db, size_t count)
{
    auto functor = [](bool const& a, bool const& b, bool& result) { result = static_cast<bool>(a != b); };
    return ogn::compute::tryComputeWithArrayBroadcasting<bool, bool, bool>(
               db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnXor
{
public:
    static size_t computeVectorized(OgnXorDatabase& db, size_t count)
    {
        return tryComputeOperator<OgnXorDatabase>(tryCompute, db, count);
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        resolveBooleanOpAttributes(node, inputs::a.token(), inputs::b.token(), outputs::result.token());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
