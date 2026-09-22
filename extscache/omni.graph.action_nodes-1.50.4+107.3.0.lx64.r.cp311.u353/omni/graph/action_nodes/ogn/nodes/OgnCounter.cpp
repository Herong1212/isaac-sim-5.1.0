// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnCounterDatabase.h"
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnCounter
{
public:
    static bool compute(OgnCounterDatabase& db)
    {
        auto iActionGraph = getInterface();
        bool isReset =
            iActionGraph->getExecutionEnabled(inputs::reset.token(), omni::graph::core::kAccordingToContextIndex);

        if (isReset)
        {
            db.state.count() = 0;
        }
        else
        {
            db.state.count() = db.state.count() + 1;
        }

        db.outputs.count() = db.state.count();
        iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
