// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <omni/hydra/IOmniHydra.h>
#include <omni/usd/UsdContextIncludes.h>
#include <omni/usd/UsdContext.h>

#include <carb/graphics/GraphicsTypes.h>
#include <carb/logging/Log.h>

#include <cuda/include/cuda_runtime_api.h>

#include <omni/graph/core/NodeTypeRegistrar.h>
#include <omni/graph/core/iComputeGraph.h>

#include <rtx/utils/GraphicsDescUtils.h>
#include <rtx/resourcemanager/ResourceManager.h>

#include <omni/kit/KitUtils.h>
#include <omni/kit/renderer/IRenderer.h>
#include <gpu/foundation/FoundationTypes.h>

#include <omni/math/linalg/vec.h>

#include "OgnRpResourceExampleHydraDatabase.h"

using omni::math::linalg::vec3f;

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

class OgnRpResourceExampleHydra
{
public:
    static bool compute(OgnRpResourceExampleHydraDatabase& db)
    {
        CARB_PROFILE_ZONE(1, "OgnRpResourceExampleHydra::compute");
        const bool sendToHydra = db.inputs.sendToHydra();
        const bool verbose = db.inputs.verbose();
        // const size_t dimension = 4;
        const size_t dimension = 3;
        const uint32_t deviceIndex = 0;

        rtx::resourcemanager::Context* resourceManagerContext = nullptr;
        rtx::resourcemanager::ResourceManager* resourceManager = nullptr;
        if (verbose)
        {
            if (auto renderer = carb::getCachedInterface<omni::kit::renderer::IRenderer>())
            {
                if (auto gpuFoundation = renderer->getGpuFoundation())
                {
                    resourceManager = gpuFoundation->getResourceManager();
                    resourceManagerContext = gpuFoundation->getResourceManagerContext();
                }
            }

            if (resourceManager == nullptr || resourceManagerContext == nullptr)
            {
                return false;
            }
        }

        auto& resourcePointerCollection = db.inputs.resourcePointerCollection();
        auto& pointCountCollection = db.inputs.pointCountCollection();
        auto& primPathCollection = db.inputs.primPathCollection();
        const size_t primCount = primPathCollection.size();

        if (primCount == 0 || pointCountCollection.size() != primPathCollection.size() ||
            2 * pointCountCollection.size() != resourcePointerCollection.size())
        {
            return false;
        }

        rtx::resourcemanager::RpResource** rpResources =
            (rtx::resourcemanager::RpResource**)resourcePointerCollection.data();
        const uint64_t* pointCounts = pointCountCollection.data();
        const NameToken* primPaths = primPathCollection.data();

        omni::usd::hydra::IOmniHydra* omniHydra =
            sendToHydra ? carb::getFramework()->acquireInterface<omni::usd::hydra::IOmniHydra>() : nullptr;

        for (size_t primIndex = 0; primIndex < primCount; primIndex++)
        {
            rtx::resourcemanager::RpResource* rpResource = rpResources[2 * primIndex + 1]; // only want deformed
                                                                                           // positions
            const uint64_t& pointsCount = pointCounts[primIndex];
            const NameToken& primPath = primPaths[primIndex];

            if (verbose)
            {
                carb::graphics::AccessFlags accessFlags =
                    resourceManager->getResourceAccessFlags(*rpResource, deviceIndex);
                std::cout << "Sending to Hydra..." << std::endl;
                std::cout << "prim path: " << db.tokenToString(primPath) << std::endl;
                std::cout << "\trpResource: " << rpResource << std::endl;
                std::cout << "\taccessFlags: " << accessFlags << std::endl;

                if (accessFlags & carb::graphics::kAccessFlagUnknown)
                    std::cout << "\t\tkAccessFlagUnknown" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagVertexBuffer)
                    std::cout << "\t\tkAccessFlagVertexBuffer" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagIndexBuffer)
                    std::cout << "\t\tkAccessFlagIndexBuffer" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagConstantBuffer)
                    std::cout << "\t\tkAccessFlagConstantBuffer" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagArgumentBuffer)
                    std::cout << "\t\tkAccessFlagArgumentBuffer" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagTextureRead)
                    std::cout << "\t\tkAccessFlagTextureRead" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagStorageRead)
                    std::cout << "\t\tkAccessFlagStorageRead" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagStorageWrite)
                    std::cout << "\t\tkAccessFlagStorageWrite" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagColorAttachmentWrite)
                    std::cout << "\t\tkAccessFlagColorAttachmentWrite" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagDepthStencilAttachmentWrite)
                    std::cout << "\t\tkAccessFlagDepthStencilAttachmentWrite" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagDepthStencilAttachmentRead)
                    std::cout << "\t\tkAccessFlagDepthStencilAttachmentRead" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagCopySource)
                    std::cout << "\t\tkAccessFlagCopySource" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagCopyDestination)
                    std::cout << "\t\tkAccessFlagCopyDestination" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagAccelStructRead)
                    std::cout << "\t\tkAccessFlagAccelStructRead" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagAccelStructWrite)
                    std::cout << "\t\tkAccessFlagAccelStructWrite" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagResolveSource)
                    std::cout << "\t\tkAccessFlagResolveSource" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagResolveDestination)
                    std::cout << "\t\tkAccessFlagResolveDestination" << std::endl;
                if (accessFlags & carb::graphics::kAccessFlagStorageClear)
                    std::cout << "\t\tkAccessFlagStorageClear" << std::endl;

                const carb::graphics::BufferDesc* bufferDesc = resourceManager->getBufferDesc(rpResource);
                std::cout << "\tbufferDesc: " << bufferDesc << std::endl;
                if (bufferDesc != nullptr)
                {
                    std::cout << "\tbuffer usage flags: " << bufferDesc->usageFlags << std::endl;

                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagNone)
                        std::cout << "\t\tkBufferUsageFlagNone" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagShaderResource)
                        std::cout << "\t\tkBufferUsageFlagShaderResource" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagShaderResourceStorage)
                        std::cout << "\t\tkBufferUsageFlagShaderResourceStorage" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagVertexBuffer)
                        std::cout << "\t\tkBufferUsageFlagVertexBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagIndexBuffer)
                        std::cout << "\t\tkBufferUsageFlagIndexBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagConstantBuffer)
                        std::cout << "\t\tkBufferUsageFlagConstantBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagRawOrStructuredBuffer)
                        std::cout << "\t\tkBufferUsageFlagRawOrStructuredBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagArgumentBuffer)
                        std::cout << "\t\tkBufferUsageFlagArgumentBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagRaytracingAccelStruct)
                        std::cout << "\t\tkBufferUsageFlagRaytracingAccelStruct" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagRaytracingBuffer)
                        std::cout << "\t\tkBufferUsageFlagRaytracingBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagRaytracingScratchBuffer)
                        std::cout << "\t\tkBufferUsageFlagRaytracingScratchBuffer" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagExportShared)
                        std::cout << "\t\tkBufferUsageFlagExportShared" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagImportShared)
                        std::cout << "\t\tkBufferUsageFlagImportShared" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagSharedCrossAdapter)
                        std::cout << "\t\tkBufferUsageFlagSharedCrossAdapter" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagHostMappedForeignMemory)
                        std::cout << "\t\tkBufferUsageFlagHostMappedForeignMemory" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagConcurrentAccess)
                        std::cout << "\t\tkBufferUsageFlagConcurrentAccess" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagVisibleCrossAdapter)
                        std::cout << "\t\tkBufferUsageFlagVisibleCrossAdapter" << std::endl;
                    if (bufferDesc->usageFlags & carb::graphics::kBufferUsageFlagRaytracingShaderBindingTable)
                        std::cout << "\t\tkBufferUsageFlagRaytracingShaderBindingTable" << std::endl;

                    std::cout << "\tbuffer size: " << bufferDesc->size << std::endl;
                    std::cout << "\tbuffer debug name: " << bufferDesc->debugName << std::endl;
                    std::cout << "\tbuffer ext: " << bufferDesc->ext << std::endl;
                }
            }

            if (sendToHydra)
            {
                omni::usd::hydra::BufferDesc desc;
                desc.data = (void*)rpResource;
                desc.elementSize = dimension * sizeof(float);
                desc.elementStride = dimension * sizeof(float);
                desc.count = pointsCount;
                desc.isGPUBuffer = true;
                desc.isDataRpResource = true;

                pxr::SdfPath path = pxr::SdfPath(db.tokenToString(primPath));

                CARB_PROFILE_ZONE(1, "OgnRpResourceExampleHydra, sending to hydra");
                omniHydra->SetPointsBuffer(pxr::SdfPath(db.tokenToString(primPath)), desc);
            }
        }
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
}
