// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnAppendTargetsDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ArrayWrapper.h>
#include <carb/logging/Log.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnAppendTargets
{
public:
    static bool computeVectorized(OgnAppendTargetsDatabase& db, size_t count)
    {
        try
        {
            NodeObj nodeObj = db.abi_node();
            auto iNode = nodeObj.iNode;
            GraphObj graphObj = iNode->getGraph(nodeObj);
            GraphContextObj context = graphObj.iGraph->getDefaultGraphContext(graphObj);

            std::vector<TargetPath> targetPaths;
            for (size_t idx = 0; idx < count; ++idx)
            {
                targetPaths.clear();
                size_t i = 0;
                while (iNode->getAttributeExists(nodeObj, formatString("inputs:input%zu", i).c_str()))
                {
                    auto attr = iNode->getAttribute(nodeObj, formatString("inputs:input%zu", i).c_str());
                    ArrayWrapper<TargetPath> pathArray{ context, attr, db.getInstanceIndex() + idx };
                    const auto* pathArrayData = pathArray.getArrayRd();
                    for (size_t i = 0; i < pathArray.size(); i++)
                    {
                        // We only add if not found or if explicitly told to do so
                        if ((std::find(targetPaths.begin(), targetPaths.end(), pathArrayData[i]) == targetPaths.end()) ||
                            db.inputs.allowDuplicates())
                        {
                            targetPaths.push_back(pathArrayData[i]);
                        }
                    }
                    i++;
                }

                auto& output = db.outputs.targets(idx);
                if (!targetPaths.empty())
                {
                    output.resize(targetPaths.size());
                    memcpy(output.data(), targetPaths.data(), sizeof(ogn::Path) * targetPaths.size());
                }
                else
                    output.resize(0);
            }
            return count;
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

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
