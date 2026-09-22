// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IPostRenderGraph.h
//!
//! @brief Defines @ref omni::graph::image::core::unstable::IPostRenderGraph_abi
#pragma once

#include <omni/graph/exec/unstable/IBase.h>
#include <omni/core/Omni.h>
#include <omni/kit/exec/core/unstable/IExecutionController.h>

namespace gpu
{
namespace rendergraph
{
//! Declare the IRenderGraph interface definition
OMNI_DECLARE_INTERFACE(IRenderGraph);
} // namespace rendergraph
enum class GfResult: int32_t;
} // namespace gpu

namespace omni
{

namespace usd
{
    using PathH = uint64_t;

    namespace hydra
    {
        struct ViewportHydraRenderResults;
    } // namespace hydra
} // namespace usd

namespace graph
{
namespace exec
{
    namespace unstable
    {
        class ExecutionPath;
    } // namespace unstable
} // namespace exec

namespace image
{
namespace core
{
namespace unstable
{
//! Declare the IPostRenderGraph interface definition
OMNI_DECLARE_INTERFACE(IPostRenderGraph);

//! The main interface for updating the post-render graph node of the execution graph.
class IPostRenderGraph_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.image.core.unstable.IPostRenderGraph")>
{
protected:

    //! @brief Update the post render graphs.
    //! @param controller The execution controller.
    //! @param execPath The execution path of the execution graph node which represents the post render graph.
    //! @param renderGraph The render graph on which the post process nodes will be executed.
    //! @param renderResults The render products from the rendering frame which is being post processed.
    //! @param renderProductPrimPaths The paths of the render products on the stage.
    //! @param renderProductCount The number of render product results.
    //! @param stageId The ID of the rendered stage.
    //! @param simTime The simulation time.
    //! @param hydraTime The rendering time.
    //! @return Returns a return code with information about the success or failure of the operation.
    virtual OMNI_ATTR("no_py") gpu::GfResult
        update_abi(OMNI_ATTR("not_null, no_acquire") omni::kit::exec::core::unstable::IExecutionController* controller,
                   OMNI_ATTR("not_null, in") omni::graph::exec::unstable::ExecutionPath const* execPath,
                   OMNI_ATTR("not_null, out") gpu::rendergraph::IRenderGraph* renderGraph,
                   omni::usd::hydra::ViewportHydraRenderResults* renderResults,
                   OMNI_ATTR("not_null, in") omni::usd::PathH const* renderProductPrimPaths,
                   size_t renderProductCount,
                   uint64_t stageId,
                   double simTime,
                   double hydraTime) noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace image
} // namespace graph
} // namespace omni

// generated API declaration
#include "IPostRenderGraph.gen.h"
