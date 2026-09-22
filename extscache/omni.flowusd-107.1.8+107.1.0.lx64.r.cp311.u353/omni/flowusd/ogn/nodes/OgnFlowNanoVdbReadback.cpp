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

#include <OgnFlowNanoVdbReadbackDatabase.h>

namespace omni
{
namespace flow
{
class OgnFlowNanoVdbReadback
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
        OgnFlowNanoVdbReadback& state = OgnFlowNanoVdbReadbackDatabase::sSharedState<OgnFlowNanoVdbReadback>(nodeObj);

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

    static bool compute(OgnFlowNanoVdbReadbackDatabase& db)
    {
        NodeObj nodeObj = db.abi_node();

        auto* iFace = db.sharedState<OgnFlowNanoVdbReadback>().iFace_;

        omni::flow::FlowUsdNanoVdbReadback readback = {};
        iFace->mapLatestNanoVdbReadback(&readback);

        db.outputs.temperature().resize(readback.temperatureNanoVdbCount);
        if (readback.temperatureNanoVdb)
        {
            memcpy(db.outputs.temperature().data(), readback.temperatureNanoVdb,
                   readback.temperatureNanoVdbCount * sizeof(uint32_t));
        }

        db.outputs.fuel().resize(readback.fuelNanoVdbCount);
        if (readback.fuelNanoVdb)
        {
            memcpy(db.outputs.fuel().data(), readback.fuelNanoVdb, readback.fuelNanoVdbCount * sizeof(uint32_t));
        }

        db.outputs.burn().resize(readback.burnNanoVdbCount);
        if (readback.burnNanoVdb)
        {
            memcpy(db.outputs.burn().data(), readback.burnNanoVdb, readback.burnNanoVdbCount * sizeof(uint32_t));
        }

        db.outputs.smoke().resize(readback.smokeNanoVdbCount);
        if (readback.smokeNanoVdb)
        {
            memcpy(db.outputs.smoke().data(), readback.smokeNanoVdb, readback.smokeNanoVdbCount * sizeof(uint32_t));
        }

        db.outputs.velocity().resize(readback.velocityNanoVdbCount);
        if (readback.velocityNanoVdb)
        {
            memcpy(db.outputs.velocity().data(), readback.velocityNanoVdb,
                   readback.velocityNanoVdbCount * sizeof(uint32_t));
        }

        db.outputs.divergence().resize(readback.divergenceNanoVdbCount);
        if (readback.divergenceNanoVdb)
        {
            memcpy(db.outputs.divergence().data(), readback.divergenceNanoVdb,
                   readback.divergenceNanoVdbCount * sizeof(uint32_t));
        }

        iFace->unmapLastestNanoVdbReadback();

        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }

private:
    IFlowUsd* iFace_;
};

REGISTER_OGN_NODE()

}
}
