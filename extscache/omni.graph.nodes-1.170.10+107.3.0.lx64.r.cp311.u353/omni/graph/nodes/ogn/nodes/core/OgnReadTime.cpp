// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnReadTimeDatabase.h>

#include <omni/fabric/IToken.h>
#include <omni/graph/core/Handle.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/unstable/Dirtyable.h>
#include <omni/kit/exec/core/unstable/IExecutionContext.h>
#include <omni/kit/IStageUpdate.h>

#include <tbb/concurrent_unordered_map.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{
namespace
{
// This node type implements the IDirtyable ONI.
class DirtyableImpl : public Dirtyable
{
public:
    DirtyableImpl(const char* const nodeTypeName) noexcept : Dirtyable(nodeTypeName)
    {
    }

private:
    const bool isNodeDirty(const NodeObj& nodeObj,
                           kit::exec::core::unstable::IExecutionContext* const executionContext,
                           InstanceIndex instanceIndex) noexcept override
    {
        // This node type should always be ticking/dirtied since the measured global time progression since application
        // startup never pauses.
        return true;
    }

    const bool isComputeRequestPropagator(const AttributeObj& outputAttributeObj,
                                          kit::exec::core::unstable::IExecutionContext* const executionContext,
                                          InstanceIndex instanceIndex) noexcept override
    {
        const NameToken& outputAttributeNameToken = outputAttributeObj.iAttribute->getNameToken(outputAttributeObj);
        if (outputAttributeNameToken == outputs::absoluteSimTime.m_token ||
            outputAttributeNameToken == outputs::deltaSeconds.m_token ||
            outputAttributeNameToken == outputs::timeSinceStart.m_token)
        {
            // Playback-independent parameters are always changing, so they should always dirty their downstreams when
            // the ReadTime node is dirtied (which happens on every execution tick), even if they're not currently
            // connected to anything.
            return true;
        }
        else if (outputAttributeNameToken == outputs::frame.m_token || outputAttributeNameToken == outputs::time.m_token)
        {
            // Playback-dependent parameters only dirty their downstreams when (a) the ReadTime node is dirtied (which
            // happens on every execution tick), and (b) when animation time is changing (which is when these specific
            // output parameters will also change).
            return executionContext->getTime()->timeChanged;
        }
        else if (outputAttributeNameToken == outputs::isPlaying.m_token)
        {
            // All other parameters only dirty their downstreams when (a) the ReadTime node is dirtied (which happens
            // on every execution tick), and (b) when the specific parameter itself has changed relative to the
            // previous execution.
            const NodeObj& nodeObj = outputAttributeObj.iAttribute->getNode(outputAttributeObj);
            const uint64_t graphInstanceId =
                nodeObj.iNode->getGraphInstanceID(nodeObj.nodeHandle, instanceIndex).id.token;
            const auto& it = m_prevIsPlaying.find(outputAttributeObj.attributeHandle);
            if (it == m_prevIsPlaying.end())
            {
                m_prevIsPlaying.emplace(
                    outputAttributeObj.attributeHandle, tbb::concurrent_unordered_map<uint64_t, bool>());
                m_prevIsPlaying.at(outputAttributeObj.attributeHandle)
                    .emplace(graphInstanceId, executionContext->getUpdateSettings()->isPlaying);
                return true;
            }
            else
            {
                const auto& it2 = it->second.find(graphInstanceId);
                if (it2 == it->second.end() || it2->second != executionContext->getUpdateSettings()->isPlaying)
                {
                    m_prevIsPlaying.at(outputAttributeObj.attributeHandle)[graphInstanceId] =
                        executionContext->getUpdateSettings()->isPlaying;
                    return true;
                }
            }
        }

        return false;
    }

    void clearSharedState(const NodeObj& nodeObj) noexcept override
    {
        const AttributeObj& outputAttributeObj = nodeObj.iNode->getAttribute(nodeObj, outputs::isPlaying.m_name);
        (void)m_prevIsPlaying.unsafe_erase(outputAttributeObj.attributeHandle);
    }

    void clearPerInstanceState(const NodeObj& nodeObj, const GraphInstanceID& graphInstanceId) noexcept override
    {
        const AttributeObj& outputAttributeObj = nodeObj.iNode->getAttribute(nodeObj, outputs::isPlaying.m_name);
        if (m_prevIsPlaying.find(outputAttributeObj.attributeHandle) != m_prevIsPlaying.end())
        {
            (void)m_prevIsPlaying.at(outputAttributeObj.attributeHandle).unsafe_erase(graphInstanceId.id.token);
        }
    }

private:
    // Per-node, per-instance cache for the isPlaying attribute's previous value.
    tbb::concurrent_unordered_map<AttributeHandle, tbb::concurrent_unordered_map<uint64_t, bool>> m_prevIsPlaying;
};

REGISTER_OGN_NODE_INTERFACE(DirtyableImpl, "omni.graph.nodes.ReadTime") // May throw.

} // anonymous namespace
} // namespace unstable
} // namespace core

namespace nodes
{

class OgnReadTime
{
public:
    static size_t computeVectorized(OgnReadTimeDatabase& db, size_t count)
    {
        const auto& contextObj = db.abi_context();
        const IGraphContext* const iContext = contextObj.iContext;

        auto deltaSeconds = db.outputs.deltaSeconds.vectorized(count);
        auto isPlaying = db.outputs.isPlaying.vectorized(count);
        auto time = db.outputs.time.vectorized(count);
        auto frame = db.outputs.frame.vectorized(count);
        auto timeSinceStart = db.outputs.timeSinceStart.vectorized(count);
        auto absoluteSimTime = db.outputs.absoluteSimTime.vectorized(count);

        auto getElapsedTime = iContext->getElapsedTime(contextObj);
        auto getIsPlaying = iContext->getIsPlaying(contextObj);
        auto getTime = iContext->getTime(contextObj);
        auto getFrame = iContext->getFrame(contextObj);
        auto getTimeSinceStart = iContext->getTimeSinceStart(contextObj);
        auto getAbsoluteSimTime = iContext->getAbsoluteSimTime(contextObj);

        std::fill(deltaSeconds.begin(), deltaSeconds.end(), getElapsedTime);
        std::fill(isPlaying.begin(), isPlaying.end(), getIsPlaying);
        std::fill(time.begin(), time.end(), getTime);
        std::fill(frame.begin(), frame.end(), getFrame);
        std::fill(timeSinceStart.begin(), timeSinceStart.end(), getTimeSinceStart);
        std::fill(absoluteSimTime.begin(), absoluteSimTime.end(), getAbsoluteSimTime);

        return count;
    }
};

REGISTER_OGN_NODE()
} // nodes
} // graph
} // omni
