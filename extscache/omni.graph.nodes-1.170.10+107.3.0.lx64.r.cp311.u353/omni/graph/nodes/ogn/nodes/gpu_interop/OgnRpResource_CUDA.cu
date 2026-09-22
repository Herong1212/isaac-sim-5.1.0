// Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include <iostream>

constexpr unsigned sequencePointsBetweenDirectionChanges = 60;
// Start in the middle of the cycle.
constexpr unsigned sequenceStartPoint = sequencePointsBetweenDirectionChanges / 2;
constexpr float speed = 100.0f / sequencePointsBetweenDirectionChanges;

__global__ void modifyPositionsKernel(float3* points, size_t numPoints, float positionChange, int displacementAxis)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (numPoints <= i) return;

    if (displacementAxis == 0)
        points[i].x += positionChange;
    else if (displacementAxis == 1)
        points[i].y += positionChange;
    else
        points[i].z += positionChange;
}

__global__ void modifyPositionsKernel(const float3* pointsRest, float3* pointsDeformed, size_t numPoints, float time, float positionScale, float timeScale, float deformScale)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (numPoints <= i) return;

    pointsDeformed[i].z = pointsRest[i].z + deformScale * (sin(timeScale * time + positionScale * pointsRest[i].x) + cos(timeScale * time + positionScale * pointsRest[i].y));
}

extern "C"
void modifyPositionsTranslation(float3* points, size_t numPoints, unsigned sequenceCounter, int displacementAxis, bool verbose, cudaStream_t stream)
{
    const int nt = 256;
    const int nb = (numPoints + nt - 1) / nt;

    const unsigned currentSequencePoint =
        (sequenceStartPoint + sequenceCounter) % (sequencePointsBetweenDirectionChanges * 2);
    // direction = 1 - 2 if we're in the [30, 60) section of the sequence range.
    const float direction = 1.0f - (2 * (currentSequencePoint >= sequencePointsBetweenDirectionChanges));
    const float positionChange = speed * direction;

    modifyPositionsKernel<<<nb, nt, 0, stream>>>(points, numPoints, positionChange, displacementAxis);

    if (verbose)
    {
        cudaError_t err = cudaDeviceSynchronize();
        std::cout << "cudaMemcpy error code: " << err << std::endl;
        std::cout << "errorName: " << cudaGetErrorName(err) << std::endl;
        std::cout << "errorDesc: " << cudaGetErrorString(err) << std::endl;
        std::cout << std::endl;
    }

}

extern "C"
void modifyPositionsSinusoidal(const float3* pointsRest, float3* pointsDeformed, size_t numPoints, float time, float positionScale, float timeScale, float deformScale, bool verbose, cudaStream_t stream)
{
    const int nt = 256;
    const int nb = (numPoints + nt - 1) / nt;

    modifyPositionsKernel<<<nb, nt, 0, stream>>>(pointsRest, pointsDeformed, numPoints, time, positionScale, timeScale, deformScale);

    if (verbose)
    {
        cudaError_t err = cudaDeviceSynchronize();
        std::cout << "cudaMemcpy error code: " << err << std::endl;
        std::cout << "errorName: " << cudaGetErrorName(err) << std::endl;
        std::cout << "errorDesc: " << cudaGetErrorString(err) << std::endl;
        std::cout << std::endl;
    }

}
