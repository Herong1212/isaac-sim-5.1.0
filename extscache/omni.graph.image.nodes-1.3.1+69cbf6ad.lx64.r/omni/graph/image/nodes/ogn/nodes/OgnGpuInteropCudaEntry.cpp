// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnGpuInteropCudaEntryDatabase.h"

#include <omni/graph/core/GpuInteropEntryUserData.h>

namespace omni
{
namespace graph
{
namespace core
{

// Replaces deprecated RenderPostprocessEntry

// Downstream nodes of OgnGpuInteropCudaEntry can write Cuda code directly and they will be scheduled on the
// Gpu Foundations Rendergraph for Device 0. GpuInteropCudaEntry passes the cuda buffer pointer and
// associated metadata for a specific named resource outputted by the Rtx Renderer (such as LdrColor for
// final color). This buffer is a read/write buffer, and changes will be passed to consumer of the renderer's
// output

class OgnGpuInteropCudaEntry
{
public:
    static bool compute(OgnGpuInteropCudaEntryDatabase& db)
    {
        auto var = db.getVariable("__cudaInteropState");
        if (!var.isValid())
            return false;

        auto userData = reinterpret_cast<GpuInteropCudaEntryUserData*>(*var.get<uint64_t>());
        if (!userData)
            return false;

        GpuInteropCudaResourceMap& cudaRsrcMap = userData->cudaRsrcMap;

        std::string sourceName = db.inputs.sourceName();

        auto it = cudaRsrcMap.find(sourceName);
        if (it == cudaRsrcMap.end())
        {
            return false;
        }

        GpuInteropCudaResourceData& renderVarData = it->second;

        db.outputs.cudaMipmappedArray() = (uint64_t)renderVarData.cudaResource;
        db.outputs.width() = renderVarData.width;
        db.outputs.height() = renderVarData.height;
        db.outputs.isBuffer() = renderVarData.isBuffer;
        db.outputs.bufferSize() = renderVarData.depthOrArraySize;
        db.outputs.mipCount() = (uint32_t)renderVarData.mipCount;
        db.outputs.format() = (uint64_t)renderVarData.format;
        db.outputs.stream() = (uint64_t)db.getCudaStream();
        db.outputs.simTime() = userData->simTime;
        db.outputs.rationalTimeOfSimNumerator() = userData->rationalTimeOfSimNumerator;
        db.outputs.rationalTimeOfSimDenominator() = userData->rationalTimeOfSimDenominator;
        db.outputs.hydraTime() = userData->hydraTime;
        db.outputs.externalTimeOfSimFrame() = userData->externalTimeOfSimFrame;
        db.outputs.frameId() = userData->frameId;

        return true;
    }

    static void initializeType(const NodeTypeObj& nodeTypeObj)
    {
        OgnGpuInteropCudaEntryDatabase::initializeType(nodeTypeObj);
    }
};

REGISTER_OGN_NODE()
}
}
}
