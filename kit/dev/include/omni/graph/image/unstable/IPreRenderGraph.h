// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IPreRenderGraph.h
//!
//! @brief Defines @ref omni::graph::image::core::unstable::IPreRenderGraph_abi
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
}
enum class GfResult: int32_t;
}

namespace omni
{
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
//! Declare the IPreRenderGraph interface definition
OMNI_DECLARE_INTERFACE(IPreRenderGraph);

//! Interface for updating pre-render graphs.
class IPreRenderGraph_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.image.core.unstable.IPreRenderGraph")>
{
protected:
    //! @brief Updates the pre-render graphs.
    //! @param controller The execution controller.
    //! @param execPath The execution path of the execution graph node which represents the pre render graph.
    //! @param renderGraph The render graph on which the pre-render processing tasks are registered.
    //! @param simTime The simulation time.
    //! @param hydraTime The render time.
    //! @return Returns a success code.
    virtual OMNI_ATTR("no_py") gpu::GfResult
        update_abi(OMNI_ATTR("not_null, no_acquire") omni::kit::exec::core::unstable::IExecutionController* controller,
                   OMNI_ATTR("in") omni::graph::exec::unstable::ExecutionPath const* execPath,
                   OMNI_ATTR("out") gpu::rendergraph::IRenderGraph* renderGraph,
                   double simTime,
                   double hydraTime) noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace image
} // namespace graph
} // namespace omni

// generated API declaration
#include "IPreRenderGraph.gen.h"
