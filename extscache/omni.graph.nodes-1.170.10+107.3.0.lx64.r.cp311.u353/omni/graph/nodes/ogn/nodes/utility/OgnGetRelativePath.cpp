// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetRelativePathDatabase.h>
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
static NameToken getRelativePath(const NameToken& pathAsToken, const pxr::SdfPath& anchor)
{
    auto pathToken = toTfToken(pathAsToken);
    if (pathAsToken != omni::fabric::kUninitializedToken && pxr::SdfPath::IsValidPathString(pathToken))
    {
        auto relPath = pxr::SdfPath(pathToken).MakeRelativePath(anchor);
        return asInt(relPath.GetToken());
    }
    return pathAsToken;
}
} // namespace

class OgnGetRelativePath
{
public:
    static size_t computeVectorized(OgnGetRelativePathDatabase& db, size_t count)
    {
        auto anchor = db.inputs.anchor.vectorized(count);
        if (db.inputs.path().type().arrayDepth > 0)
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                if (anchor[idx] == omni::fabric::kUninitializedToken)
                {
                    db.outputs.relativePath(idx).copyData(db.inputs.path(idx));
                }
                else
                {
                    const auto anchorPath = pxr::SdfPath(toTfToken(anchor[idx]));
                    const auto inputPathArray = *db.inputs.path(idx).get<OgnToken[]>();
                    auto outputPathArray = *db.outputs.relativePath(idx).get<OgnToken[]>();
                    outputPathArray.resize(inputPathArray.size());
                    std::transform(inputPathArray.begin(), inputPathArray.end(), outputPathArray.begin(),
                                   [&](const auto& p) { return getRelativePath(p, anchorPath); });
                }
            }
        }
        else
        {
            auto ipt = db.inputs.path().get<OgnToken>();
            auto inputPath = ipt.vectorized(count);

            auto oldInputs = db.state.path.vectorized(count);
            auto oldAnchor = db.state.anchor.vectorized(count);

            auto op = db.outputs.relativePath().get<OgnToken>();
            auto outputs = op.vectorized(count);

            for (size_t idx = 0; idx < count; ++idx)
            {
                if (oldAnchor[idx] != anchor[idx] || oldInputs[idx] != inputPath[idx])
                {
                    if (anchor[idx] == omni::fabric::kUninitializedToken)
                    {
                        outputs[idx] = inputPath[idx];
                    }
                    else
                    {
                        const auto anchorPath = pxr::SdfPath(toTfToken(anchor[idx]));
                        outputs[idx] = getRelativePath(inputPath[idx], anchorPath);
                    }
                    oldAnchor[idx] = anchor[idx];
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
            node.iNode->getAttribute(node, OgnGetRelativePathAttributes::inputs::path.m_name),
            node.iNode->getAttribute(node, OgnGetRelativePathAttributes::outputs::relativePath.m_name)
        };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
