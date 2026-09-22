// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnRationalTimeSyncGateDatabase.h>

#include <omni/fabric/RationalTime.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnRationalTimeSyncGate
{
public:
    // The current number of accumulated executions.
    uint32_t m_numAccumulatedExecIn{ 0 };
    // The current synchronization value.
    fabric::RationalTime m_syncValue = fabric::kInvalidRationalTime;

    static bool compute(OgnRationalTimeSyncGateDatabase& db)
    {
        auto nodeObj = db.abi_node();
        const AttributeObj attr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::execIn.m_token);
        const auto accumulationThreshold = static_cast<uint32_t>(attr.iAttribute->getUpstreamConnectionCount(attr));

        OgnRationalTimeSyncGate& state = db.perInstanceState<OgnRationalTimeSyncGate>();
        const fabric::RationalTime syncValue{ db.inputs.rationalTimeNumerator(), db.inputs.rationalTimeDenominator() };
        const bool reset = syncValue != state.m_syncValue;
        state.m_numAccumulatedExecIn = reset ? 1 : std::min(state.m_numAccumulatedExecIn + 1, accumulationThreshold);
        state.m_syncValue = syncValue;
        db.outputs.rationalTimeNumerator() = syncValue.numerator;
        db.outputs.rationalTimeDenominator() = syncValue.denominator;
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
