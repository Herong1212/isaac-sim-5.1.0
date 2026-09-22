// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// This include must come first in order to use PCH, and it must be exactly:
// #include "UsdPCH.h"
// For more information, see:
// https://premake.github.io/docs/Precompiled-Headers/
// clang-format off
#include "UsdPCH.h"
// clang-format on

#include "TestFramework.h"
#include "TestHelpers.h"

#include <omni/fabric/core/Fabric.h>
#include <omni/fabric/usd/FabricUsd.h>
#include <omni/fabric/stage/SimStageWithHistory.h>
#include <omni/fabric/stage/StageReaderWriter.h>

#include <cuda/include/cuda_runtime_api.h>
#include <cuda/include/cuda.h>

using namespace omni::fabric;

TEST_CASE("Modify prim in USD stage using Fabric",
          "[stageReaderWriter]"
          "[CUDA]"
          "[fabricDocsInlineSample]"
          "[component=kit][owner=rtonge][priority=mandatory]")
{
    P2ATestFramework framework;
   
    pxr::UsdStageRefPtr usdStage = pxr::UsdStage::CreateInMemory();
    UsdStageId usdStageId = getUsdStageId(usdStage);

    SimStageWithHistory swh(usdStageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eCuda);
    StageReaderWriter stage(swh.getWorkingFabricId());

    // Make USD stage containing a cube
    // example-begin create-cube
    pxr::UsdPrim prim = usdStage->DefinePrim(pxr::SdfPath("/cube"), pxr::TfToken("Cube"));
    prim.CreateAttribute(pxr::TfToken("size"), pxr::SdfValueTypeNames->Double).Set(1.0);
    // example-end create-cube

    // Prefetch prim to fabric
    // example-begin prefetch-prim
    Path primPath("/cube");
    swh.prefetchPrimFromUsdStage(primPath);
    // example-end prefetch-prim

    // Make the cube 10 times bigger using FC
    // example-begin scale-cube
    double& size = *stage.getAttribute<double>(primPath, Token("size"));
    size = size * 10;
    // example-end scale-cube

    // Write FC back to USD
    // example-begin writeback
    omni::fabric::exportUsdPrimData(omni::fabric::Fabric(swh.getWorkingFabricId()));
    // example-end writeback

    // Check that the value got back to USD
    // example-begin check-value-changed-in-usd
    pxr::UsdAttribute sizeAttr = prim.GetAttribute(pxr::TfToken("size"));
    double value;
    sizeAttr.Get(&value);
    CHECK(value == 10.0f);
    // example-end check-value-changed-in-usd
}

TEST_CASE("Modify many prims in USD stage using Fabric",
          "[stageReaderWriter]"
          "[CUDA]"
          "[fabricDocsInlineSample]"
          "[component=kit][owner=rtonge][priority=mandatory]")
{
    P2ATestFramework framework;

    pxr::UsdStageRefPtr usdStage = pxr::UsdStage::CreateInMemory();
    UsdStageId usdStageId = getUsdStageId(usdStage);
    SimStageWithHistory swh(usdStageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eCuda);
    StageReaderWriter stage(swh.getWorkingFabricId());
    omni::fabric::Fabric fabric(swh.getWorkingFabricId());

    // Make USD stage containing 1000 cubes
    // example-begin create-many-cubes
    const size_t cubeCount = 1000;
    for (size_t i = 0; i != cubeCount; i++)
    {
        pxr::SdfPath path("/cube_" + std::to_string(i));
        pxr::UsdPrim prim = usdStage->DefinePrim(path, pxr::TfToken("Cube"));
        prim.CreateAttribute(pxr::TfToken("size"), pxr::SdfValueTypeNames->Double).Set(1.0);
    }
    // example-end create-many-cubes

    // example-begin prefetch-many-cubes
    for (size_t i = 0; i != cubeCount; i++)
    {
        Path path(("/cube_" + std::to_string(i)).c_str());
        swh.prefetchPrimFromUsdStage(path);
    }
    // example-end prefetch-many-cubes

    // example-begin find-all-cubes
    AttrNameAndType cubeTag(omni::fabric::s_PrimTypeType, Token("Cube"));
    PrimBucketList cubeBuckets = stage.findPrims({ cubeTag });
    // example-end find-all-cubes

    // example-begin iterate-over-cubes
    for (size_t bucket = 0; bucket != cubeBuckets.bucketCount(); bucket++)
    {
        auto sizes = stage.getAttributeArray<double>(cubeBuckets, bucket, Token("size"));
        for (double& size : sizes)
        {
            size *= 10;
        }
    }
    // example-end iterate-over-cubes

    // example-begin writeback-cubes-and-check
    omni::fabric::exportUsdPrimData(fabric);
    for (size_t i = 0; i != cubeCount; i++)
    {
        pxr::SdfPath path("/cube_" + std::to_string(i));
        pxr::UsdPrim prim = usdStage->GetPrimAtPath(path);
        pxr::UsdAttribute sizeAttr = prim.GetAttribute(pxr::TfToken("size"));
        double value;
        sizeAttr.Get(&value);
        CHECK(value == 10.0f);
    }
    // example-end writeback-cubes-and-check
}

CUfunction compileKernel(const char* sourceCode, const char* functionName, CUdevice device, CUcontext context);

TEST_CASE("Modify many prims in USD stage using Fabric with GPU",
          "[stageReaderWriter]"
          "[CUDA]"
          "[fabricDocsInlineSample]"
          "[component=kit][owner=rtonge][priority=mandatory]")
{
    P2ATestFramework framework;
    CUDAdeviceAndContext cuda;

    pxr::UsdStageRefPtr usdStage = pxr::UsdStage::CreateInMemory();
    UsdStageId usdStageId = getUsdStageId(usdStage);
    SimStageWithHistory swh(usdStageId, 1, { 1, 30 }, omni::fabric::GpuComputeType::eCuda);
    StageReaderWriter stage(swh.getWorkingFabricId());

    omni::fabric::Fabric fabric(swh.getWorkingFabricId());

    // Make USD stage containing 1000 cubes
    // example-begin create-many-cubes2
    const size_t cubeCount = 1000;
    for (size_t i = 0; i != cubeCount; i++)
    {
        pxr::SdfPath path("/cube_" + std::to_string(i));
        pxr::UsdPrim prim = usdStage->DefinePrim(path, pxr::TfToken("Cube"));
        prim.CreateAttribute(pxr::TfToken("size"), pxr::SdfValueTypeNames->Double).Set(1.0);
    }

    for (size_t i = 0; i != cubeCount; i++)
    {
        Path path(("/cube_" + std::to_string(i)).c_str());
        swh.prefetchPrimFromUsdStage(path);
    }

    AttrNameAndType cubeTag(omni::fabric::s_PrimTypeType, Token("Cube"));
    PrimBucketList cubeBuckets = stage.findPrims({ cubeTag });
    // example-end create-many-cubes2

    // example-begin many-cubes-init-gpu
    static const char* scaleCubes =
        "   extern \"C\" __global__"
        "   void scaleCubes(double* cubeSizes, size_t count)"
        "   {"
        "       size_t i = blockIdx.x * blockDim.x + threadIdx.x;"
        "       if(count<=i) return;"
        ""
        "       cubeSizes[i] *= 10.0;"
        "   }";

    CUfunction kernel = compileKernel(scaleCubes, "scaleCubes", cuda.device, cuda.context);
    // example-end many-cubes-init-gpu

    // example-begin iterate-over-cubes-gpu
    for (size_t bucket = 0; bucket != cubeBuckets.bucketCount(); bucket++)
    {
        gsl::span<double> sizesD = stage.getAttributeArrayGpu<double>(cubeBuckets, bucket, Token("size"));

        double* ptr = sizesD.data();
        size_t elemCount = sizesD.size();
        void* args[] = { &ptr, &elemCount };
        int blockSize, minGridSize;
        cuOccupancyMaxPotentialBlockSize(&minGridSize, &blockSize, kernel, nullptr, 0, 0);
        CUresult err = cuLaunchKernel(kernel, minGridSize, 1, 1, blockSize, 1, 1, 0, NULL, args, 0);
        REQUIRE(!err);
    }
    // example-end iterate-over-cubes-gpu

    // example-begin writeback-cubes-and-check2
    omni::fabric::exportUsdPrimData(fabric);

    for (size_t i = 0; i != cubeCount; i++)
    {
        pxr::SdfPath path("/cube_" + std::to_string(i));
        pxr::UsdPrim prim = usdStage->GetPrimAtPath(path);
        pxr::UsdAttribute sizeAttr = prim.GetAttribute(pxr::TfToken("size"));
        double value;
        sizeAttr.Get(&value);
        CHECK(value == 10.0f);
    }
    // example-end writeback-cubes-and-check2
}
