// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnGpuInteropRenderProductEntryDatabase.h"
#include <omni/graph/core/GpuInteropEntryUserData.h>
#include <omni/graph/core/iComputeGraph.h>

namespace omni
{
namespace graph
{
namespace core
{

// Replaces depreciated GpuInteropRenderProductEntry

// Downstream nodes of OgnGpuInteropRenderProductEntry can write Cuda code directly and they will be scheduled on the
// Gpu Foundations Rendergraph for Device 0. GpuInteropCudaEntry passes the cuda buffer pointer and
// associated metadata for a specific named resource outputted by the Rtx Renderer (such as LdrColor for
// final color). This buffer is a read/write buffer, and changes will be passed to consumer of the renderer's
// output

class OgnGpuInteropRenderProductEntry
{
public:
    static bool compute(OgnGpuInteropRenderProductEntryDatabase& db)
    {
        auto var = db.getVariable("__rpInteropState");
        if (!var.isValid())
            return false;

        auto userData = reinterpret_cast<GpuInteropRpEntryUserData*>(*var.get<uint64_t>());
        if (!userData)
            return false;

        db.outputs.simTime() = userData->simTime;
        db.outputs.hydraTime() = userData->hydraTime;
        db.outputs.rp() = (uint64_t)userData->rp;
        db.outputs.gpu() = (uint64_t)userData->gpu;
        db.outputs.exec() = ExecutionAttributeState::kExecutionAttributeStateEnabled;

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
