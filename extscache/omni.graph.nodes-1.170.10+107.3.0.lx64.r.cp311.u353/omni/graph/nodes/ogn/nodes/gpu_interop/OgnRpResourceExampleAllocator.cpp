// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnRpResourceExampleAllocatorDatabase.h"

#include <carb/graphics/GraphicsTypes.h>
#include <carb/logging/Log.h>

#include <cuda/include/cuda_runtime_api.h>

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/NodeTypeRegistrar.h>

#include <rtx/utils/GraphicsDescUtils.h>
#include <rtx/resourcemanager/ResourceManager.h>

#include <omni/kit/KitUtils.h>
#include <omni/kit/renderer/IRenderer.h>
#include <gpu/foundation/FoundationTypes.h>

#include <omni/math/linalg/vec.h>

using omni::math::linalg::vec3f;

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

class OgnRpResourceExampleAllocator
{
    // NOTE: this node is meant only as an early example of gpu interop on a prerender graph.
    // Storing a pointer to an RpResource is a temporary measure that will not work in a
    // multi-node setting.

    bool previousSuccess;
    bool previousReload;
    std::vector<rtx::resourcemanager::RpResource*> resourcePointerCollection;
    std::vector<uint64_t> pointCountCollection;
    std::vector<NameToken> primPathCollection;

public:
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        // std::cout << "OgnRpResourceExampleAllocator::initialize" << std::endl;
    }

    static void release(const NodeObj& nodeObj)
    {
        // std::cout << "OgnRpResourceExampleAllocator::release" << std::endl;

        if (auto renderer = carb::getCachedInterface<omni::kit::renderer::IRenderer>())
        {
            if (auto gpuFoundation = renderer->getGpuFoundation())
            {
                rtx::resourcemanager::ResourceManager* resourceManager = gpuFoundation->getResourceManager();
                rtx::resourcemanager::Context* resourceManagerContext = gpuFoundation->getResourceManagerContext();

                if (resourceManager == nullptr || resourceManagerContext == nullptr)
                {
                    // nothing to do if the resource manager was already destroyed
                    return;
                }

                auto& internalState =
                    OgnRpResourceExampleAllocatorDatabase::sSharedState<OgnRpResourceExampleAllocator>(nodeObj);
                auto& resourcePointerCollection = internalState.resourcePointerCollection;
                const size_t resourceCount = resourcePointerCollection.size();
                for (size_t i = 0; i < resourceCount; i++)
                {
                    auto rpResource = resourcePointerCollection[i];
                    if (rpResource)
                        resourceManager->releaseResource(*rpResource);
                }
            }
        }
    }

    static bool compute(OgnRpResourceExampleAllocatorDatabase& db)
    {
        CARB_PROFILE_ZONE(1, "OgnRpResourceExampleAllocator::compute");
        rtx::resourcemanager::Context* resourceManagerContext = nullptr;
        rtx::resourcemanager::ResourceManager* resourceManager = nullptr;

        auto& internalState = db.sharedState<OgnRpResourceExampleAllocator>();

        const bool previousSuccess = internalState.previousSuccess;
        const bool previousReload = internalState.previousReload;
        internalState.previousSuccess = false;
        internalState.previousReload = false;
        const bool verbose = db.inputs.verbose();

        if (auto renderer = carb::getCachedInterface<omni::kit::renderer::IRenderer>())
        {
            if (auto gpuFoundation = renderer->getGpuFoundation())
            {
                resourceManager = gpuFoundation->getResourceManager();
                resourceManagerContext = gpuFoundation->getResourceManagerContext();
            }
        }

        cudaStream_t stream = (cudaStream_t)db.inputs.stream();

        if (verbose)
        {
            std::cout << "OgnRpResourceExampleAllocator::compute -- cudaStream: " << stream << std::endl;
        }

        if (!stream)
        {
            db.outputs.resourcePointerCollection().resize(0);
            db.outputs.pointCountCollection().resize(0);
            db.outputs.primPathCollection().resize(0);
            return false;
        }

        if (resourceManager == nullptr || resourceManagerContext == nullptr)
        {
            db.outputs.resourcePointerCollection().resize(0);
            db.outputs.pointCountCollection().resize(0);
            db.outputs.primPathCollection().resize(0);
            return false;
        }

        auto& resourcePointerCollection = internalState.resourcePointerCollection;
        auto& pointCountCollection = internalState.pointCountCollection;
        auto& primPathCollection = internalState.primPathCollection;

        const bool reloadAttr = db.inputs.reload();
        if ((reloadAttr && !previousReload) || !previousSuccess)
        {
            internalState.previousReload = true;

            if (resourcePointerCollection.size() != 0)
            {
                if (verbose)
                {
                    std::cout << "freeing RpResource." << std::endl;
                }

                const size_t resourceCount = resourcePointerCollection.size();
                for (size_t i = 0; i < resourceCount; i++)
                {
                    auto rpResource = resourcePointerCollection[i];
                    if (rpResource)
                        resourceManager->releaseResource(*rpResource);
                }

                resourcePointerCollection.resize(0);
                pointCountCollection.resize(0);
                primPathCollection.resize(0);
            }
        }

        if (resourcePointerCollection.size() == 0)
        {
            const auto& pointsAttr = db.inputs.points();

            const size_t pointsCount = pointsAttr.size();
            const vec3f* points = pointsAttr.data();
            const NameToken primPath = db.inputs.primPath();

            if (pointsCount == 0)
                return false;
            if (points == nullptr)
                return false;

            // const uint64_t dimension = 4;
            const uint64_t dimension = 3;
            const uint64_t size = pointsCount * dimension * sizeof(float);

            const uint32_t deviceIndex = 0;

            carb::graphics::BufferUsageFlags usageFlags = carb::graphics::kBufferUsageFlagNone;
            usageFlags |= carb::graphics::kBufferUsageFlagShaderResourceStorage;
            usageFlags |= carb::graphics::kBufferUsageFlagVertexBuffer;
            usageFlags |= carb::graphics::kBufferUsageFlagRawOrStructuredBuffer;
            usageFlags |= carb::graphics::kBufferUsageFlagRaytracingBuffer;
            carb::graphics::BufferDesc bufferDesc = rtx::RtxBufferDesc(size, "Mesh Buffer", usageFlags);

            rtx::resourcemanager::ResourceDesc resourceDesc = {};
            resourceDesc.mode = rtx::resourcemanager::ResourceMode::eDefault;
            resourceDesc.memoryLocation = carb::graphics::MemoryLocation::eDevice;
            resourceDesc.category = rtx::resourcemanager::ResourceCategory::eVertexBuffer;
            resourceDesc.usageFlags = rtx::resourcemanager::kResourceUsageFlagCudaShared |
                                      rtx::resourcemanager::kResourceUsageFlagNoSyncScope;
            resourceDesc.deviceMask = OMNI_ALL_DEVICES_MASK;
            resourceDesc.creationDeviceIndex = deviceIndex;

            for (size_t i = 0; i < 2; i++)
            {
                rtx::resourcemanager::RpResource* rpResource =
                    resourceManager->getResourceFromBufferDesc(*resourceManagerContext, bufferDesc, resourceDesc);

                float* cpuPtr = new float[pointsCount * dimension];
                for (size_t j = 0; j < pointsCount; j++)
                {
                    cpuPtr[dimension * j] = points[j][0];
                    cpuPtr[dimension * j + 1] = points[j][1];
                    cpuPtr[dimension * j + 2] = points[j][2];
                    if (dimension == 4)
                        cpuPtr[dimension * j + 3] = 1.f;
                }
                void* cudaPtr = resourceManager->getCudaDevicePointer(*rpResource, deviceIndex);
                cudaError_t err =
                    cudaMemcpy(cudaPtr, cpuPtr, pointsCount * dimension * sizeof(float), cudaMemcpyHostToDevice);
                delete[] cpuPtr;

                if (verbose)
                {
                    std::cout << "prim: " << db.tokenToString(primPath) << std::endl;
                    std::cout << "cudaMemcpy to device error code: " << err << std::endl;
                    std::cout << "errorName: " << cudaGetErrorName(err) << std::endl;
                    std::cout << "errorDesc: " << cudaGetErrorString(err) << std::endl;
                    std::cout << std::endl;
                }

                resourcePointerCollection.push_back(rpResource);
            }

            pointCountCollection.push_back((uint64_t)pointsCount);
            primPathCollection.push_back(primPath);

            db.outputs.resourcePointerCollection.resize(resourcePointerCollection.size());
            memcpy(db.outputs.resourcePointerCollection().data(), resourcePointerCollection.data(),
                   resourcePointerCollection.size() * sizeof(uint64_t));
            db.outputs.pointCountCollection.resize(pointCountCollection.size());
            memcpy(db.outputs.pointCountCollection().data(), pointCountCollection.data(),
                   pointCountCollection.size() * sizeof(uint64_t));
            db.outputs.primPathCollection.resize(primPathCollection.size());
            memcpy(db.outputs.primPathCollection().data(), primPathCollection.data(),
                   primPathCollection.size() * sizeof(NameToken));
        }

        if (resourcePointerCollection.size() == 0)
        {
            return false;
        }

        db.outputs.stream() = (uint64_t)stream;

        internalState.previousSuccess = true;
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
}
