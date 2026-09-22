// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnForLoopDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnForLoop
{
public:
    static bool compute(OgnForLoopDatabase& db)
    {
        auto iActionGraph = getInterface();
        bool const isBreakLoop = iActionGraph->getExecutionEnabled(inputs::breakLoop.token(), db.getInstanceIndex());
        bool const isExecIn = iActionGraph->getExecutionEnabled(inputs::execIn.token(), db.getInstanceIndex());

        auto finishLoop = [&db, &iActionGraph]()
        {
            db.state.i() = -1;
            iActionGraph->setExecutionEnabled(outputs::finished.token(), db.getInstanceIndex());
        };

        if (isBreakLoop)
        {
            finishLoop();
            return true;
        }

        if (isExecIn)
            db.state.i() = -1;

        int i = db.state.i();

        // no existing loop state, initialize it to zero
        if (i == -1)
            i = 0;

        int step = db.inputs.step();

        if (step == 0)
        {
            db.logError("Step can not be zero");
            return false;
        }


        int start = db.inputs.start();
        int stop = db.inputs.stop();

        int rangeVal = start + step * i;

        if (step > 0)
        {
            if (rangeVal >= stop)
            {
                finishLoop();
                return true;
            }
        }
        else
        {
            if (rangeVal <= stop)
            {
                finishLoop();
                return true;
            }
        }

        // execute the loop body
        db.outputs.value() = rangeVal;
        db.outputs.index() = i;
        db.state.i() = i + 1;
        iActionGraph->setExecutionEnabledAndPushed(outputs::loopBody.token(), db.getInstanceIndex());

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
