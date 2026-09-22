// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "OgnGpuInteropCpuToDiskDatabase.h"

#include <carb/extras/Path.h>
#include <carb/filesystem/IFileSystem.h>
#include <carb/graphics/GraphicsTypes.h>
#include <carb/imaging/IImaging.h>
#include <carb/logging/Log.h>
#include <carb/tasking/TaskingUtils.h>

#include <cuda/include/cuda_runtime_api.h>

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/GpuInteropEntryUserData.h>

#include <rtx/hydra/CommonAovTokens.h>
#include <rtx/hydra/HydraRenderResults.h>
#include <rtx/rendergraph/RenderGraphBuilder.h>
#include <rtx/rendergraph/RenderGraphTypes.h>
#include <rtx/resourcemanager/ResourceManager.h>

#include <gpu/rendergraph/IRenderGraph.h>

#include <string>

#if !CARB_PLATFORM_WINDOWS
#    define sprintf_s snprintf
#endif

namespace omni
{
namespace graph
{
namespace core
{
namespace examples
{

struct RenderOpCudaCallbackParams
{
    size_t size;
    uint8_t bpp;
    omni::usd::hydra::HydraRVRawResource* rawResource;
    uint32_t width;
    uint32_t height;
    uint32_t rowSize;
    carb::Format format;
    std::string saveLocation;
    uint64_t fileSaveFlags;
    carb::tasking::TaskGroup *tasks;
    carb::imaging::IImaging* imaging;
    carb::tasking::Semaphore* semaphore;
};

void cudaCpuToDiskCallback(cudaStream_t stream, cudaError_t status, void *userData)
{
    // Is this a race condition, will timeline semaphore for cmdlist
    // complete before cudaCpuToDiskCallback() finishes?
    if (userData != nullptr)
    {
        RenderOpCudaCallbackParams* params = (RenderOpCudaCallbackParams*)userData;

        omni::usd::hydra::HydraRVRawResource* acquiredRawResource = params->rawResource->acquire();

        auto w = params->width;
        auto h = params->height;
        auto format = params->format;
        auto rowSize = params->rowSize;
        auto imaging = params->imaging;
        std::string fullPath = params->saveLocation;
        uint64_t fileSaveFlags = params->fileSaveFlags;
        auto saveImageFn = [imaging, acquiredRawResource, w, h, format, rowSize, fullPath, fileSaveFlags](){
            bool success = imaging->saveToFile(acquiredRawResource->data(), w, h, rowSize, format, fullPath.c_str(), fileSaveFlags);
            if (!success)
            {
                const char* error = imaging->getErrorMessage();
                CARB_LOG_ERROR("Failed to save file %s: %s", fullPath.c_str(), error);
            }
            delete acquiredRawResource;
        };

        carb::getCachedInterface<carb::tasking::ITasking>()->addThrottledTask(params->semaphore,
            carb::tasking::Priority::eLow, params->tasks, saveImageFn);

        delete params;
    }
}

struct CpuToDiskUserData
{
    int64_t captureCount;
    carb::tasking::TaskGroup tasks;
    carb::tasking::Semaphore* semaphore;
};

class OgnGpuInteropCpuToDisk
{
public:
    static bool compute(OgnGpuInteropCpuToDiskDatabase& db)
    {
        auto iToken = carb::getCachedInterface<omni::usd::ITokenAbi>();
        omni::graph::core::GpuFoundationsInterfaces* gpu = (GpuFoundationsInterfaces*)db.inputs.gpu();
        omni::usd::hydra::HydraRenderProduct* rp = (omni::usd::hydra::HydraRenderProduct*)db.inputs.rp();

        if (!gpu || !rp || !iToken)
            return false;

        const INode* const iNode = db.abi_node().iNode;
        const IGraphContext* const iContext = db.abi_context().iContext;

        auto userData = db.userData<CpuToDiskUserData>();
        if (!userData)
            return false;

        auto activeValueAttr = omni::graph::core::getAttributeW(db.abi_context(), db.abi_node().nodeContextHandle, Token("inputs:active"), db.getInstanceIndex());
        bool* activeValue = getDataW<bool>(db.abi_context(), activeValueAttr);

        const bool skipInactiveNodes = db.inputs.skipInactive();

        if (activeValue && *activeValue)
        {
            *activeValue = false;
        }
        else
        {
            if (activeValue && skipInactiveNodes)
            {
                // This early out is used during DL-Denoiser training in scripts.
                // Ground Truth accumulation might lead to RenderProducts here that are
                // no longer in memory.
                // To avoid the below 'rp->frameNumber' access, this 'inputs:skipInactive'
                // attribute has been introduced (OMPE-29178).
                return false;
            }

            size_t frameStart = db.inputs.startFrame();
            if (rp->frameNumber < frameStart)
                return false;

            int64_t frameCount = db.inputs.frameCount();
            if (frameCount != -1 && userData->captureCount >= frameCount)
                return false;
        }

        std::string aovCpuStr = db.inputs.aovCpu();
        if (aovCpuStr.empty())
            return false;

        std::string aovGpuStr = db.inputs.aovGpu();
        if (aovGpuStr.empty())
            return false;

        std::string saveLocation = db.inputs.saveLocation();
        if (saveLocation.empty())
            return false;

        carb::filesystem::IFileSystem* fs = carb::getCachedInterface<carb::filesystem::IFileSystem>();
        if (fs && !fs->exists(saveLocation.c_str()))
            fs->makeDirectories(saveLocation.c_str());

        std::string fileType = db.inputs.fileType();
        if (fileType.empty())
            return false;

        const uint64_t fileSaveFlags = db.inputs.saveFlags();

        if (!userData->semaphore)
        {
            auto inFlightWrites = db.inputs.maxInflightWrites();
            userData->semaphore = carb::getCachedInterface<carb::tasking::ITasking>()->createSemaphore(inFlightWrites);
        }

        std::string inputFileNameStem, inputFileName = db.inputs.fileName();

        if (!inputFileName.empty())
        {
            inputFileNameStem = carb::extras::Path(inputFileName).getStem();
        }

        std::string filename;
        if (!inputFileNameStem.empty())
        {
            filename = inputFileNameStem + "_" + aovGpuStr + "." + fileType;
        }
        else
        {
            const int autoFileNumber = db.inputs.autoFileNumber();
            const int fileNumber = db.inputs.fileNumber();

            if (autoFileNumber >= 0)
            {
                char numBuffer[256];
                sprintf_s(numBuffer, CARB_COUNTOF(numBuffer), "%06d", int(autoFileNumber + userData->captureCount));
                filename = aovGpuStr + "_" + std::string(numBuffer) + "." + fileType;
            }
            else if (fileNumber >= 0)
            {
                char numBuffer[256];
                sprintf_s(numBuffer, CARB_COUNTOF(numBuffer), "%06d", fileNumber);
                filename = aovGpuStr + "_" + std::string(numBuffer) + "." + fileType;
            }
            else
            {
                filename = aovGpuStr + "_" + std::to_string(rp->frameNumber) + "." + fileType;
            }
        }

        carb::extras::Path folder(saveLocation);
        carb::extras::Path fullPath = folder.join(filename);

        auto srcAovRsrcH = iToken->getPermanentHandle(aovGpuStr.c_str());
        auto srcRenderVarRsrc = omni::usd::hydra::getRenderVarFromProduct(rp, srcAovRsrcH);

        if (!(srcRenderVarRsrc && srcRenderVarRsrc->resource))
        {
            CARB_LOG_WARN_ONCE("OgnGpuInteropCpuToDisk missing source resource aov %s", aovGpuStr.c_str());
            return false;
        }

        auto srcAovBufferH = iToken->getPermanentHandle(aovCpuStr.c_str());
        auto srcRenderVarBuffer = omni::usd::hydra::getRenderVarFromProduct(rp, srcAovBufferH);

        if (!(srcRenderVarBuffer && srcRenderVarBuffer->rawResource && srcRenderVarBuffer->rawResource->data()))
        {
            CARB_LOG_WARN_ONCE("OgnGpuInteropCpuToDisk missing source buffer aov %s", aovCpuStr.c_str());
            return false;
        }

        if (srcRenderVarBuffer->isRpResource)
        {
            CARB_LOG_WARN_ONCE("OgnGpuInteropGpuToCpuCopy malformed input buffer");
            return false;
        }

        carb::graphics::Graphics* graphics = (carb::graphics::Graphics*)gpu->graphics;
        carb::graphics::DeviceGroup* deviceGroup = (carb::graphics::DeviceGroup*)gpu->deviceGroup;
        gpu::rendergraph::IRenderGraph* iRenderGraph = (gpu::rendergraph::IRenderGraph*)gpu->renderGraph;
        rtx::resourcemanager::Context* rmCtx = (rtx::resourcemanager::Context*)gpu->resourceManagerContext;
        rtx::resourcemanager::ResourceManager* rm = (rtx::resourcemanager::ResourceManager*)gpu->resourceManager;
        rtx::rendergraph::RenderGraphBuilder* rgBuilder = (rtx::rendergraph::RenderGraphBuilder*)gpu->renderGraphBuilder;

        uint32_t deviceIndex = rm->getFirstDeviceIndex(*rmCtx, *srcRenderVarRsrc->resource);
        rtx::rendergraph::RenderGraph* renderGraph = iRenderGraph->getRenderGraph(deviceIndex);

        const carb::graphics::DeviceCaps& deviceCaps = graphics->getDeviceCaps(deviceGroup->getDevice(deviceIndex));

        auto rgResource = rgBuilder->registerExternalTexture(*renderGraph, *srcRenderVarRsrc->resource);
        carb::graphics::TextureDesc texDesc = rgBuilder->getResourceTextureDesc(*rgResource);

        // Use CudaAsync call to copy buffer. Is this really the best approach for readback
        {
            using namespace carb::graphics;
            rtx::rendergraph::ParamBlockRefs paramBlockRefs{ 0, {} };
            rtx::rendergraph::RenderOpParams* renderOpParams = rgBuilder->createParams(*renderGraph, paramBlockRefs);

            // carb::imaging::saveToFile supports multiple file formats, so we will not validate texDesc.format here
            // Arguably, it would be nice to return false for any format that carb::imaging::saveToFile does not support

            uint8_t bpp = carb::graphics::getLookupTexelFormat(texDesc.format)->formatSize;
            uint32_t rowSize = (uint32_t)CARB_ALIGNED_SIZE(texDesc.width * bpp, deviceCaps.optimalBufferCopyRowPitchAlignment);
            size_t bufferSize = CARB_ALIGNED_SIZE(rowSize * texDesc.height, deviceCaps.uploadBufferTextureRowAlignment);

            auto size = bufferSize;
            auto width = texDesc.width;
            auto height = texDesc.height;
            auto format = texDesc.format;
            auto *tasks = &userData->tasks;
            auto semaphore = userData->semaphore;
            omni::usd::hydra::HydraRVRawResource* srcResource = srcRenderVarBuffer->rawResource;
            carb::imaging::IImaging* imaging = carb::getCachedInterface<carb::imaging::IImaging>();

            rtx::rendergraph::addRenderOpLambdaEx(
                // Setting kRenderOpFlagNoAnnotation to minimize API Transitions for just adding annotations
                *rgBuilder, *renderGraph, "OG Copy Gpu to Cpu", renderOpParams,
                rtx::rendergraph::kRenderOpFlagNoAnnotation,
                [srcResource, size, bpp, width, height, format, rowSize, imaging, semaphore, tasks, fullPath,
                 fileSaveFlags](rtx::rendergraph::RenderOpInputCp renderOpInput) {

                    auto callbackParams = new RenderOpCudaCallbackParams();
                    callbackParams->bpp = bpp;
                    callbackParams->size = size;
                    callbackParams->tasks = tasks;
                    callbackParams->width = width;
                    callbackParams->height = height;
                    callbackParams->rowSize = rowSize;
                    callbackParams->imaging = imaging;
                    callbackParams->rawResource = srcResource;
                    callbackParams->semaphore = semaphore;
                    callbackParams->format = (carb::Format)format;
                    callbackParams->saveLocation = fullPath.getString();
                    callbackParams->fileSaveFlags = fileSaveFlags;

                    renderOpInput->graphicsMux->cmdCudaInterop(
                        renderOpInput->commandList,
                        [](cudaStream_t cudaStream, void* userData) {
                            RenderOpCudaCallbackParams* params = static_cast<RenderOpCudaCallbackParams*>(userData);
                            cudaStreamAddCallback(cudaStream, cudaCpuToDiskCallback, params, 0);
                        },
                        callbackParams,
                        carb::graphicsmux::CudaInteropFlags::eNone);
                }
            );
        }

        db.outputs.rp() = (uint64_t)rp;
        db.outputs.gpu() = (uint64_t)gpu;

        userData->captureCount++;

        return true;
    }

    static void initialize(const GraphContextObj& context, const NodeObj& node)
    {
        const INode* const iNode = node.iNode;
        if (!iNode)
            return;

        CpuToDiskUserData* userData = new CpuToDiskUserData();
        userData->captureCount = 0;
        userData->semaphore = nullptr;
        iNode->setUserData(node, userData);
    }

    static void release(const NodeObj& data)
    {
        const INode* const iNode = data.iNode;
        if (!iNode)
            return;

        CpuToDiskUserData* userData = (CpuToDiskUserData*)iNode->getUserData(data);
        if (userData)
        {
            userData->tasks.wait();
            if (userData->semaphore)
            {
                carb::getCachedInterface<carb::tasking::ITasking>()->destroySemaphore(userData->semaphore);
            }
            delete userData;
            userData = nullptr;
        }
    }

};

REGISTER_OGN_NODE()

}
}
}
}
