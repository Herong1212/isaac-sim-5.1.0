// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/usd/common.h>
#include <pxr/usd/sdf/valueTypeName.h>
#include <omni/graph/core/PostUsdInclude.h>

#include <omni/fabric/FabricUSD.h>

#include <OgnAppendPathDatabase.h>
// clang-format on

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
static NameToken appendPath(const NameToken& pathAsToken, const pxr::SdfPath& suffix)
{
    auto pathToken = toTfToken(pathAsToken);
    if (pathAsToken != omni::fabric::kUninitializedToken && pxr::SdfPath::IsValidPathString(pathToken))
    {
        auto newPath = pxr::SdfPath(pathToken).AppendPath(suffix);
        return asInt(newPath.GetToken());
    }
    return pathAsToken;
}
} // namespace

class OgnAppendPath
{
public:
    static size_t computeVectorized(OgnAppendPathDatabase& db, size_t count)
    {
        auto suffix = db.inputs.suffix.vectorized(count);
        if (db.inputs.path().type().arrayDepth > 0)
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                if (suffix[idx] == omni::fabric::kUninitializedToken)
                {
                    db.outputs.path(idx).copyData(db.inputs.path(idx));
                }
                else
                {
                    const auto suffixPath = pxr::SdfPath(toTfToken(suffix[idx]));
                    const auto inputPathArray = *db.inputs.path(idx).get<OgnToken[]>();
                    auto outputPathArray = *db.outputs.path(idx).get<OgnToken[]>();
                    outputPathArray.resize(inputPathArray.size());
                    std::transform(inputPathArray.begin(), inputPathArray.end(), outputPathArray.begin(),
                                   [&](const auto& p) { return appendPath(p, suffixPath); });
                }
            }
        }
        else
        {
            auto ipt = db.inputs.path().get<OgnToken>();
            auto inputPath = ipt.vectorized(count);

            auto oldInputs = db.state.path.vectorized(count);
            auto oldSuffix = db.state.suffix.vectorized(count);

            auto op = db.outputs.path().get<OgnToken>();
            auto outputs = op.vectorized(count);

            for (size_t idx = 0; idx < count; ++idx)
            {
                if (oldSuffix[idx] != suffix[idx] || oldInputs[idx] != inputPath[idx])
                {
                    if (suffix[idx] == omni::fabric::kUninitializedToken)
                    {
                        outputs[idx] = inputPath[idx];
                    }
                    else
                    {
                        const auto suffixPath = pxr::SdfPath(toTfToken(suffix[idx]));
                        outputs[idx] = appendPath(inputPath[idx], suffixPath);
                    }
                    oldSuffix[idx] = suffix[idx];
                    oldInputs[idx] = inputPath[idx];
                }
            }
        }
        return count;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        // Resolve fully-coupled types for the 2 attributes
        std::array<AttributeObj, 2> attrs{ node.iNode->getAttribute(node, OgnAppendPathAttributes::inputs::path.m_name),
                                           node.iNode->getAttribute(node, OgnAppendPathAttributes::outputs::path.m_name) };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
