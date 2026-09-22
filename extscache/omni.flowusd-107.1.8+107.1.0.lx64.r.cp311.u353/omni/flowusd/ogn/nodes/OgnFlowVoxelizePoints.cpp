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

#include <OgnFlowVoxelizePointsDatabase.h>

namespace omni
{
namespace flow
{
class OgnFlowVoxelizePoints
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
        OgnFlowVoxelizePoints& state = OgnFlowVoxelizePointsDatabase::sSharedState<OgnFlowVoxelizePoints>(nodeObj);

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

    static bool compute(OgnFlowVoxelizePointsDatabase& db)
    {
        NodeObj nodeObj = db.abi_node();

        auto* iFace = db.sharedState<OgnFlowVoxelizePoints>().iFace_;

        auto output =
            iFace->voxelizePoints((const carb::Float3*)db.inputs.points().data(), db.inputs.points().size(),
                                  (const carb::Float3*)db.inputs.colors().data(), db.inputs.colors().size(),
                                  db.inputs.localToWorld().data(), 16u, db.inputs.cellSize(), db.inputs.maxBlocks());

        omni::flow::FlowUsdVoxelizePointsReadback readback = {};
        if (iFace->mapVoxelizePointsOutputReadback(output, &readback, true))
        {
            db.outputs.redNanoVdb.resize(readback.redNanoVdbCount);
            db.outputs.greenNanoVdb.resize(readback.greenNanoVdbCount);
            db.outputs.blueNanoVdb.resize(readback.blueNanoVdbCount);
            db.outputs.alphaNanoVdb.resize(readback.alphaNanoVdbCount);

            for (size_t idx = 0u; idx < readback.redNanoVdbCount; idx++)
            {
                db.outputs.redNanoVdb()[idx] = readback.redNanoVdb[idx];
            }
            for (size_t idx = 0u; idx < readback.greenNanoVdbCount; idx++)
            {
                db.outputs.greenNanoVdb()[idx] = readback.greenNanoVdb[idx];
            }
            for (size_t idx = 0u; idx < readback.blueNanoVdbCount; idx++)
            {
                db.outputs.blueNanoVdb()[idx] = readback.blueNanoVdb[idx];
            }
            for (size_t idx = 0u; idx < readback.alphaNanoVdbCount; idx++)
            {
                db.outputs.alphaNanoVdb()[idx] = readback.alphaNanoVdb[idx];
            }

            iFace->releaseVoxelizePointsOutput(output);
        }

        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }

private:
    IFlowUsd* iFace_;
};

REGISTER_OGN_NODE()

}
}
