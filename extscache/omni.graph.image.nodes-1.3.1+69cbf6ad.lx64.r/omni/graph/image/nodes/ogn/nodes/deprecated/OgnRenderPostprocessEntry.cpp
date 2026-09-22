// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnRenderPostprocessEntryDatabase.h"

#include <omni/graph/core/GpuInteropEntryUserData.h>
#include <omni/graph/core/iComputeGraph.h>

namespace omni
{
namespace graph
{
namespace core
{

// OmniGraph nodes which postprocess the RTX renderer output need to be connected downstream of a RenderPostprocessEntry
// node. The RenderPostprocessEntry outputs the R/W RgResource of the texture's final color (along with associated
// metadata such as width, height, etc.) as OmniGraph attributes which can be read by downstream nodes. Modifications to
//  this RgResource will be reflected in the viewport. The format of the RgResource is an RgTexture created with CUDA
// interoperability as opposed to a buffer.

class OgnRenderPostprocessEntry
{
public:
    static bool compute(OgnRenderPostprocessEntryDatabase& db)
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
        db.outputs.mipCount() = (uint32_t)renderVarData.mipCount;
        db.outputs.format() = (uint64_t)renderVarData.format;
        db.outputs.stream() = (uint64_t)db.getCudaStream();
        db.outputs.simTime() = userData->simTime;
        db.outputs.rationalTimeOfSimNumerator() = userData->rationalTimeOfSimNumerator;
        db.outputs.rationalTimeOfSimDenominator() = userData->rationalTimeOfSimDenominator;
        db.outputs.hydraTime() = userData->hydraTime;

        return true;
    }

    static void initialize(const GraphContextObj&, const NodeObj&)
    {
        CARB_LOG_WARN_ONCE("OgnRenderPostprocessEntry is deprecated. Please use OgnGpuInteropCudaEntry");
    }

    static void initializeType(const NodeTypeObj& nodeTypeObj)
    {
        OgnRenderPostprocessEntryDatabase::initializeType(nodeTypeObj);
    }
};

REGISTER_OGN_NODE()
}
}
}
