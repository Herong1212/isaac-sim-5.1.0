// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetParentPathDatabase.h>
#include <omni/fabric/FabricUSD.h>

using omni::fabric::asInt;
using omni::fabric::toTfToken;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
static NameToken getParentPath(const NameToken& pathAsToken)
{
    auto pathToken = toTfToken(pathAsToken);
    if (pathAsToken != omni::fabric::kUninitializedToken && pxr::SdfPath::IsValidPathString(pathToken))
    {
        auto parentPath = pxr::SdfPath(pathToken).GetParentPath();
        return asInt(parentPath.GetToken());
    }
    return pathAsToken;
}
} // namespace

class OgnGetParentPath
{
public:
    static bool computeVectorized(OgnGetParentPathDatabase& db, size_t count)
    {
        if (db.inputs.path().type().arrayDepth > 0)
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto inputPathArray = *db.inputs.path(idx).get<OgnToken[]>();
                auto outputPathArray = *db.outputs.parentPath(idx).get<OgnToken[]>();
                outputPathArray.resize(inputPathArray.size());
                std::transform(inputPathArray.begin(), inputPathArray.end(), outputPathArray.begin(),
                               [&](const auto& p) { return getParentPath(p); });
            }
        }
        else
        {
            auto ipt = db.inputs.path().get<OgnToken>();
            auto inputPath = ipt.vectorized(count);

            auto oldInputs = db.state.path.vectorized(count);

            auto op = db.outputs.parentPath().get<OgnToken>();
            auto outputs = op.vectorized(count);

            for (size_t idx = 0; idx < count; ++idx)
            {
                if (oldInputs[idx] != inputPath[idx])
                {
                    outputs[idx] = getParentPath(inputPath[idx]);
                    oldInputs[idx] = inputPath[idx];
                }
            }
        }
        return count;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        // Resolve fully-coupled types for the 2 attributes
        std::array<AttributeObj, 2> attrs{
            node.iNode->getAttribute(node, OgnGetParentPathAttributes::inputs::path.m_name),
            node.iNode->getAttribute(node, OgnGetParentPathAttributes::outputs::parentPath.m_name)
        };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
