// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file NodeDef.h
//!
//! @brief Declares @ref omni::graph::core::unstable::IGenericNodeGraphDef.
#pragma once

#include <carb/profiler/Profile.h>

#include <omni/String.h>
#include <omni/graph/core/IInternal.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/unstable/IGenericNodeGraphDef.h>
#include <omni/graph/exec/unstable/GraphBuilder.h>
#include <omni/graph/exec/unstable/NodeGraphDef.h>
#include <omni/inspect/IInspectJsonSerializer.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::IGenericNodeGraphDef
template <typename... Bases>
class GenericNodeGraphDefT : public exec::unstable::NodeGraphDefT<Bases..., exec::unstable::INodeGraphDefDebug>
{
public:
    //! Construct generic OmniGraph definition.
    //!
    //! This class is a base class for all OmniGraph node graph definitions and will use provided executor.
    //!
    //! @param  builder  Builder constructing the graph
    //! @param  executorFactory  Executor factory to use for this instance of the graph
    //! @param  definitionName  Definition name is considered as a token that transformation passes can register against
    //! @param  graphObj  Authoring graph associated with this definition
    //! @param  isInstanced  Is this an instanced OmniGraph
    //!
    //! A valid pointer is always returned.
    static omni::core::ObjectPtr<GenericNodeGraphDefT> create(omni::core::ObjectParam<exec::unstable::IGraphBuilder> builder,
                                                              exec::unstable::ExecutorFactory executorFactory,
                                                              const carb::cpp::string_view& definitionName,
                                                              const GraphObj& graphObj,
                                                              bool isInstanced) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(builder);
        OMNI_GRAPH_EXEC_ASSERT(definitionName.data());
        auto def =  omni::core::steal(new GenericNodeGraphDefT(builder->getGraph(), std::move(executorFactory), definitionName, graphObj, isInstanced));
        def->build(builder);
        return def;
    }

    exec::unstable::IGraphBuilder* build_abi(exec::unstable::IGraphBuilder* parentBuilder) noexcept override
    {
        auto builder = exec::unstable::GraphBuilder::create(parentBuilder, this);

        // make sure the topology of the graph is valid...this may not be the case if graph is empty
        // because if happens lazily when requesting root node
        this->getRoot()->validateOrResetTopology();

        // attach to authoring graph
        m_privateDef->attachToAuthoring(this);

        return builder.detach();
    }

    bool inspect_abi(inspect::IInspector* inspector) noexcept override
    {
        return true;
    }

    static omni::string getDefinitionName(const GraphObj& graphObj) noexcept
    {
        static const omni::string sDefNamePrefix = "og.def.graph_";

        return sDefNamePrefix + graphObj.iGraph->getEvaluatorName(graphObj);
    }

protected:
    using BaseType = exec::unstable::NodeGraphDefT<Bases..., exec::unstable::INodeGraphDefDebug>;

    GraphObj getAuthoringGraph_abi() noexcept override
    {
        return m_privateDef->getAuthoringGraph();
    }

    bool isInstanced_abi() noexcept override
    {
        return m_privateDef->isInstanced();
    }

    exec::unstable::INode* getExecutionNode_abi(const NodeObj* nodeObj) noexcept override
    {
        return nullptr;
    }

    exec::unstable::Status preExecute_abi(exec::unstable::ExecutionTask* info) noexcept override
    {
        return m_privateDef->preExecute(*info);
    }

    exec::unstable::Status postExecute_abi(exec::unstable::ExecutionTask* info) noexcept override
    {
        return m_privateDef->postExecute(*info);
    }

    void getInstanceInfo_abi(omni::graph::exec::unstable::ExecutionTask const* info, InstanceIndex* retBaseInstanceIndex, size_t* retNumberOfInstances) noexcept override
    {
        m_privateDef->getInstanceInfo(*info, *retBaseInstanceIndex, *retNumberOfInstances);
    }

    GenericNodeGraphDefT(exec::unstable::IGraph* graph,
                         exec::unstable::ExecutorFactory&& executorFactory,
                         const carb::cpp::string_view& definitionName,
                         const GraphObj& graphObj,
                         bool isInstanced) noexcept
        : BaseType(graph, std::move(executorFactory), definitionName) // may throw
          ,
          m_privateDef(
              carb::getCachedInterface<omni::graph::core::IInternal>()->createPrivateGraphDef(graphObj, isInstanced),
              omni::core::kSteal)
    {
    }

private:
    omni::core::ObjectPtr<IPrivateNodeGraphDef> m_privateDef; //!< Internal object, hiding implementation details
                                                              //!< relying on OG internals
};

//! @copydoc omni::graph::exec::unstable::IGenericNodeGraphDef
using GenericNodeGraphDef = GenericNodeGraphDefT<IGenericNodeGraphDef>;

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni
