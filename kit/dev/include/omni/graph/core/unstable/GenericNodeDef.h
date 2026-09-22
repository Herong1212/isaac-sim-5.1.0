// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file NodeDef.h
//!
//! @brief Declares @ref omni::graph::core::unstable::IGenericNodeDef.
#pragma once

#include <carb/profiler/Profile.h>

#include <omni/graph/core/IInternal.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/unstable/IGenericNodeDef.h>
#include <omni/graph/exec/unstable/ExecutionTask.h>
#include <omni/graph/exec/unstable/NodeDef.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

//! @copydoc omni::graph::core::unstable::IGenericNodeDef
template <typename... Bases>
class GenericNodeDefT : public exec::unstable::NodeDefT<Bases...>
{
public:
    //! Construct OmniGraph node definition which will use call ogn compute method to execute the node
    //!
    //! @param  definitionName  Definition name is considered as a token that transformation passes can register
    //!                         against.  Must not be @c nullptr.
    //! @param  nodeObj  Authoring node associated with this definition instance
    //! @param  segStart The first instance index at which the def refers to (segment start)
    //! @param  segLen   The number of instances in the segment(segment length)
    static omni::core::ObjectPtr<GenericNodeDefT> create(const carb::cpp::string_view& definitionName,
                                                         const NodeObj& nodeObj,
                                                         InstanceIndex segStart = { kInvalidVal },
                                                         size_t segLen = kInvalidVal) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(definitionName.data());
        return omni::core::steal(new GenericNodeDefT(definitionName, nodeObj, segStart, segLen));
    }

    //! Determine scheduling constraint based on the OmniGraph node object
    static exec::unstable::SchedulingInfo getSchedulingInfo(const NodeObj& nodeObj) noexcept
    {
        auto schedulingInfo = exec::unstable::SchedulingInfo::eSerial;

        NodeTypeObj nodeTypeObj = nodeObj.iNode->getNodeTypeObj(nodeObj);
        if (!nodeTypeObj.isValid())
        {
            return schedulingInfo;
        }
        ISchedulingHints* const schedulingHints = nodeTypeObj.iNodeType->getSchedulingHints(nodeTypeObj);
        ISchedulingHints2* const schedulingHints2 = omni::core::cast<ISchedulingHints2>(schedulingHints).get();
        if (schedulingHints)
        {
            if (schedulingHints->getThreadSafety() == eThreadSafety::eSafe ||
                (schedulingHints2 && schedulingHints2->getPurityStatus() == ePurityStatus::ePure))
            {
                // schedulingHints()->getDataAccess(eAccessLocation::eUsd) == eAccessType::eRead
                // depending on situation, above can be scheduled in parallel. In general it is safer
                // to assume serial, since USD composition engine is not thread safe...but once the stage
                // is composed, pulling out individual attribute values is safe.
                // Currently we will hurt performance for nodes like OgnReadPrimAttribute and make
                // our mainline branch be slower than prototype. We will explore runtime override
                // to scheduling hints that would allow changing the dispatch based on runtime information.

                // Also note that with the current ordering of the if-else statements, a node
                // can technically be both threadsafe AND write to usd, if the node's compute
                // implementation allows for it (e.g. with a delay write to USD that leverages
                // the OG "registerForUSDWriteBack").
                schedulingInfo = exec::unstable::SchedulingInfo::eParallel;
            }
            else if (schedulingHints->getDataAccess(eAccessLocation::eUsd) == eAccessType::eWrite)
            {
                schedulingInfo = exec::unstable::SchedulingInfo::eIsolate;
            }
        }

        return schedulingInfo;
    }

protected:
    using BaseType = exec::unstable::NodeDefT<Bases...>;

    exec::unstable::Status execute_abi(exec::unstable::ExecutionTask* info) noexcept override
    {
        auto scope = std::unique_ptr<ICudaDeviceScopeGuard>{ m_privateDef->enforceCudaDevice() };
        return executeImpl(info);        
    }

    virtual exec::unstable::Status executeImpl(exec::unstable::ExecutionTask* info) noexcept
    {
        exec::unstable::ExecutionTask* currentTask = exec::unstable::getCurrentTask();
        if (!m_nodeObj.iNode->isDisabled(m_nodeObj) && currentTask)
        {
            InstanceIndex baseInstanceIndex{ 0 };
            size_t numberOfInstances{ 1 };

            m_privateDef->getInstanceInfo(*info, baseInstanceIndex, numberOfInstances);

            CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "NodeCompute");
            if (m_nodeTypeObj.iNodeType->computeVectorized)
            {
                currentTask->setUserIndex(baseInstanceIndex.index);
                m_nodeTypeObj.iNodeType->computeVectorized(m_contextObj, m_nodeObj, numberOfInstances);
            }
            else
            {
                if (m_nodeTypeObj.iNodeType->compute == nullptr)
                {
                    // this can happen if a node is provided by an extension and the user unloads the extension or
                    // manually deregisters the node type.
                    CARB_LOG_WARN_ONCE("Node implementation lost, aborting graph execution");
                }
                else
                {
                    InstanceIndex currentInstance = baseInstanceIndex;
                    for (size_t i = 0; i < numberOfInstances; ++i)
                    {
                        currentTask->setUserIndex(currentInstance.index);
                        m_nodeTypeObj.iNodeType->compute(m_contextObj, m_nodeObj);

                        ++currentInstance;
                    }
                }
            }
        }
        return exec::unstable::Status::eSuccess;
    }

    exec::unstable::SchedulingInfo getSchedulingInfo_abi(const exec::unstable::ExecutionTask* info) noexcept override
    {
        return m_schedulingInfo;
    }

    NodeObj getAuthoringNode_abi() noexcept override
    {
        return m_nodeObj;
    }

    GenericNodeDefT(const carb::cpp::string_view& definitionName,
                    const NodeObj& nodeObj,
                    InstanceIndex segStart = { kInvalidVal },
                    size_t segLen = { kInvalidVal }) noexcept
        : BaseType(definitionName),
          m_nodeObj{ nodeObj },
          m_schedulingInfo(getSchedulingInfo(nodeObj)),
          m_privateDef(carb::getCachedInterface<omni::graph::core::IInternal>()->createPrivateNodeDefWithSegInfo(
                           nodeObj, segStart, segLen),
                       omni::core::kSteal)

    {
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
        m_contextObj = graphObj.iGraph->getDefaultGraphContext(graphObj);
        m_nodeTypeObj = nodeObj.iNode->getNodeTypeObj(nodeObj);
    }

protected:
    static constexpr size_t kInvalidVal{ size_t(-1) };

    NodeObj m_nodeObj; //!< Authoring node this instance is defining for execution
    GraphContextObj m_contextObj; //!< Authoring graph context stored for speed of execution
    NodeTypeObj m_nodeTypeObj; //!< Authoring node type information stored for speed of execution
    exec::unstable::SchedulingInfo m_schedulingInfo; //!< Scheduling constraint

    omni::core::ObjectPtr<IPrivateNodeDef> m_privateDef; //!< Internal object, hiding implementation details
                                                         //!< relying on OG internals
};

//! @copydoc omni::graph::exec::unstable::IGenericNodeDef
using GenericNodeDef = GenericNodeDefT<IGenericNodeDef>;

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni
