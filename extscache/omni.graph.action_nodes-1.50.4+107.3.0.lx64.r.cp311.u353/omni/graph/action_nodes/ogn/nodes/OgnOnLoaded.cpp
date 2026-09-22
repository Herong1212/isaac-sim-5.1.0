// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnLoadedDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnOnLoaded
{
    bool m_triggered{ false };

public:
    static bool compute(OgnOnLoadedDatabase& db)
    {
        auto& state = db.perInstanceState<OgnOnLoaded>();
        if (!state.m_triggered)
        {
            state.m_triggered = true;
            // This node does nothing but trigger downstream when first computed. When the execution evaluator receives
            // the first tick event it will ensure that OnLoaded nodes are run before any OnTick or other event node.
            // It's not possible to encapsulate the OnLoaded logic of the evaluator in this node due to the
            // special requirement that it run before others that are ready.
            auto iActionGraph = getInterface();
            iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());
        }
        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
