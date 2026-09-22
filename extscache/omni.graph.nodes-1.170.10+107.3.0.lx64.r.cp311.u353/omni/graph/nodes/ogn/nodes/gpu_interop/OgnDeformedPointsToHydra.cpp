// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnDeformedPointsToHydraDatabase.h"

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

#include <omni/hydra/IOmniHydra.h>

#include <omni/graph/core/BundlePrims.h>
#include <omni/math/linalg/vec.h>

using omni::math::linalg::vec3f;

using omni::graph::core::BundleAttributeInfo;
using omni::graph::core::BundlePrim;
using omni::graph::core::BundlePrims;
using omni::graph::core::ConstBundlePrim;
using omni::graph::core::ConstBundlePrims;

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

class OgnDeformedPointsToHydra
{
    // NOTE: this node is meant only for early usage of gpu interop on a prerender graph.
    // Storing a pointer to an RpResource is a temporary measure that will not work in a
    // multi-node setting.

    bool previousSuccess;
    rtx::resourcemanager::RpResource* resourcePointer;
    uint64_t pointCount;
    NameToken primPath;

public:
    static void initInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        OgnDeformedPointsToHydraDatabase db(nodeObj);
        auto& internalState =
            OgnDeformedPointsToHydraDatabase::sPerInstanceState<OgnDeformedPointsToHydra>(nodeObj, instanceId);
        internalState.resourcePointer = nullptr;
        internalState.pointCount = 0;
        internalState.primPath = db.stringToToken("");
        internalState.previousSuccess = false;
    }

    static bool compute(OgnDeformedPointsToHydraDatabase& db)
    {
        CARB_PROFILE_ZONE(1, "OgnDeformedPointsToHydra::compute");
        rtx::resourcemanager::Context* resourceManagerContext = nullptr;
        rtx::resourcemanager::ResourceManager* resourceManager = nullptr;

        auto& internalState = db.perInstanceState<OgnDeformedPointsToHydra>();

        const bool previousSuccess = internalState.previousSuccess;
        internalState.previousSuccess = false;
        const bool verbose = db.inputs.verbose();

        if (db.inputs.primPath() == db.stringToToken("") || db.inputs.points.size() == 0)
        {
            return false;
        }

        bool reload = false;
        if (internalState.resourcePointer == nullptr || internalState.primPath != db.inputs.primPath() ||
            internalState.pointCount != db.inputs.points.size() || !internalState.previousSuccess)
        {
            reload = true;
        }

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
            std::cout << "OgnDeformedPointsToHydra::compute -- cudaStream: " << stream << std::endl;
        }


        if (resourceManager == nullptr || resourceManagerContext == nullptr)
        {
            return false;
        }

        const uint32_t deviceIndex = 0;
        const size_t pointsCount = db.inputs.points.size();

        const uint64_t dimension = 3;
        const uint64_t size = pointsCount * dimension * sizeof(float);

        if (reload)
        {
            if (internalState.resourcePointer != nullptr)
            {
                if (verbose)
                {
                    std::cout << "freeing RpResource." << std::endl;
                }

                resourceManager->releaseResource(*internalState.resourcePointer);
                internalState.resourcePointer = nullptr;
            }

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

            internalState.resourcePointer =
                resourceManager->getResourceFromBufferDesc(*resourceManagerContext, bufferDesc, resourceDesc);
            internalState.pointCount = pointsCount;
            internalState.primPath = db.inputs.primPath();
        }

        const float3* cudaSrc = (const float3*)(*db.inputs.points.gpu());
        void* cudaDst = resourceManager->getCudaDevicePointer(*internalState.resourcePointer, deviceIndex);

        cudaMemcpy(cudaDst, (const void*)cudaSrc, size, cudaMemcpyDeviceToDevice);

        if (db.inputs.sendToHydra())
        {
            omni::usd::hydra::IOmniHydra* omniHydra =
                carb::getFramework()->acquireInterface<omni::usd::hydra::IOmniHydra>();

            omni::usd::hydra::BufferDesc desc;
            desc.data = (void*)internalState.resourcePointer;
            desc.elementSize = dimension * sizeof(float);
            desc.elementStride = dimension * sizeof(float);
            desc.count = pointsCount;
            desc.isGPUBuffer = true;
            desc.isDataRpResource = true;

            pxr::SdfPath path = pxr::SdfPath(db.tokenToString(internalState.primPath));

            CARB_PROFILE_ZONE(1, "OgnRpResourceToHydra_Arrays, sending to hydra");
            omniHydra->SetPointsBuffer(pxr::SdfPath(db.tokenToString(internalState.primPath)), desc);
        }

        internalState.previousSuccess = previousSuccess;
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
}
