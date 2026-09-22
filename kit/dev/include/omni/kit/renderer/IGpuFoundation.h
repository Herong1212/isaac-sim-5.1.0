// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>

namespace carb
{
namespace graphics
{
struct Graphics;
}
namespace graphicsmux
{
struct GraphicsMux;
}
namespace glinterop
{
struct GLInterop;
}
namespace cudainterop
{
struct CudaInterop;
}
}

namespace rtx
{
namespace resourcemanager
{
struct ResourceManager;
class Context;
typedef uint32_t SyncScopeId;
}
namespace rendergraph
{
struct RenderGraphBuilder;
class RenderGraphContext;
}
namespace shaderdb
{
struct ShaderDb;
class Context;
}
namespace psodb
{
struct PsoDb;
struct Context;
}
}

namespace gpu
{
namespace foundation
{
class IGpuFoundation;
struct GpuFoundationContext;
struct GpuDevices;
}
}

namespace omni
{
namespace kit
{
namespace renderer
{

class IGpuFoundation
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::renderer::IGpuFoundation", 1, 1);

    virtual carb::graphics::Graphics* getGraphics() = 0;
    virtual carb::graphicsmux::GraphicsMux* getGraphicsMux() = 0;

    virtual rtx::resourcemanager::ResourceManager* getResourceManager() = 0;
    virtual rtx::resourcemanager::Context* getResourceManagerContext() = 0;

    virtual rtx::rendergraph::RenderGraphBuilder* getRenderGraphBuilder() = 0;

    virtual rtx::shaderdb::ShaderDb* getShaderDb() = 0;
    virtual rtx::shaderdb::Context* getShaderDbContext() = 0;

    virtual rtx::psodb::PsoDb* getPipelineStateDb() = 0;
    virtual rtx::psodb::Context* getPipelineStateDbContext() = 0;

    virtual carb::glinterop::GLInterop* getOpenGlInterop() = 0;
    virtual carb::cudainterop::CudaInterop* getCudaInterop() = 0;

    virtual gpu::foundation::IGpuFoundation* getGpuFoundation() = 0;
    virtual gpu::foundation::GpuDevices* getGpuFoundationDevices() = 0;

    virtual bool isBindlessSupported() = 0;

    virtual rtx::resourcemanager::SyncScopeId getSyncScopeId() = 0;

    virtual bool isCompatibilityMode() = 0;
};

}
}
}
