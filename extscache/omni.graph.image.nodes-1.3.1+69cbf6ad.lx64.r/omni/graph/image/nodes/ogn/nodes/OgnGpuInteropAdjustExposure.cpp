// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnGpuInteropAdjustExposureDatabase.h"

#include <carb/graphics/GraphicsTypes.h>
#include <carb/logging/Log.h>

#include <cuda/include/cuda_runtime_api.h>
#include <omni/graph/core/iComputeGraph.h>

#define CUDA_SUCCEEDED(result) ((result) == cudaSuccess)
#define CUDA_FAILED(result) ((result) != cudaSuccess)

#define CUDA_CHECK(result)                                                                                             \
    {                                                                                                                  \
        cudaError_t _result = (result);                                                                                \
        if (CUDA_FAILED(_result))                                                                                      \
        {                                                                                                              \
            CARB_LOG_ERROR(                                                                                            \
                "CUDA error %d: %s - %s)", (_result), cudaGetErrorName(_result), cudaGetErrorString(_result));         \
        }                                                                                                              \
    }

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

extern "C" void adjustExposure(cudaSurfaceObject_t surfObj, int width, int height, float exposure, cudaStream_t stream);

// OmniGraph nodes which postprocess the RTX renderer output need to be connected downstream of a RenderPostprocessEntry
// node. These connections will contain the R/W RgResource and associated metadata of the RTX renderer output and
// modifications on this RgResource will be reflected in the viewport.

class OgnGpuInteropAdjustExposure
{
public:
    static bool compute(OgnGpuInteropAdjustExposureDatabase& db)
    {
        float exposure = db.inputs.exposure();

        cudaMipmappedArray_t cudaMipmappedArray = (cudaMipmappedArray_t)db.inputs.cudaMipmappedArray();
        if (!cudaMipmappedArray)
            return false;

        uint32_t width = db.inputs.width();
        if (!width)
            return false;

        uint32_t height = db.inputs.height();
        if (!height)
            return false;

        uint16_t mipCount = (uint16_t)db.inputs.mipCount();
        if (!mipCount)
            return false;

        carb::graphics::Format format = (carb::graphics::Format)db.inputs.format();
        if (format == carb::graphics::Format::eUnknown)
            return false;

        cudaStream_t stream = (cudaStream_t)db.inputs.stream();
        if (!stream)
            return false;

        cudaArray_t levelArray;
        CUDA_CHECK(cudaGetMipmappedArrayLevel(&levelArray, cudaMipmappedArray, 0));

        // Specify surface
        struct cudaResourceDesc resDesc;
        memset(&resDesc, 0, sizeof(resDesc));
        resDesc.resType = cudaResourceTypeArray;

        // Create the surface objects
        resDesc.res.array.array = levelArray;
        cudaSurfaceObject_t surfObj = 0;
        CUDA_CHECK(cudaCreateSurfaceObject(&surfObj, &resDesc));

        adjustExposure(surfObj, width, height, exposure, stream);

        // Destroy surface objects
        CUDA_CHECK(cudaDestroySurfaceObject(surfObj));

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
}
