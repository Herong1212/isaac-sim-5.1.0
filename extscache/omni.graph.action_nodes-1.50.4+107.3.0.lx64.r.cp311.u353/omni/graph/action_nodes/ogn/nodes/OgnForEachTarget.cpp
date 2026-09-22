// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnForEachTargetDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnForEachTarget
{
public:
    size_t m_arrayIndex{ 0 };

    static bool compute(OgnForEachTargetDatabase& db)
    {
        auto iActionGraph = getInterface();
        auto const& targets = db.inputs.targets();
        size_t const numTargets = targets.size();

        auto& state = db.perInstanceState<OgnForEachTarget>();

        if (iActionGraph->getExecutionEnabled(inputs::execIn.token(), db.getInstanceIndex()))
            state.m_arrayIndex = 0;

        if (state.m_arrayIndex >= numTargets)
        {
            iActionGraph->setExecutionEnabled(outputs::finished.token(), db.getInstanceIndex());
            state.m_arrayIndex = 0;
            return true;
        }

        size_t currentIndex = state.m_arrayIndex++;

        iActionGraph->setExecutionEnabledAndPushed(outputs::loopBody.token(), db.getInstanceIndex());
        db.outputs.arrayIndex() = static_cast<int>(currentIndex);

        auto& target = db.outputs.target();
        if (!targets.empty())
        {
            target.resize(1);
            target[0] = targets[currentIndex];
        }
        else
            target.resize(0);

        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
