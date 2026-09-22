// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnBranchDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnBranch
{
public:
    static bool compute(OgnBranchDatabase& db)
    {
        auto iActionGraph = getInterface();
        bool condition = db.inputs.condition();

        if (condition)
            iActionGraph->setExecutionEnabled(outputs::execTrue.token(), db.getInstanceIndex());
        else
            iActionGraph->setExecutionEnabled(outputs::execFalse.token(), db.getInstanceIndex());

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
