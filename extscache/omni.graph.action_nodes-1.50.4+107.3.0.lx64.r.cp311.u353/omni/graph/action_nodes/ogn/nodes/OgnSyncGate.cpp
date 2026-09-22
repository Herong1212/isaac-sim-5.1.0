// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnSyncGateDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnSyncGate
{
public:
    // The current number of accumulated executions.
    uint32_t m_numAccumulatedExecIn{ 0 };
    // The current synchronization value.
    uint64_t m_syncValue{ 0 };

    static bool compute(OgnSyncGateDatabase& db)
    {
        auto nodeObj = db.abi_node();
        const AttributeObj attr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::execIn.m_token);
        const auto accumulationThreshold = static_cast<uint32_t>(attr.iAttribute->getUpstreamConnectionCount(attr));

        OgnSyncGate& state = db.perInstanceState<OgnSyncGate>();
        const bool reset = db.inputs.syncValue() != state.m_syncValue;
        state.m_numAccumulatedExecIn = reset ? 1 : std::min(state.m_numAccumulatedExecIn + 1, accumulationThreshold);
        db.outputs.syncValue() = state.m_syncValue = db.inputs.syncValue();
        if (state.m_numAccumulatedExecIn >= accumulationThreshold)
        {
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
