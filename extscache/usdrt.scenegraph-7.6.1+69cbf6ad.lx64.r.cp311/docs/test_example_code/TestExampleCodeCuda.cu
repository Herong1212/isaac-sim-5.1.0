// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#include <carb/Types.h>
#include <omni/fabric/batch/Defines.h>
#include <omni/fabric/batch/Types.h>
#include <omni/fabric/batch/View.h>
#include <usdrt/scenegraph/usd/rt/primSelection.h>

// Begin CUDA code for prim processing on GPU example
__global__ void changeColors_impl(const omni::fabric::batch::View view, omni::fabric::batch::AttributeRef displayColors)
{
    const unsigned int index = blockIdx.x * blockDim.x + threadIdx.x;
    const unsigned int gridStride = blockDim.x * gridDim.x;

    omni::fabric::batch::ViewIterator iter(view, index);

    while (iter.advance(gridStride))
    {
        iter.getArrayAttributeWr<carb::Float3>(displayColors).elements[0] = { 1, 0, 0};
    }
}

void changeColors(const usdrt::RtPrimSelection selection, omni::fabric::batch::AttributeRef displayColors)
{
    const dim3 blockDim(768);
    const dim3 gridDim((selection.GetCount() + blockDim.x - 1) / blockDim.x);

    changeColors_impl<<<gridDim, blockDim>>>(selection.GetBatchView(), displayColors);
}
// End CUDA code for prim processing on GPU example
