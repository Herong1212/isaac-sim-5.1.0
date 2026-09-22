// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGateDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

enum GateState
{
    kGateStateClosed = 0,
    kGateStateOpen = 1,
    kGateStateUninitialized = 2,
};

class OgnGate
{
public:
    int m_gate{ kGateStateUninitialized };

    static bool compute(OgnGateDatabase& db)
    {
        auto iActionGraph = getInterface();
        auto& state = db.perInstanceState<OgnGate>();

        // On our first ever compute call, initialize the gate state.
        if (state.m_gate == kGateStateUninitialized)
        {
            state.m_gate = db.inputs.startClosed() ? kGateStateClosed : kGateStateOpen;
        }

        // In compute one of toggle or enter will be enabled
        bool isToggle = iActionGraph->getExecutionEnabled(inputs::toggle.token(), db.getInstanceIndex());
        if (isToggle)
        {
            // toggle the state
            state.m_gate = (state.m_gate + 1) % 2;
        }
        else
        {
            if (state.m_gate == kGateStateOpen)
                iActionGraph->setExecutionEnabled(outputs::exit.token(), db.getInstanceIndex());
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
