// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnRenderPreprocessEntryDatabase.h"

#include <omni/graph/core/GpuInteropEntryUserData.h>
#include <omni/graph/core/iComputeGraph.h>

namespace omni
{
namespace graph
{
namespace core
{

// OmniGraph nodes executed as a render preprocess need to be connected downstream of an entry point node
// in order to be scheduled as part of the render graph.
// Scheduling of cuda interop nodes begins with one of these entry nodes, which passes data (e.g. a cuda stream
// identifier) to downstream nodes.

class OgnRenderPreprocessEntry
{
public:
    static bool compute(OgnRenderPreprocessEntryDatabase& db)
    {
        CARB_PROFILE_ZONE(1, "OgnRenderPreprocessEntry::compute");

        auto var = db.getVariable("__cudaInteropState");
        if (!var.isValid())
            return false;

        auto userData = reinterpret_cast<GpuInteropCudaEntryUserData*>(*var.get<uint64_t>());
        if (!userData)
            return false;

        db.outputs.stream() = (uint64_t)db.getCudaStream();
        db.outputs.simTime() = userData->simTime;
        db.outputs.rationalTimeOfSimNumerator() = userData->rationalTimeOfSimNumerator;
        db.outputs.rationalTimeOfSimDenominator() = userData->rationalTimeOfSimDenominator;
        db.outputs.hydraTime() = userData->hydraTime;

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
