// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/iComputeGraph.h>

#include <tbb/concurrent_hash_map.h>

#include <memory>

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    StateManager  Class that automatically manages per-node state data
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// ======================================================================
/**
 * This class structure provides support for internal state data. The reason for such a tricky implementation is to
 * make it easier to access from the node implementation code. At compute time only the database is accessible, so
 * the state information is best retrieved from there. At the same time the minimal amount of effort required to set
 * up state information is to put it in the node implementation class, so the database needs to know how the class is
 * structured and the class needs to know how the database is structured, leading to a recursive inclusion, not handled
 * well by C++.
 * 
 * Instead of this a templated state manager is instantiated by the .ogn generation code that lives as a static member
 * of the generated database class. The template parameters hide the fact that the state exists in the not-yet-defined
 * node implementation class, at the cost of requiring the class be mentioned when retrieving the state information.
 * 
 * Inside the node's compute method the state information is retrieved as:
 *      auto& state = db.internalState<OgnMyNode>();
 */
struct StateManager
{
    // As the map from NodeHandle to the state information cannot know the template type (not yet defined as per the
    // above explanation) this base class is set up as a basic form of type hiding. This way the map can hold
    // references to the heterogeneous set of templated state information. This is safe because every NodeHandle will
    // uniquely reference a different type of state class, and the virtual base class hides that fact from the
    // non-templated part of this manager.
    struct StateHolderBase
    {
        virtual ~StateHolderBase() {}
    };

    // The templated holder class provides access to the underlying state information.
    template <typename StateInformationClass>
    struct StateHolder : StateHolderBase
    {
        std::unique_ptr<StateInformationClass> m_stateObject;
        StateHolder() : m_stateObject{ std::make_unique<StateInformationClass>() } {}
        StateInformationClass& value() { return *m_stateObject; }
    };

    using Key = std::pair<NodeHandle, size_t>;//pair of the node and the graph instance ID (ie. represent a unique node in a unique graph instance)
    using ConcurrentHashMap = tbb::concurrent_hash_map<Key, std::unique_ptr<StateHolderBase>>;
    using WriteAccessor = typename ConcurrentHashMap::accessor;

    // This method provides access to the internal state through the instance Id
    template <typename StateInformationClass>
    StateInformationClass& getState(NodeHandle value, GraphInstanceID instanceId)
    {
        // It would have been better to avoid having a state manager at all when no state exists but a simple method
        // of doing so was not found. This approach looked promising but suffered from the same circular dependency
        // that mandated the current approach: https://stackoverflow.com/questions/25492589/
        // Here we at least let the node writer know that they need to add state for this call to make sense.
        static_assert(!std::is_empty<StateInformationClass>::value, "State class is empty");

        Key k{ value, instanceId.id.token };

        WriteAccessor writeIt;
        if (!m_managedState.find(writeIt, k))
        {
            m_managedState.emplace(writeIt, k, std::make_unique<StateHolder<StateInformationClass>>());
        }
        // This is the magic that lets a generic map correctly handle members of templated types. We've
        // constructed the class to guarantee that a reinterpret_cast will work, avoiding the more expensive
        // dynamic_cast, and since this method is templated the exact type for casting is known.
        return (reinterpret_cast<StateHolder<StateInformationClass>*>(writeIt->second.get()))->value();
    }

    // This method provides access to the internal state through the instance index
    template <typename StateInformationClass>
    StateInformationClass& getState(NodeHandle value, InstanceIndex idx = kAccordingToContextIndex)
    {
        return getState<StateInformationClass>(value, carb::getCachedInterface<INode>()->getGraphInstanceID(value, idx));
    }

    // As the lifespan of node handles is limited they must remove themselves from the state map when they are
    // released. Note that this is required due to the fact that the node implementation classes are not
    // themselves instantiated, except for this state management. The NodeHandle refers to a unique instantiation
    // of a node of a particular type in a unique OmniGraph evaluation context.
    //
    // This method does not need to be templated because the underlying StateHolder knows how to destroy its type.
    void removeState(NodeHandle value, GraphInstanceID instanceID)
    {
        Key k{ value, instanceID.id.token };
        m_managedState.erase(k);
    }

    // Quick lookup of state information associated with a node, using the base class type to mask the templated
    // type that lies beneath. Using a unique_ptr ensures it is properly destroyed when the node is released.
    ConcurrentHashMap m_managedState;
};

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
