// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnClosingDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnOnClosing
{
public:
    static bool compute(OgnOnClosingDatabase& db)
    {
        auto iActionGraph = getInterface();
        // This node does nothing but trigger downstream when computed. When the execution evaluator receives the
        // pre-detach event it will ensure that only OnClosing nodes will be evaluated before cleaning up the graph.
        // It's not possible to encapsulate the closing logic of the evaluator in this node due to the
        // special requirement that other event nodes be disabled, which only applies to this one case.
        // (We don't want OnTick running during the closing).
        iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());
        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
