// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file GraphBuilderContext.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraphBuilderContext.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/IGraphBuilderContext.h>
#include <omni/graph/exec/unstable/IPassPipeline.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::IGraphBuilderContext
template <typename... Bases>
class GraphBuilderContextT : public Implements<Bases...>
{
public:
    //! Construct graph builder context for a given @ref IGraph with a given pass transformation pipeline.
    //!
    //! @p graph must not be @c nullptr.
    //!
    //! @p passPipeline must not be @c nullptr.
    //!
    //! The returned pointer is always valid.
    static omni::core::ObjectPtr<GraphBuilderContextT> create(omni::core::ObjectParam<IGraph> graph,
                                                              omni::core::ObjectParam<IPassPipeline> passPipeline) noexcept
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(graph);
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(passPipeline);
        return omni::core::steal(new GraphBuilderContextT(graph.get(), passPipeline.get()));
    }

protected:
    //! @copydoc omni::graph::exec::unstable::IGraphBuilderContext::getConstructionStamp_abi
    Stamp getConstructionStamp_abi() noexcept override
    {
        return m_constructionStamp;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderContext::getGraph_abi
    IGraph* getGraph_abi() noexcept override
    {
        return m_owner;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderContext::runTransformations_abi
    void runTransformations_abi(INodeGraphDef* nodeGraphDef) noexcept override
    {
        m_pipeline->run(this, nodeGraphDef);
        m_constructionStamp.next();
    }

    //! Constructor.
    GraphBuilderContextT(IGraph* graph, IPassPipeline* pipeline)
        : m_owner{ graph }, m_pipeline{ pipeline, omni::core::kBorrow }
    {
    }

private:
    IGraph* m_owner; //!< Owner of all graphs this context touches
    PassPipelinePtr m_pipeline; //!< Graph transformations pipeline used in this context
    Stamp m_constructionStamp; //!< Construction version incremented after pipeline run.
};

//! Core GraphBuilderContext implementation for @ref omni::graph::exec::unstable::IGraphBuilderContext
using GraphBuilderContext = GraphBuilderContextT<IGraphBuilderContext>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
