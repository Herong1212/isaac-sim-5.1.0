// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnFlipFlopDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnFlipFlop
{
public:
    // The flip-flop cycles output activation between 2 outputs
    static constexpr size_t kNumLevels = 2;

    // The output that will be activated on the next compute. 0 == A, 1 == B
    int m_nextLevel{ 0 };

    static bool compute(OgnFlipFlopDatabase& db)
    {
        auto iActionGraph = getInterface();
        OgnFlipFlop& state = db.perInstanceState<OgnFlipFlop>();

        if (state.m_nextLevel == 0)
        {
            iActionGraph->setExecutionEnabled(outputs::a.token(), db.getInstanceIndex());
            db.outputs.isA() = true;
        }
        else
        {
            iActionGraph->setExecutionEnabled(outputs::b.token(), db.getInstanceIndex());
            db.outputs.isA() = false;
        }
        state.m_nextLevel = (state.m_nextLevel + 1) % kNumLevels;

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
