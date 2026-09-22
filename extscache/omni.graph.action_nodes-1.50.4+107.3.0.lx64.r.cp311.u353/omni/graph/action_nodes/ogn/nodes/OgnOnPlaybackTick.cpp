// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnPlaybackTickDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnOnPlaybackTick
{
public:
    static bool compute(OgnOnPlaybackTickDatabase& db)
    {
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        if (!iContext->getIsPlaying(contextObj))
        {
            return true;
        }

        db.outputs.time() = iContext->getTime(contextObj);
        db.outputs.deltaSeconds() = iContext->getElapsedTime(contextObj);
        db.outputs.frame() = iContext->getFrame(contextObj);
        auto iActionGraph = getInterface();
        iActionGraph->setExecutionEnabled(outputs::tick.token(), db.getInstanceIndex());

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
