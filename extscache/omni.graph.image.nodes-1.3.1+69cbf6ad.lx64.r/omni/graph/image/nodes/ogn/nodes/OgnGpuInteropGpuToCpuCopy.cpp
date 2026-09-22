// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnGpuInteropGpuToCpuCopyDatabase.h"

#include <carb/graphics/GraphicsTypes.h>
#include <carb/logging/Log.h>

#include <cuda/include/cuda_runtime_api.h>

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/GpuInteropEntryUserData.h>

#include <rtx/hydra/CommonAovTokens.h>
#include <rtx/hydra/HydraRenderResults.h>
#include <rtx/resourcemanager/ResourceManager.h>
#include <rtx/rendergraph/RenderGraphBuilder.h>
#include <rtx/rendergraph/RenderGraphTypes.h>

#include <gpu/rendergraph/IRenderGraph.h>

#include <atomic>
#include <memory>
#include <string>
#include <vector>

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

class OgnGpuInteropGpuToCpuCopy
{
public:
    /**
     * @brief An HydraRVRawResource supporting pinned memory.
     */
    class PinnedHydraRVRawResource final : public usd::hydra::HydraRVRawResource
    {
        bool m_pinned;

        explicit PinnedHydraRVRawResource(const PinnedHydraRVRawResource* src)
        : usd::hydra::HydraRVRawResource(dynamic_cast<const usd::hydra::HydraRVRawResource*>(src)),
            m_pinned(src->m_pinned)
        {
        }

    public:
        explicit PinnedHydraRVRawResource(size_t size, int cudaDeviceIndex, bool tryPinned=true)
        : usd::hydra::HydraRVRawResource(nullptr, 0), m_pinned(false)
        {
            if (tryPinned)
            {
                m_buffer = allocatePinnedMemory(
                    carb::getCachedInterface<carb::cudainterop::CudaInterop>(), size, cudaDeviceIndex);
                m_pinned = m_buffer != nullptr;
            }
            if (!m_pinned)
            {
                m_buffer = CARB_MALLOC(size);
            }
            if (m_buffer)
            {
                m_size = size;
                m_referenceCount = new std::atomic_int(1);
            }
        }
        virtual ~PinnedHydraRVRawResource()
        {
            if (m_referenceCount && (m_referenceCount->fetch_sub(1) == 1))
            {
                delete m_referenceCount;
                if (m_pinned)
                {
                    carb::getCachedInterface<carb::cudainterop::CudaInterop>()->freeHostMemory(m_buffer);
                }
                else
                {
                    CARB_FREE(m_buffer);
                }
            }
            // prevent the base class unref
            m_referenceCount = nullptr;
        }

        HydraRVRawResource* acquire() const override
        {
            return new PinnedHydraRVRawResource(this);
        }

        bool isLocked() const
        {
            return *m_referenceCount > 1;
        }

    private:
        // Allocate a cuda pinned memory host buffer of the given size for the given device.
        // Returns pointer on the allocated memory (nullptr on failure)
        static inline void* allocatePinnedMemory(carb::cudainterop::CudaInterop* cudaInteropPtr,
                                                size_t size,
                                                int cudaDeviceIndex)
        {
            int cudaCurrDeviceIndex = 0;
            cudaInteropPtr->getDevice(&cudaCurrDeviceIndex);
            const bool switchDevice = cudaCurrDeviceIndex != cudaDeviceIndex;
            if (switchDevice)
            {
                cudaInteropPtr->setDevice(cudaDeviceIndex);
            }
            void* pinnedMemory;
            auto status = cudaInteropPtr->allocateHostMemory(&pinnedMemory, size,
                                                             cudaHostAllocDefault, "OgnGpuInteropGpuToCpuCopy");
            if (status != cudaSuccess)
            {
                pinnedMemory = nullptr;
            }
            if (switchDevice)
            {
                cudaInteropPtr->setDevice(cudaCurrDeviceIndex);
            }
            return pinnedMemory;
        }
    };
    std::vector<std::unique_ptr<PinnedHydraRVRawResource>> m_cachedResources;

    usd::hydra::HydraRVRawResource* getHostResource(size_t size, int cudaDeviceIndex)
    {
        bool invalidCacheSize = false;
        for (const auto& res : m_cachedResources)
        {
            if (res->isLocked())
            {
                continue;
            }
            if (res->size() == size)
            {
                return res->acquire();
            }
            else
            {
                invalidCacheSize = true;
                break;
            }
        }
        if (invalidCacheSize)
        {
            m_cachedResources.clear();
        }
        m_cachedResources.push_back(std::make_unique<PinnedHydraRVRawResource>(size, cudaDeviceIndex));
        return m_cachedResources.back()->acquire();
    }

    static bool compute(OgnGpuInteropGpuToCpuCopyDatabase& db)
    {
        auto iToken = carb::getCachedInterface<omni::usd::ITokenAbi>();
        omni::graph::core::GpuFoundationsInterfaces* gpu = (GpuFoundationsInterfaces*)db.inputs.gpu();
        omni::usd::hydra::HydraRenderProduct* rp = (omni::usd::hydra::HydraRenderProduct*)db.inputs.rp();

        if (!gpu || !rp || !iToken)
            return false;

        std::string aovGpuStr = db.inputs.aovGpu();
        if (aovGpuStr.empty())
        {
            return false;
        }

        auto srcAovH = iToken->getPermanentHandle(aovGpuStr.c_str());
        auto srcRenderVar = omni::usd::hydra::getRenderVarFromProduct(rp, srcAovH);

        if (!(srcRenderVar && srcRenderVar->resource))
        {
            CARB_LOG_WARN_ONCE("OgnGpuInteropGpuToCpuCopy missing source aov %s", aovGpuStr.c_str());
            return false;
        }

        if (!srcRenderVar->isRpResource)
        {
            CARB_LOG_WARN_ONCE("OgnGpuInteropGpuToCpuCopy supports RpResources only");
            return false;
        }

        carb::graphics::Graphics* graphics = (carb::graphics::Graphics*)gpu->graphics;
        carb::graphics::DeviceGroup* deviceGroup = (carb::graphics::DeviceGroup*)gpu->deviceGroup;
        gpu::rendergraph::IRenderGraph* iRenderGraph = (gpu::rendergraph::IRenderGraph*)gpu->renderGraph;
        rtx::resourcemanager::Context* rmCtx = (rtx::resourcemanager::Context*)gpu->resourceManagerContext;
        rtx::resourcemanager::ResourceManager* rm = (rtx::resourcemanager::ResourceManager*)gpu->resourceManager;
        rtx::rendergraph::RenderGraphBuilder* rgBuilder = (rtx::rendergraph::RenderGraphBuilder*)gpu->renderGraphBuilder;

        uint32_t deviceIndex = rm->getFirstDeviceIndex(*rmCtx, *srcRenderVar->resource);
        rtx::rendergraph::RenderGraph* renderGraph = iRenderGraph->getRenderGraph(deviceIndex);
        const carb::graphics::DeviceCaps& deviceCaps = graphics->getDeviceCaps(deviceGroup->getDevice(deviceIndex));

        auto appendAovToProduct = [](omni::usd::hydra::HydraRenderProduct* rp, omni::usd::TokenH aov,
                                    usd::hydra::HydraRVRawResource* rawResource)
        {
            using namespace omni::usd::hydra;

            HydraRenderVar* newVars = new HydraRenderVar[rp->renderVarCnt + 1];
            size_t varArraySize = sizeof(HydraRenderVar) * rp->renderVarCnt;
            memcpy(newVars, rp->vars, varArraySize);
            newVars[rp->renderVarCnt].aov = aov;
            newVars[rp->renderVarCnt].isRpResource = false;
            newVars[rp->renderVarCnt].rawResource =  rawResource;
            newVars[rp->renderVarCnt].isBufferRpResource = false;

            delete[] rp->vars;
            rp->vars = newVars;
            rp->renderVarCnt++;
        };

        if(srcRenderVar->isBufferRpResource)
        {
            void* hostBuffer = nullptr;
            std::string aovCpuStr = aovGpuStr + "_Host";
            omni::usd::TokenH newAov = 0;
            {
                newAov = iToken->getPermanentHandle(aovCpuStr.c_str());

                carb::cudainterop::CudaInterop* cudaInterop = carb::getCachedInterface<carb::cudainterop::CudaInterop>();
                int cudaDeviceIndex = cudaInterop->queryDevice(graphics, deviceGroup->getDevice(deviceIndex));

                usd::hydra::HydraRVRawResource* rawResource = nullptr;
                const uint32_t resDeviceIndex = rm->getFirstDeviceIndex(*rmCtx, *srcRenderVar->resource);
                const size_t hostResourceSize = rm->getResourceMemorySize(*srcRenderVar->resource, resDeviceIndex);
                rawResource = db.sharedState<OgnGpuInteropGpuToCpuCopy>().getHostResource(hostResourceSize, cudaDeviceIndex);

                if (rawResource)
                {
                    appendAovToProduct(rp, newAov, rawResource);
                    // After realloc in appendAovToProduct, srcRenderVar is invalid
                    srcRenderVar = omni::usd::hydra::getRenderVarFromProduct(rp, srcAovH);
                    hostBuffer = rawResource->data();
                }
            }

            // Use CudaAsync call to copy buffer (in order to prevent CPU waiting for GPU, make sure you use pinned host memory).
            using namespace carb::graphics;
            rtx::rendergraph::ParamBlockRefs paramBlockRefs{ 0, {} };
            rtx::rendergraph::RenderOpParams* renderOpParams = rgBuilder->createParams(*renderGraph, paramBlockRefs);

            struct RenderOpCudaCopyParams
            {
                size_t size;
                void* hostPtr;
                void* devicePtr;
                carb::cudainterop::CudaInterop* cudaInterop;
            };

            rtx::resourcemanager::RpResource* srcResource = srcRenderVar->resource;
            rtx::rendergraph::addRenderOpLambdaEx(
                // Setting kRenderOpFlagNoAnnotation to minimize API Transitions for just adding annotations
                *rgBuilder, *renderGraph, "OG Copy Gpu to Cpu", renderOpParams,
                rtx::rendergraph::kRenderOpFlagNoAnnotation,
                [rgBuilder, hostBuffer, rm, rmCtx, srcResource, deviceIndex](rtx::rendergraph::RenderOpInputCp renderOpInput)
                {
                    auto callbackParams = new RenderOpCudaCopyParams();
                    callbackParams->hostPtr = hostBuffer;
                    callbackParams->size = rm->getResourceMemorySize(*srcResource, deviceIndex);
                    callbackParams->devicePtr = rm->getCudaDevicePointer(*srcResource, deviceIndex);
                    callbackParams->cudaInterop = carb::getCachedInterface<carb::cudainterop::CudaInterop>();
                    

                    renderOpInput->graphicsMux->cmdCudaInterop(
                        renderOpInput->commandList,
                        [](cudaStream_t cudaStream, void* userData)
                        {
                            CARB_PROFILE_ZONE(1, "memcpyAsync");
                            RenderOpCudaCopyParams* params = static_cast<RenderOpCudaCopyParams*>(userData);
                            // params->cudaInterop->setDevice(params->cudaDeviceIndex)
                            params->cudaInterop->memcpyAsync(
                                params->hostPtr, params->devicePtr, params->size, cudaStream);
                            delete params;
                        },
                        callbackParams, carb::graphicsmux::CudaInteropFlags::eNone);
                });
            db.outputs.rp() = (uint64_t)rp;
            db.outputs.gpu() = (uint64_t)gpu;
            db.outputs.aovCpu() = aovCpuStr;

            return true;
        }
        else
        {
            auto rgResource = rgBuilder->registerExternalTexture(*renderGraph, *srcRenderVar->resource);
            carb::graphics::TextureDesc texDesc = rgBuilder->getResourceTextureDesc(*rgResource);

            auto w = texDesc.width;
            auto h = texDesc.height;
            auto allocRpSharedBuffer = [rm, rmCtx, rgBuilder, renderGraph, w, h, deviceCaps, deviceIndex](
                                        carb::Format format, uint32_t& outRowSize, const char* debugName)
            {
                using namespace carb::graphics;
                size_t bpp = carb::graphics::getLookupTexelFormat(format)->formatSize;
                outRowSize = (uint32_t)CARB_ALIGNED_SIZE(w * bpp, deviceCaps.optimalBufferCopyRowPitchAlignment);
                size_t sharedBuffSize = CARB_ALIGNED_SIZE(outRowSize * h, deviceCaps.uploadBufferTextureRowAlignment);

                BufferDesc buffDesc = {};
                buffDesc.size = sharedBuffSize;
                buffDesc.usageFlags = carb::graphics::kBufferUsageFlagExportShared;
                buffDesc.debugName = debugName;

                rtx::resourcemanager::ResourceDesc resourceDesc = {};
                resourceDesc.mode = rtx::resourcemanager::ResourceMode::eDefault;
                resourceDesc.memoryLocation = MemoryLocation::eDevice;
                resourceDesc.category = rtx::resourcemanager::ResourceCategory::eOtherBuffer;
                resourceDesc.usageFlags = rtx::resourcemanager::kResourceUsageFlagCudaShared;
                resourceDesc.deviceMask = carb::graphics::DeviceMask::getDeviceMaskFromIndex(deviceIndex);
                resourceDesc.syncScopeId = rgBuilder->getRenderGraphDesc(*renderGraph).syncScopeId;

                return rm->getResourceFromBufferDesc(*rmCtx, buffDesc, resourceDesc);
            };

            // Allocate a staging buffer to copy texture into
            uint32_t rowSize;
            rtx::resourcemanager::RpResource* stagingBuffer = nullptr;
            stagingBuffer = allocRpSharedBuffer(texDesc.format, rowSize, "OgnGpuInteropGpuToCpuCopy Staging Buffer");
            if (!stagingBuffer)
            {
                CARB_LOG_WARN_ONCE("OgnGpuInteropGpuToCpuCopy cannot allocate staging buffer");
                return false;
            }

            // Create new AOV and allocate a CPU buffer that will receive contents of staging buffer
            void* hostBuffer = nullptr;
            std::string aovCpuStr = aovGpuStr + "_Host";
            omni::usd::TokenH newAov = 0;
            {
                newAov = iToken->getPermanentHandle(aovCpuStr.c_str());

                carb::cudainterop::CudaInterop* cudaInterop = carb::getCachedInterface<carb::cudainterop::CudaInterop>();
                int cudaDeviceIndex = cudaInterop->queryDevice(graphics, deviceGroup->getDevice(deviceIndex));

                //std::unique_ptr<PinnedHydraRVRawResource> rawResource;
                usd::hydra::HydraRVRawResource* rawResource = nullptr;
                if (stagingBuffer)
                {
                    const uint32_t resDeviceIndex = rm->getFirstDeviceIndex(*rmCtx, *stagingBuffer);
                    const size_t hostResourceSize = rm->getResourceMemorySize(*stagingBuffer, resDeviceIndex);
                    rawResource = db.sharedState<OgnGpuInteropGpuToCpuCopy>().getHostResource(hostResourceSize, cudaDeviceIndex);
                }

                if (rawResource)
                {
                    appendAovToProduct(rp, newAov, rawResource);
                    // After realloc in appendAovToProduct, srcRenderVar is invalid
                    srcRenderVar = omni::usd::hydra::getRenderVarFromProduct(rp, srcAovH);
                    hostBuffer = rawResource->data();
                }
            }

            // Use CudaAsync call to copy buffer (in order to prevent CPU waiting for GPU, make sure you use pinned host memory).
            {
                using namespace carb::graphics;
                rtx::rendergraph::ParamBlockRefs paramBlockRefs{ 0, {} };
                rtx::rendergraph::RenderOpParams* renderOpParams = rgBuilder->createParams(*renderGraph, paramBlockRefs);

                struct RenderOpCudaCopyParams
                {
                    size_t size;
                    void* hostPtr;
                    void* devicePtr;
                    carb::cudainterop::CudaInterop* cudaInterop;
                };

                rtx::resourcemanager::RpResource* srcResource = srcRenderVar->resource;
                rtx::rendergraph::addRenderOpLambdaEx(
                    // Setting kRenderOpFlagNoAnnotation to minimize API Transitions for just adding annotations
                    *rgBuilder, *renderGraph, "OG Copy Gpu to Cpu", renderOpParams,
                    rtx::rendergraph::kRenderOpFlagNoAnnotation,
                    [rgBuilder, hostBuffer, rm, rmCtx, srcResource, stagingBuffer, rowSize,
                    deviceIndex](rtx::rendergraph::RenderOpInputCp renderOpInput)
                    {
                        auto cmdListGfx =
                            renderOpInput->graphicsMux->getGraphicsCommandList(renderOpInput->commandList, nullptr);
                        carb::graphics::Buffer* sharedBuff = rm->getBufferFromResource(*stagingBuffer, deviceIndex);
                        rm->copyTextureToBuffer(*rmCtx, cmdListGfx, srcResource, sharedBuff, rowSize, deviceIndex);

                        auto callbackParams = new RenderOpCudaCopyParams();
                        callbackParams->hostPtr = hostBuffer;
                        callbackParams->size = rm->getResourceMemorySize(*stagingBuffer, deviceIndex);
                        callbackParams->devicePtr = rm->getCudaDevicePointer(*stagingBuffer, deviceIndex);
                        callbackParams->cudaInterop = carb::getCachedInterface<carb::cudainterop::CudaInterop>();
                        renderOpInput->graphicsMux->cmdCudaInterop(
                            renderOpInput->commandList,
                            [](cudaStream_t cudaStream, void* userData)
                            {
                                CARB_PROFILE_ZONE(1, "memcpyAsync");
                                RenderOpCudaCopyParams* params = static_cast<RenderOpCudaCopyParams*>(userData);
                                // params->cudaInterop->setDevice(params->cudaDeviceIndex)
                                params->cudaInterop->memcpyAsync(
                                    params->hostPtr, params->devicePtr, params->size, cudaStream);
                                delete params;
                            },
                            callbackParams, carb::graphicsmux::CudaInteropFlags::eNone);

                        rm->releaseResource(*stagingBuffer);
                    });
            }
            db.outputs.rp() = (uint64_t)rp;
            db.outputs.gpu() = (uint64_t)gpu;
            db.outputs.aovCpu() = aovCpuStr;

            return true;
         }
    }
};

REGISTER_OGN_NODE()

}
}
}
}
