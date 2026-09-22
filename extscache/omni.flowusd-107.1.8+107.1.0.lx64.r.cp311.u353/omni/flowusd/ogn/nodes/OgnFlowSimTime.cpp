// Copyright (c) 2019-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include <carb/Defines.h>

#include <omni/flowusd/IFlowUsd.h>

#include <OgnFlowSimTimeDatabase.h>

namespace omni
{
namespace flow
{
class OgnFlowSimTime
{
public:
    static bool getIsActionGraph(const GraphContextObj& context)
    {
        GraphObj graphObj = context.iContext->getGraph(context);
        const char* evaluatorName = graphObj.iGraph->getEvaluatorName(graphObj);

        return (strcmp(evaluatorName, "execution") == 0);
    }

    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        OgnFlowSimTime& state = OgnFlowSimTimeDatabase::sSharedState<OgnFlowSimTime>(nodeObj);

        state.iFace_ = carb::getFramework()->tryAcquireInterface<IFlowUsd>();
        CARB_ASSERT(state.iFace_);

        GraphObj graphObj = context.iContext->getGraph(context);
        const char* evaluatorName = graphObj.iGraph->getEvaluatorName(graphObj);

        const bool isActionGraph = getIsActionGraph(context);

        // Create exec in for action graph node
        if (isActionGraph)
        {
            if (!nodeObj.iNode->getAttributeExists(nodeObj, "inputs:execIn"))
            {
                nodeObj.iNode->createAttribute(nodeObj, "execIn",
                                               { BaseDataType::eUInt, 1, 0, AttributeRole::eExecution }, nullptr,
                                               nullptr, AttributePortType::kAttributePortType_Input,
                                               ExtendedAttributeType::kExtendedAttributeType_Regular, nullptr);
            }
        }
    }

    static bool compute(OgnFlowSimTimeDatabase& db)
    {
        auto* iFace = db.sharedState<OgnFlowSimTime>().iFace_;

        db.outputs.lastAbsoluteSimTime() = iFace->getLastAbsoluteSimTime();
        db.outputs.lastFaultAbsoluteSimTime() = iFace->getLastFaultAbsoluteSimTime();
        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }

private:
    IFlowUsd* iFace_;
};

REGISTER_OGN_NODE()

}
}
