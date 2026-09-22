// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <unordered_map>
#include <carb/graphics/GraphicsTypes.h>

namespace carb
{
namespace graphics
{
struct Graphics;
class DeviceGroup;
} // namespace graphics
namespace graphicsmux
{
struct GraphicsMux;
} // namespace graphicsmux
} // namespace carb
namespace rtx
{
namespace rendergraph
{
struct RenderGraphBuilder;
} // namespace rendergraph
namespace resourcemanager
{
struct ResourceManager;
class Context;
} // namespace resourcemanager
} // namespace rtx

namespace gpu
{
namespace rendergraph
{
OMNI_DECLARE_INTERFACE(IRenderGraph);
} // namespace rendergraph
} // namespace gpu

namespace omni
{

namespace usd
{
namespace hydra
{
    struct HydraRenderProduct;
} // namespace hydra
} // namespace usd

namespace graph
{
namespace core
{

struct GpuInteropCudaResourceData
{
    void* cudaResource;
    uint32_t width;
    uint32_t height;
    uint32_t depthOrArraySize;
    uint16_t mipCount;
    carb::graphics::Format format;
    bool isBuffer;
    uint32_t deviceIndex;
};

typedef std::unordered_map<std::string, GpuInteropCudaResourceData> GpuInteropCudaResourceMap;

struct GpuInteropCudaEntryUserData
{
    double simTime;
    int64_t rationalTimeOfSimNumerator;     //<< rational time required for fetching data from fabric
    uint64_t rationalTimeOfSimDenominator;
    double hydraTime;
    int64_t frameId;
    int64_t externalTimeOfSimFrame;
    GpuInteropCudaResourceMap cudaRsrcMap;
};

// Gpu Foundations initialization inside Kit remains a trainwreck, since unresolved
// we pass

struct GpuFoundationsInterfaces
{
    carb::graphics::Graphics* graphics;
    carb::graphicsmux::GraphicsMux* graphicsMux;
    carb::graphics::DeviceGroup* deviceGroup;
    rtx::rendergraph::RenderGraphBuilder* renderGraphBuilder;
    rtx::resourcemanager::ResourceManager* resourceManager;
    rtx::resourcemanager::Context* resourceManagerContext;
    gpu::rendergraph::IRenderGraph* renderGraph;
};

struct GpuInteropRpEntryUserData
{
    double simTime;
    double hydraTime;
    GpuFoundationsInterfaces* gpu;
    omni::usd::hydra::HydraRenderProduct* rp;
};

} // namespace core
} // namespace graph
} // namespace omni
