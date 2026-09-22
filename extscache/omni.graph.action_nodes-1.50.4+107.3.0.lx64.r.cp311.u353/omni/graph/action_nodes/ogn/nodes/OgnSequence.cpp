// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnSequenceDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnSequence
{
public:
    // Which branch we should take next
    int m_nextOutput{ 0 };

    static bool compute(OgnSequenceDatabase& db)
    {
        auto iActionGraph = getInterface();
        OgnSequence& state = db.perInstanceState<OgnSequence>();

        if (state.m_nextOutput == 0)
        {
            iActionGraph->setExecutionEnabledAndPushed(outputs::a.token(), db.getInstanceIndex());
        }
        else
        {
            iActionGraph->setExecutionEnabled(outputs::b.token(), db.getInstanceIndex());
        }

        state.m_nextOutput = (state.m_nextOutput + 1) % 2;

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
