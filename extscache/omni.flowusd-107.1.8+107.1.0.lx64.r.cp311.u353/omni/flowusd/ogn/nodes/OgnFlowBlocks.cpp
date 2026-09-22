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

#include <OgnFlowBlocksDatabase.h>

namespace omni
{
namespace flow
{
class OgnFlowBlocks
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
        OgnFlowBlocks& state = OgnFlowBlocksDatabase::sSharedState<OgnFlowBlocks>(nodeObj);

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

    static bool compute(OgnFlowBlocksDatabase& db)
    {
        NodeObj nodeObj = db.abi_node();

        auto* iFace = db.sharedState<OgnFlowBlocks>().iFace_;
        if (!iFace)
        {
            return false;
        }

        db.outputs.maxBlockCount() = iFace->getMaxBlockCount();
        db.outputs.activeBlockCount() = iFace->getActiveBlockCount();
        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }

private:
    IFlowUsd* iFace_;
};

REGISTER_OGN_NODE()

}
}
