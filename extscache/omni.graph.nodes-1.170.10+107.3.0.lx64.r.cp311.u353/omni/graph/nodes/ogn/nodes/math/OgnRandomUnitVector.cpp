// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "random/RandomNodeBase.h"

#include <OgnRandomUnitVectorDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{
using namespace random;

class OgnRandomUnitVector : public NodeBase<OgnRandomUnitVector, OgnRandomUnitVectorDatabase>
{
public:
    static void initialize(GraphContextObj const& contextObj, NodeObj const& nodeObj)
    {
        generateRandomSeed(contextObj, nodeObj, inputs::seed, inputs::useSeed);
    }

    static bool onCompute(OgnRandomUnitVectorDatabase& db, size_t count)
    {
        // TODO: Specify output type, we should be able to generate double precision output too...
        return computeRandoms(db, count, [](GeneratorState& gen) { return gen.nextUnitVec3f(); });
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
