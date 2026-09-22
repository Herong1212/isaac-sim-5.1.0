// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnceDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnOnce
{
    bool m_open{ false };

public:
    static bool compute(OgnOnceDatabase& db)
    {
        auto iActionGraph = getInterface();
        auto& state = db.perInstanceState<OgnOnce>();

        bool isReset = iActionGraph->getExecutionEnabled(inputs::reset.token(), db.getInstanceIndex());
        if (isReset)
        {
            state.m_open = false;
            return true;
        }

        if (!state.m_open)
        {
            state.m_open = true;
            iActionGraph->setExecutionEnabled(outputs::once.token(), db.getInstanceIndex());
        }
        else
        {
            iActionGraph->setExecutionEnabled(outputs::after.token(), db.getInstanceIndex());
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
