// Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

__global__ void adjustExposureKernel(cudaSurfaceObject_t surfObj, int width, int height, float exposure)
{
    unsigned int x = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int y = blockIdx.y * blockDim.y + threadIdx.y;
    if (x < width && y < height) {
        uchar4 data = {0, 0, 0, 0};
        surf2Dread(&data,  surfObj, x * 4, y);
        float multiplier = pow(2.f, exposure);
        data.x = (unsigned char)min(data.x * multiplier, 255.f);
        data.y = (unsigned char)min(data.y * multiplier, 255.f);
        data.z = (unsigned char)min(data.z * multiplier, 255.f);
        // Write to output surface
        surf2Dwrite(data, surfObj, x * 4, y);
    }
}

extern "C"
void adjustExposure(cudaSurfaceObject_t surfObj, int width, int height, float exposure, cudaStream_t stream)
{
    dim3 dimBlock(32, 32);
    dim3 dimGrid((width  + dimBlock.x - 1) / dimBlock.x,
                 (height + dimBlock.y - 1) / dimBlock.y);

    adjustExposureKernel<<<dimGrid, dimBlock, 0, stream>>>(surfObj, width, height, exposure);
}
